import json
import logging
from typing import Any

from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def parse_json_response(content: str) -> dict[str, Any]:
	"""
	Parse JSON da resposta do LLM, removendo code fences se necessário.
	"""
	content = (content or "").strip()
	if content.startswith("```"):
		content = content.strip("`")
		if content.lower().startswith("json"):
			content = content[4:]
		content = content.strip()

	try:
		return json.loads(content)
	except json.JSONDecodeError:
		start = content.find("{")
		end = content.rfind("}")
		if start != -1 and end != -1:
			try:
				return json.loads(content[start: end + 1])
			except json.JSONDecodeError:
				pass
		logger.error("Resposta LLM não é JSON válido: %s", content[:500])
		raise


def format_job_data(job) -> dict[str, Any]:
	"""Extrai dados formatados do Job para passar ao prompt de análise."""
	return {
		"job_title": job.title,
		"job_seniority": job.get_seniority_display(),
		"work_model": job.get_work_model_display(),
		"location": job.location or "Não especificada",
		"contract_type": job.get_contract_type_display(),
		"min_experience_years": job.min_experience_years,
		"languages": job.languages or "Não especificado",
		"education_level": job.get_education_level_display(),
		"required_skills": job.required_skills or "(não informado)",
		"nice_to_have": job.nice_to_have or "(não informado)",
		"job_description": strip_tags(job.description or ""),
	}


def format_context(chunks: list[str]) -> str:
	"""
	Formata os chunks do RAG em um contexto legível para o LLM.
	Junta os trechos recuperados do currículo com separadores visuais
	para facilitar a leitura pelo LLM.
	"""
	return "\n\n---\n\n".join(chunks) if chunks else "(sem contexto)"


def build_job_query(job) -> str:
	"""Constrói query para busca semântica no RAG.	"""
	description = strip_tags(job.description or "")
	return (
		f"{job.title}\nSenioridade: {job.get_seniority_display()}\n"
		f"Skills obrigatórias: {job.required_skills}\n"
		f"Desejáveis: {job.nice_to_have}\n\n{description}"
	)
