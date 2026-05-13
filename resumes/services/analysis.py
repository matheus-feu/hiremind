import json
import logging
from typing import Any

from django.db import transaction
from django.utils.html import strip_tags

from .extraction import ExtractionError, TextExtractorService
from .llm import get_default_provider
from .vector_store import get_default_vector_store
from ..models import Analysis, Job, Resume

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista sênior em recrutamento técnico (TechRecruiter).
Sua tarefa: analisar trechos de um currículo (recuperados via RAG) e compará-los com uma vaga.

Responda SEMPRE em JSON válido com EXATAMENTE este schema (sem texto fora do JSON):
{
  "candidate_name": "string (extraia do currículo se possível, senão vazio)",
  "seniority": "apprentice | intern | trainee | junior | mid_level | senior | specialist | staff | principal | tech_lead | architect | coordinator | product_owner | manager | head | director | vp | c_level",
  "years_experience": number,
  "skills": ["lista de skills detectadas"],
  "matched_skills": ["skills do candidato que cobrem requisitos da vaga"],
  "missing_skills": ["skills da vaga que o candidato NÃO demonstra"],
  "strengths": ["3 a 5 pontos fortes objetivos"],
  "weaknesses": ["até 5 lacunas/pontos de atenção"],
  "summary": "resumo profissional do candidato em 4 a 6 frases, em português",
  "score": number (0 a 100, aderência à vaga, considere skills, experiência, senioridade, modalidade, idiomas e requisitos),
  "interview_questions": [
     {"question": "pergunta técnica em português", "topic": "tema", "difficulty": "easy|medium|hard"}
  ]
}

Regras:
- Use APENAS as informações dos trechos do currículo. Se algo não aparece, considere ausente.
- Ajuste o score considerando: modalidade de trabalho, localização, tipo de contrato, anos de experiência mínimos, idiomas obrigatórios, escolaridade.
- Se candidato não atende requisito crítico (ex: vaga remoto mas CV só presencial, ou falta inglês obrigatório), penalize o score.
- Gere de 5 a 8 perguntas de entrevista relevantes, calibradas pela senioridade detectada e pelos gaps.
- Não inclua comentários, markdown, ou texto fora do JSON.
"""

USER_PROMPT_TEMPLATE = """### VAGA
Título: {job_title}
Senioridade alvo: {job_seniority}
Skills obrigatórias: {required_skills}
Skills desejáveis: {nice_to_have}

Descrição:
{job_description}

### TRECHOS RELEVANTES DO CURRÍCULO (RAG, top-{k})
{context}

### INSTRUÇÃO
Gere o JSON conforme o schema do sistema."""


class ResumeAnalysisService:
	"""High-level orchestrator: extract → embed → RAG → LLM → persist."""

	def __init__(self, rag_k: int = 6) -> None:
		self.extractor = TextExtractorService()
		self.vector_store = get_default_vector_store()
		self.provider = get_default_provider()
		self.rag_k = rag_k

	def extract_and_persist_text(self, resume: Resume) -> str:
		text = self.extractor.extract_from_uploaded(resume.file)
		text = (text or "").strip()
		if len(text) < 50:
			raise ExtractionError(
				"Texto extraído muito curto/vazio — o arquivo pode ser uma "
				"imagem escaneada (precisa OCR) ou estar corrompido."
			)
		resume.raw_text = text
		resume.save(update_fields=["raw_text", "updated_at"])
		return text

	def index_resume(self, resume: Resume) -> int:
		return self.vector_store.index_resume(
			resume_id=str(resume.id),
			text=resume.raw_text or "",
			metadata={
				"candidate_name": resume.candidate_name or "",
				"candidate_email": resume.candidate_email or "",
			},
		)

	def _build_job_query(self, job: Job) -> str:
		description = strip_tags(job.description or "")
		return (
			f"{job.title}\nSenioridade: {job.get_seniority_display()}\n"
			f"Skills obrigatórias: {job.required_skills}\n"
			f"Desejáveis: {job.nice_to_have}\n\n{description}"
		)

	def _invoke_llm(self, job: Job, context_chunks: list[str]) -> dict[str, Any]:
		from langchain_core.messages import HumanMessage, SystemMessage

		chat = self.provider.get_chat()
		try:
			chat = chat.bind(response_format={"type": "json_object"})
		except Exception:
			pass

		context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(sem contexto)"
		user = USER_PROMPT_TEMPLATE.format(
			job_title=job.title,
			job_seniority=job.get_seniority_display(),
			work_model=job.get_work_model_display(),
			location=job.location or "Não especificada",
			contract_type=job.get_contract_type_display(),
			min_experience_years=job.min_experience_years,
			languages=job.languages or "Não especificado",
			education_level=job.get_education_level_display(),
			required_skills=job.required_skills or "(não informado)",
			nice_to_have=job.nice_to_have or "(não informado)",
			job_description=strip_tags(job.description or ""),
			context=context,
			k=len(context_chunks),
		)
		messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user)]
		response = chat.invoke(messages)
		content = response.content if hasattr(response, "content") else str(response)
		return self._safe_json(content)

	@staticmethod
	def _safe_json(content: str) -> dict[str, Any]:
		content = (content or "").strip()
		if content.startswith("```"):
			# strip code fences
			content = content.strip("`")
			if content.lower().startswith("json"):
				content = content[4:]
			content = content.strip()
		try:
			return json.loads(content)
		except json.JSONDecodeError:
			# try to find first { ... } block
			start = content.find("{")
			end = content.rfind("}")
			if start != -1 and end != -1:
				try:
					return json.loads(content[start: end + 1])
				except json.JSONDecodeError:
					pass
			logger.error("Resposta LLM não é JSON válido: %s", content[:500])
			raise

	@transaction.atomic
	def analyze(self, resume: Resume, job: Job) -> Analysis:
		"""Run the full pipeline. Idempotent: updates existing Analysis."""
		try:
			resume.mark_processing()
			self.extract_and_persist_text(resume)
			self.index_resume(resume)

			chunks = self.vector_store.retrieve_for_job(
				job_text=self._build_job_query(job),
				resume_id=str(resume.id),
				k=self.rag_k,
			)
			data = self._invoke_llm(job, chunks)
			print(data)

			# update candidate name from LLM if missing
			if not resume.candidate_name and data.get("candidate_name"):
				resume.candidate_name = str(data["candidate_name"])[:200]
				resume.save(update_fields=["candidate_name", "updated_at"])

			analysis, _ = Analysis.objects.update_or_create(
				resume=resume,
				job=job,
				defaults={
					"seniority": str(data.get("seniority", ""))[:50],
					"years_experience": float(data.get("years_experience") or 0),
					"skills": data.get("skills") or [],
					"matched_skills": data.get("matched_skills") or [],
					"missing_skills": data.get("missing_skills") or [],
					"summary": data.get("summary") or "",
					"score": float(data.get("score") or 0),
					"strengths": data.get("strengths") or [],
					"weaknesses": data.get("weaknesses") or [],
					"interview_questions": data.get("interview_questions") or [],
					"raw_response": data,
				},
			)
			resume.mark_done()
			return analysis
		except Exception as exc:  # noqa: BLE001
			logger.exception("Falha analisando resume %s", resume.id)
			resume.mark_error(str(exc))
			raise
