from pathlib import Path

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import Job, Resume

ALLOWED_EXTS = {".pdf", ".docx", ".txt"}
MAX_UPLOAD_MB = 10


class SkillsTagInput(forms.TextInput):
	"""TextInput marcado para virar um campo de tags via Tom Select no front."""

	def __init__(self, attrs=None):
		base = {
			"class": "form-control skills-tagger",
			"autocomplete": "on",
			"style": "min-height: 48px; padding: 0.75rem; font-size: 1rem;",
			"data-autocomplete-url": reverse_lazy("resumes:skills-autocomplete"),
		}
		base.update(attrs or {})
		super().__init__(attrs=base)


class JobForm(forms.ModelForm):
	class Meta:
		model = Job
		fields = [
			"title", "seniority", "work_model", "location", "contract_type",
			"min_experience_years", "languages", "education_level",
			"required_skills", "nice_to_have",
			"salary_min", "salary_max", "salary_visible", "benefits", "openings",
			"description", "is_active",
		]
		labels = {
			"title": _("Título da vaga"),
			"seniority": _("Senioridade"),
			"work_model": _("Modalidade de trabalho"),
			"location": _("Localização"),
			"contract_type": _("Tipo de contrato"),
			"min_experience_years": _("Experiência mínima (anos)"),
			"languages": _("Idiomas"),
			"education_level": _("Escolaridade"),
			"required_skills": _("Skills obrigatórias"),
			"nice_to_have": _("Skills desejáveis"),
			"salary_min": _("Salário mínimo (R$)"),
			"salary_max": _("Salário máximo (R$)"),
			"salary_visible": _("Exibir faixa salarial publicamente"),
			"benefits": _("Benefícios"),
			"openings": _("Número de vagas"),
			"description": _("Descrição da vaga"),
			"is_active": _("Vaga ativa"),
		}
		widgets = {
			"description": CKEditorWidget(
				config_name="default",
				attrs={'style': 'width: 100%; display: block;'}
			),
			"required_skills": SkillsTagInput(),
			"nice_to_have": SkillsTagInput(),
			"location": forms.TextInput(attrs={"placeholder": _("ex: São Paulo - SP, Remoto")}),
			"languages": forms.TextInput(attrs={"placeholder": _("ex: Inglês avançado, Espanhol intermediário")}),
			"benefits": forms.Textarea(attrs={"rows": 3, "placeholder": _("VR, VA, plano de saúde, gympass…")}),
			"min_experience_years": forms.NumberInput(attrs={"min": 0, "step": 0.5}),
			"salary_min": forms.NumberInput(attrs={"min": 0, "step": 100}),
			"salary_max": forms.NumberInput(attrs={"min": 0, "step": 100}),
			"openings": forms.NumberInput(attrs={"min": 1}),
		}


class ResumeUploadForm(forms.ModelForm):
	class Meta:
		model = Resume
		fields = ["job", "file"]
		labels = {
			"job": _("Vaga para análise"),
			"file": _("Arquivo (PDF, DOCX ou TXT, até 10MB)"),
		}
		widgets = {
			"file": forms.ClearableFileInput(attrs={"accept": ".pdf,.docx,.txt"}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["job"].queryset = Job.objects.filter(is_active=True)
		self.fields["job"].empty_label = _("Vincular a uma vaga")

	def clean_file(self):
		"""Valida o arquivo enviado: extensão, tamanho e presença."""
		f = self.cleaned_data.get("file")

		if not f or not f.name:
			raise ValidationError(_("Envie um arquivo."))
		if Path(f.name).suffix.lower() not in ALLOWED_EXTS:
			raise ValidationError(_("Use: %(exts)s.") % {"exts": ", ".join(sorted(ALLOWED_EXTS))})
		if not f.size:
			raise ValidationError(_("Arquivo vazio."))
		if f.size > MAX_UPLOAD_MB * 1024 * 1024:
			raise ValidationError(_("Máximo %(mb)dMB.") % {"mb": MAX_UPLOAD_MB})

		return f
