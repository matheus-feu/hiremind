import logging

from django.db import transaction

from .chains import create_analysis_chain, invoke_chain
from .extraction import ExtractionError, TextExtractorService
from .llm import get_default_provider
from .parsers import build_job_query, format_context, format_job_data
from .vector_store import get_default_vector_store
from ..models import Analysis, Job, Resume

logger = logging.getLogger(__name__)

class ResumeAnalysisService:
	"""Orquestrador de análise de currículos."""
	def __init__(self, rag_k: int = 6) -> None:
		self.extractor = TextExtractorService()
		self.vector_store = get_default_vector_store()
		self.provider = get_default_provider()
		self.rag_k = rag_k
		self._analysis_chain = None

	def extract_and_persist_text(self, resume: Resume) -> str:
		text = self.extractor.extract_from_uploaded(resume.file)
		text = (text or '').strip()
		if len(text) < 50:
			raise ExtractionError('Texto extraído muito curto')

		resume.raw_text = text
		resume.save(update_fields=['raw_text', 'updated_at'])
		logger.info(f'Texto extraído e salvo para Resume {resume.id} (length={len(text)})')
		return text

	def index_resume(self, resume: Resume) -> int:
		chunks_count = self.vector_store.index_resume(
			resume_id=str(resume.id),
			text=resume.raw_text or '',
			metadata={
				'candidate_name': resume.candidate_name or '',
				'candidate_email': resume.candidate_email or ''
			},
		)
		logger.info(f'Resume indexado em RAG: {chunks_count} chunks para Resume {resume.id}')
		return chunks_count

	def retrieve_context(self, job: Job, resume_id: str) -> list[str]:
		job_query = build_job_query(job)
		chunks = self.vector_store.retrieve_for_job(job_text=job_query, resume_id=resume_id, k=self.rag_k)
		logger.info(f'RAG recuperou {len(chunks)} chunks para Job {job.id} e Resume {resume_id}')
		return chunks

	def _get_analysis_chain(self):
		if self._analysis_chain is None:
			self._analysis_chain = create_analysis_chain(self.provider)
			logger.debug('Chain criada')
		return self._analysis_chain

	def invoke_llm_analysis(self, job: Job, context_chunks: list[str]) -> dict:
		chain_input = {**format_job_data(job), 'context': format_context(context_chunks), 'k': len(context_chunks)}
		chain = self._get_analysis_chain()
		result = invoke_chain(chain, chain_input)
		logger.info(f'LLM retornou resultado da análise para Job {job.id} (score={result.get("score", 0)})')
		return result

	def persist_analysis(self, resume: Resume, job: Job, llm_data: dict) -> Analysis:
		if not resume.candidate_name and llm_data.get('candidate_name'):
			resume.candidate_name = str(llm_data['candidate_name'])[:200]
			resume.save(update_fields=['candidate_name', 'updated_at'])

		analysis, created = Analysis.objects.update_or_create(
			resume=resume, job=job,
			defaults={
				'seniority': str(llm_data.get('seniority', ''))[:50],
				'years_experience': float(llm_data.get('years_experience') or 0),
				'skills': llm_data.get('skills') or [],
				'matched_skills': llm_data.get('matched_skills') or [],
				'missing_skills': llm_data.get('missing_skills') or [],
				'summary': llm_data.get('summary') or '',
				'score': float(llm_data.get('score') or 0),
				'strengths': llm_data.get('strengths') or [],
				'weaknesses': llm_data.get('weaknesses') or [],
				'interview_questions': llm_data.get('interview_questions') or [],
				'raw_response': llm_data,
			},
		)
		logger.info(
			f'Analysis {"criada" if created else "atualizada"} para Resume {resume.id} e Job {job.id} (score={analysis.score})')
		return analysis

	@transaction.atomic
	def analyze(self, resume: Resume, job: Job) -> Analysis:
		try:
			resume.mark_processing()
			logger.info(f'Iniciando análise para Resume {resume.id} e Job {job.id}')
			self.extract_and_persist_text(resume)
			self.index_resume(resume)
			chunks = self.retrieve_context(job, str(resume.id))
			llm_data = self.invoke_llm_analysis(job, chunks)
			analysis = self.persist_analysis(resume, job, llm_data)
			resume.mark_done()
			logger.info(f'✅ Análise concluída para Resume {resume.id} e Job {job.id} (score={analysis.score})')
			return analysis
		except Exception as exc:
			logger.exception(f'❌ Falha analisando Resume {resume.id} para Job {job.id}')
			resume.mark_error(str(exc))
			raise