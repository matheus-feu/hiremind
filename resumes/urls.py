from django.urls import path

from . import views

app_name = "resumes"

urlpatterns = [
	path("", views.HomeView.as_view(), name="home"),
	path("skills/autocomplete/", views.skill_autocomplete, name="skills-autocomplete"),

	# Jobs
	path("jobs/", views.JobListView.as_view(), name="job-list"),
	path("jobs/new/", views.JobCreateView.as_view(), name="job-create"),
	path("jobs/<uuid:pk>/", views.JobDetailView.as_view(), name="job-detail"),
	path("jobs/<uuid:pk>/edit/", views.JobUpdateView.as_view(), name="job-edit"),
	path("jobs/<uuid:pk>/delete/", views.JobDeleteView.as_view(), name="job-delete"),

	# Resumes
	path("resumes/", views.ResumeListView.as_view(), name="resume-list"),
	path("resumes/new/", views.ResumeUploadView.as_view(), name="resume-upload"),
	path("resumes/new/<uuid:job_id>/", views.ResumeUploadView.as_view(), name="resume-upload-for-job"),
	path("resumes/<uuid:pk>/", views.ResumeDetailView.as_view(), name="resume-detail"),
	path("resumes/<uuid:pk>/delete/", views.ResumeDeleteView.as_view(), name="resume-delete"),
	path("resumes/<uuid:pk>/analyze/<uuid:job_id>/", views.RunAnalysisView.as_view(), name="resume-analyze"),

	# Analyses
	path("analyses/<uuid:pk>/", views.AnalysisDetailView.as_view(), name="analysis-detail"),
]
