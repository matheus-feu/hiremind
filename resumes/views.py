import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
	CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View,
)

from .forms import JobForm, ResumeUploadForm
from .models import Analysis, Job, Resume
from .utils import run_analysis

logger = logging.getLogger(__name__)


def skill_autocomplete(request):
	"""GET /skills/autocomplete/?q=py → [{value, text}, ...] para o Tom Select."""
	q = request.GET.get("q", "").lower()
	skills = {
		s.strip()
		for required, nice in Job.objects.values_list("required_skills", "nice_to_have")
		for chunk in (required, nice)
		for s in (chunk or "").split(",")
		if s.strip() and q in s.lower()
	}
	return JsonResponse([{"value": s, "text": s} for s in sorted(skills)[:30]], safe=False)


class HomeView(TemplateView):
	template_name = "resumes/home.html"

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["jobs_count"] = Job.objects.count()
		ctx["resumes_count"] = Resume.objects.count()
		ctx["analyses_count"] = Analysis.objects.count()
		ctx["recent_analyses"] = (
			Analysis.objects.select_related("resume", "job").order_by("-created_at")[:5]
		)
		return ctx


class JobListView(ListView):
	model = Job
	template_name = "resumes/job_list.html"
	context_object_name = "jobs"
	paginate_by = 20

	def get_queryset(self):
		queryset = Job.objects.select_related().order_by("-created_at")

		status = self.request.GET.get("status")
		if status == "active":
			queryset = queryset.filter(is_active=True)
		elif status == "inactive":
			queryset = queryset.filter(is_active=False)

		seniority = self.request.GET.get("seniority")
		if seniority:
			queryset = queryset.filter(seniority=seniority)

		work_model = self.request.GET.get("work_model")
		if work_model:
			queryset = queryset.filter(work_model=work_model)

		contract_type = self.request.GET.get("contract_type")
		if contract_type:
			queryset = queryset.filter(contract_type=contract_type)

		search = self.request.GET.get("search")
		if search:
			queryset = queryset.filter(title__icontains=search)

		ordering = self.request.GET.get("ordering", "-created_at")
		if ordering:
			queryset = queryset.order_by(ordering)

		return queryset

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["seniority_choices"] = Job.SeniorityChoices.choices
		ctx["work_model_choices"] = Job.WorkModelChoices.choices
		ctx["contract_type_choices"] = Job.ContractTypeChoices.choices
		ctx["total_jobs"] = self.get_queryset().count()
		ctx["active_jobs"] = Job.objects.filter(is_active=True).count()

		query_params = self.request.GET.copy()
		if "page" in query_params:
			query_params.pop("page")
		ctx["query_string"] = query_params.urlencode()

		return ctx


class JobDetailView(DetailView):
	model = Job
	template_name = "resumes/job_detail.html"
	context_object_name = "job"

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["ranking"] = (
			Analysis.objects
			.filter(job=self.object)
			.select_related("resume", "job")
			.order_by("-score", "-years_experience", "-created_at")
		)
		ctx["resumes"] = self.object.resumes.all()[:50]
		return ctx


class JobCreateView(CreateView):
	model = Job
	form_class = JobForm
	template_name = "resumes/job_form.html"
	success_url = reverse_lazy("resumes:job-list")


class JobUpdateView(UpdateView):
	model = Job
	form_class = JobForm
	template_name = "resumes/job_form.html"

	def get_success_url(self):
		return reverse_lazy("resumes:job-detail", args=[self.object.pk])


class JobDeleteView(DeleteView):
	model = Job
	template_name = "resumes/confirm_delete.html"
	success_url = reverse_lazy("resumes:job-list")


class ResumeListView(ListView):
	model = Resume
	template_name = "resumes/resume_list.html"
	context_object_name = "resumes"
	paginate_by = 20
	queryset = Resume.objects.select_related("job")


class ResumeDetailView(DetailView):
	model = Resume
	template_name = "resumes/resume_detail.html"
	context_object_name = "resume"

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx["analyses"] = self.object.analyses.select_related("job").order_by("-score")
		ctx["jobs"] = Job.objects.filter(is_active=True)
		
		all_skills = set()
		for analysis in ctx["analyses"]:
			if analysis.skills:
				all_skills.update(analysis.skills)
		ctx["all_skills"] = sorted(all_skills)
		
		return ctx


class ResumeUploadView(CreateView):
	model = Resume
	form_class = ResumeUploadForm
	template_name = "resumes/resume_form.html"

	def form_valid(self, form):
		response = super().form_valid(form)
		if self.object.job:
			run_analysis(self.request, self.object, self.object.job)
		else:
			messages.info(self.request, "Selecione uma vaga para analisar.")
		return response

	def get_success_url(self):
		return reverse_lazy("resumes:resume-detail", args=[self.object.pk])


class ResumeDeleteView(DeleteView):
	model = Resume
	template_name = "resumes/confirm_delete.html"
	success_url = reverse_lazy("resumes:resume-list")


class RunAnalysisView(View):

	def post(self, request, pk, job_id):
		run_analysis(request, get_object_or_404(Resume, pk=pk), get_object_or_404(Job, pk=job_id))
		return redirect("resumes:resume-detail", pk=pk)


class AnalysisDetailView(DetailView):
	model = Analysis
	template_name = "resumes/analysis_detail.html"
	context_object_name = "analysis"
