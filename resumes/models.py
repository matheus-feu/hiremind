import uuid

from django.db import models


class TimeStampedModel(models.Model):
	"""Abstract model that provides created/updated timestamps."""

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Job(TimeStampedModel):
	"""Represents an open job/position to which candidates can be matched."""

	class SeniorityChoices(models.TextChoices):
		APPRENTICE = "apprentice", "Jovem Aprendiz"
		INTERN = "intern", "Estágio"
		TRAINEE = "trainee", "Trainee"
		JUNIOR = "junior", "Júnior"
		MID_LEVEL = "mid_level", "Pleno"
		SENIOR = "senior", "Sênior"
		SPECIALIST = "specialist", "Especialista"
		STAFF = "staff", "Staff"
		PRINCIPAL = "principal", "Principal"
		TECH_LEAD = "tech_lead", "Tech Lead"
		ARCHITECT = "architect", "Arquiteto"
		COORDINATOR = "coordinator", "Coordenador(a)"
		PRODUCT_OWNER = "product_owner", "Product Owner"
		MANAGER = "manager", "Gerente"
		HEAD = "head", "Head"
		DIRECTOR = "director", "Diretor(a)"
		VP = "vp", "VP"
		C_LEVEL = "c_level", "C-Level (CTO/CIO/CPO)"

	class WorkModelChoices(models.TextChoices):
		ONSITE = "onsite", "Presencial"
		REMOTE = "remote", "Remoto"
		HYBRID = "hybrid", "Híbrido"

	class ContractTypeChoices(models.TextChoices):
		CLT = "clt", "CLT"
		PJ = "pj", "PJ"
		INTERNSHIP = "internship", "Estágio"
		FREELANCE = "freelance", "Freelance"
		TEMPORARY = "temporary", "Temporário"

	class EducatinonLevelChoices(models.TextChoices):
		NONE = "none", "Sem exigência"
		HIGH_SCHOOL = "high_school", "Ensino Médio"
		ASSOCIATE = "associate", "Tecnólogo"
		BACHELORS = "bachelors", "Bacharelado"
		MASTERS = "masters", "Mestrado"
		PHD = "phd", "Doutorado"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=200)
	description = models.TextField(help_text="Descrição detalhada da vaga, responsabilidades, etc.")
	required_skills = models.TextField(blank=True)
	nice_to_have = models.TextField(blank=True)
	seniority = models.CharField(max_length=20, choices=SeniorityChoices, default=SeniorityChoices.MID_LEVEL)
	work_model = models.CharField(max_length=20, choices=WorkModelChoices, default=WorkModelChoices.ONSITE)
	education_level = models.CharField(max_length=100, blank=True, choices=EducatinonLevelChoices, default=EducatinonLevelChoices.NONE)
	min_experience_years = models.FloatField(default=0, help_text="Anos mínimos de experiência")
	location = models.CharField(max_length=100, blank=True, help_text="Cidade/Estado ou 'Remoto'")
	contract_type = models.CharField(max_length=20, choices=ContractTypeChoices, default=ContractTypeChoices.CLT)
	languages = models.CharField(max_length=200, blank=True, help_text="Idiomas requeridos")
	salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	salary_visible = models.BooleanField(default=False)
	benefits = models.TextField(blank=True, help_text="Benefícios oferecidos")
	openings = models.PositiveIntegerField(default=1)
	application_deadline = models.DateField(null=True, blank=True)
	department = models.CharField(max_length=100, blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"{self.title} ({self.get_seniority_display()})"

	@property
	def required_skills_list(self) -> list[str]:
		return [s.strip() for s in self.required_skills.split(",") if s.strip()]

	@property
	def nice_to_have_list(self) -> list[str]:
		return [s.strip() for s in self.nice_to_have.split(",") if s.strip()]


class Resume(TimeStampedModel):
	"""Uploaded candidate resume."""

	class Status(models.TextChoices):
		PENDING = "pending", "Pendente"
		PROCESSING = "processing", "Processando"
		DONE = "done", "Concluído"
		ERROR = "error", "Erro"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	candidate_name = models.CharField(max_length=200, blank=True)
	candidate_email = models.EmailField(blank=True)
	file = models.FileField(upload_to="resumes/%Y/%m/")
	raw_text = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status, default=Status.PENDING)
	status_detail = models.TextField(blank=True, default="")
	job = models.ForeignKey(
		Job,
		on_delete=models.CASCADE,
		related_name="resumes",
		null=True,
		blank=True
	)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return self.candidate_name or f"Currículo {self.id}"

	def mark_processing(self) -> None:
		self.status = self.Status.PROCESSING
		self.save(update_fields=["status", "updated_at"])

	def mark_done(self) -> None:
		self.status = self.Status.DONE
		self.save(update_fields=["status", "updated_at"])

	def mark_error(self, message: str) -> None:
		self.status = self.Status.ERROR
		self.status_detail = message
		self.save(update_fields=["status", "status_detail", "updated_at"])


class Analysis(TimeStampedModel):
	"""AI-generated analysis of a resume against a job."""

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="analyses")
	job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="analyses")

	seniority = models.CharField(max_length=50, blank=True)
	years_experience = models.FloatField(default=0)
	skills = models.JSONField(default=list, blank=True)
	matched_skills = models.JSONField(default=list, blank=True)
	missing_skills = models.JSONField(default=list, blank=True)
	summary = models.TextField(blank=True)
	score = models.FloatField(default=0, help_text="0-100 fit score")
	strengths = models.JSONField(default=list, blank=True)
	weaknesses = models.JSONField(default=list, blank=True)
	interview_questions = models.JSONField(default=list, blank=True)
	raw_response = models.JSONField(default=dict, blank=True)

	class Meta:
		ordering = ["-score", "-created_at"]
		verbose_name_plural = "Analyses"
		constraints = [
			models.UniqueConstraint(fields=["resume", "job"], name="uniq_resume_job_analysis")
		]

	def __str__(self) -> str:
		return f"Análise {self.resume} → {self.job} ({self.score:.1f})"
