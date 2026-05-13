from django.contrib import admin
from .models import Job, Resume, Analysis


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "seniority", "is_active", "created_at")
    list_filter = ("seniority", "is_active")
    search_fields = ("title", "description")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("candidate_name", "candidate_email", "status", "job", "created_at")
    list_filter = ("status", "job")
    search_fields = ("candidate_name", "candidate_email")
    readonly_fields = ("raw_text", "status", "status_detail")


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("resume", "job", "score", "seniority", "years_experience", "created_at")
    list_filter = ("job", "seniority")
    search_fields = ("resume__candidate_name", "summary")

