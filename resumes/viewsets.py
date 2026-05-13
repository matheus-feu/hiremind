from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Analysis, Job, Resume
from .serializers import AnalysisSerializer, JobSerializer, ResumeSerializer
from .services import ResumeAnalysisService


@extend_schema_view(
	list=extend_schema(
		tags=["jobs"],
		summary="Listar todas as vagas",
		description="Retorna uma lista paginada de todas as vagas cadastradas no sistema.",
	),
	create=extend_schema(
		tags=["jobs"],
		summary="Criar nova vaga",
		description="Cria uma nova vaga no sistema.",
	),
	retrieve=extend_schema(
		tags=["jobs"],
		summary="Obter detalhes da vaga",
		description="Retorna os detalhes completos de uma vaga específica.",
	),
	update=extend_schema(
		tags=["jobs"],
		summary="Atualizar vaga",
		description="Atualiza todos os campos de uma vaga existente.",
	),
	partial_update=extend_schema(
		tags=["jobs"],
		summary="Atualizar vaga parcialmente",
		description="Atualiza apenas os campos fornecidos de uma vaga existente.",
	),
	destroy=extend_schema(
		tags=["jobs"],
		summary="Deletar vaga",
		description="Remove uma vaga do sistema.",
	),
)
class JobViewSet(viewsets.ModelViewSet):
	"""
	CRUD completo de vagas via API.

	Endpoints:
	- GET /api/jobs/ → lista todas as vagas
	- POST /api/jobs/ → cria nova vaga
	- GET /api/jobs/{id}/ → detalhe de uma vaga
	- PUT/PATCH /api/jobs/{id}/ → atualiza vaga
	- DELETE /api/jobs/{id}/ → remove vaga
	- GET /api/jobs/active/ → filtra apenas vagas ativas
	"""
	queryset = Job.objects.all()
	serializer_class = JobSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	filterset_fields = ["seniority", "work_model", "contract_type", "is_active", "education_level"]
	search_fields = ["title", "description", "required_skills", "location"]
	ordering_fields = ["created_at", "title", "min_experience_years"]
	ordering = ["-created_at"]

	@action(detail=False, methods=["get"])
	def active(self, request):
		"""Retorna apenas vagas ativas."""
		queryset = self.get_queryset().filter(is_active=True)
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)


@extend_schema_view(
	list=extend_schema(
		tags=["resumes"],
		summary="Listar todos os currículos",
		description="Retorna uma lista paginada de todos os currículos cadastrados no sistema.",
	),
	create=extend_schema(
		tags=["resumes"],
		summary="Upload de currículo",
		description="Faz upload de um novo currículo (PDF ou DOCX) para o sistema.",
	),
	retrieve=extend_schema(
		tags=["resumes"],
		summary="Obter detalhes do currículo",
		description="Retorna os detalhes completos de um currículo específico.",
	),
	update=extend_schema(
		tags=["resumes"],
		summary="Atualizar currículo",
		description="Atualiza todos os campos de um currículo existente.",
	),
	partial_update=extend_schema(
		tags=["resumes"],
		summary="Atualizar currículo parcialmente",
		description="Atualiza apenas os campos fornecidos de um currículo existente.",
	),
	destroy=extend_schema(
		tags=["resumes"],
		summary="Deletar currículo",
		description="Remove um currículo do sistema.",
	),
)
class ResumeViewSet(viewsets.ModelViewSet):
	"""
	CRUD de currículos via API.

	Endpoints:
	- GET /api/resumes/ → lista todos os currículos
	- POST /api/resumes/ → faz upload de currículo
	- GET /api/resumes/{id}/ → detalhe do currículo
	- DELETE /api/resumes/{id}/ → remove currículo
	- POST /api/resumes/{id}/analyze/ → analisa currículo com IA
	"""
	queryset = Resume.objects.select_related("job").all()
	serializer_class = ResumeSerializer
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
	filterset_fields = ["status", "job"]
	ordering_fields = ["created_at", "candidate_name"]
	ordering = ["-created_at"]

	@extend_schema(
		tags=["resumes"],
		summary="Analisar currículo",
		description="Executa análise de IA deste currículo para uma vaga específica.",
		request={
			"application/json": {
				"type": "object",
				"properties": {
					"job_id": {"type": "integer", "example": 1, "description": "ID da vaga para análise"}
				},
				"required": ["job_id"]
			}
		},
		responses={
			200: AnalysisSerializer,
			400: OpenApiResponse(description="job_id é obrigatório"),
			404: OpenApiResponse(description="Job não encontrado"),
			500: OpenApiResponse(description="Erro ao processar análise"),
		},
		examples=[
			OpenApiExample(
				"Exemplo de requisição",
				value={"job_id": 1},
				request_only=True,
			)
		]
	)
	@action(detail=True, methods=["post"])
	def analyze(self, request, pk=None):
		"""Analisa este currículo para uma vaga específica."""
		resume = self.get_object()
		job_id = request.data.get("job_id") or (resume.job_id if resume.job else None)
		if not job_id:
			return Response({"detail": "job_id é obrigatório"}, status=400)
		try:
			job = Job.objects.get(pk=job_id)
		except Job.DoesNotExist:
			return Response({"detail": "Job não encontrado"}, status=404)
		try:
			analysis = ResumeAnalysisService().analyze(resume, job)
		except Exception as exc:  # noqa: BLE001
			return Response({"detail": str(exc)}, status=500)
		return Response(AnalysisSerializer(analysis).data, status=200)


@extend_schema_view(
	list=extend_schema(
		tags=["analyses"],
		summary="Listar todas as análises",
		description="Retorna uma lista paginada de todas as análises de candidatos. Filtre por ?resume={id} ou ?job={id}. Ordene por ?ordering=-score",
	),
	retrieve=extend_schema(
		tags=["analyses"],
		summary="Obter detalhes da análise",
		description="Retorna os detalhes completos de uma análise específica, incluindo score e recomendações.",
	),
)
class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
	"""
	Listagem e visualização de análises (somente leitura).

	Endpoints:
	- GET /api/analyses/ → lista todas as análises
	- GET /api/analyses/{id}/ → detalhe da análise

	Filtros disponíveis:
	- ?resume={resume_id}
	- ?job={job_id}
	- ?ordering=-score (ordena por melhor match)
	"""
	queryset = Analysis.objects.select_related("resume", "job").all()
	serializer_class = AnalysisSerializer
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
	filterset_fields = ["resume", "job"]
	ordering_fields = ["created_at", "score"]
	ordering = ["-score", "-created_at"]
