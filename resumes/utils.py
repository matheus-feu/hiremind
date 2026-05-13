import logging

from django.contrib import messages
from django.utils.translation import gettext as _

from .models import Job, Resume
from .services import ResumeAnalysisService
from .services.extraction import ExtractionError
from .services.llm import LLMConfigurationError

logger = logging.getLogger(__name__)


def run_analysis(request, resume: Resume, job: Job) -> None:
	"""Roda o pipeline de análise e adiciona uma mensagem na request."""
	try:
		ResumeAnalysisService().analyze(resume, job)
		messages.success(
			request,
			_("Currículo analisado contra '%(title)s'.") % {"title": job.title},
		)
	except LLMConfigurationError as exc:
		messages.error(request, _("OpenAI não configurada: %(err)s") % {"err": exc})
	except ExtractionError as exc:
		messages.error(request, _("Não foi possível ler o arquivo: %(err)s") % {"err": exc})
	except Exception as exc:
		logger.exception("Falha analisando resume %s", resume.id)
		messages.warning(request, _("Análise falhou: %(err)s") % {"err": exc})
