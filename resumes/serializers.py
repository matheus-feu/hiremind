from rest_framework import serializers

from .models import Analysis, Job, Resume


class JobSerializer(serializers.ModelSerializer):
	class Meta:
		model = Job
		fields = [
			"id", "title", "description", "required_skills", "nice_to_have",
			"seniority", "work_model", "location", "contract_type",
			"min_experience_years", "languages", "education_level",
			"salary_min", "salary_max", "salary_visible", "benefits", "openings",
			"application_deadline", "department",
			"is_active", "created_at", "updated_at",
		]
		read_only_fields = ["id", "created_at", "updated_at"]

	def validate(self, data):
		"""Valida que salary_max >= salary_min se ambos fornecidos."""
		salary_min = data.get("salary_min")
		salary_max = data.get("salary_max")
		if salary_min and salary_max and salary_max < salary_min:
			raise serializers.ValidationError(
				{"salary_max": "Salário máximo deve ser maior ou igual ao mínimo."}
			)
		return data


class ResumeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Resume
		fields = [
			"id", "candidate_name", "candidate_email", "file",
			"status", "job", "created_at", "updated_at",
		]
		read_only_fields = ["id", "status", "created_at", "updated_at"]


class AnalysisSerializer(serializers.ModelSerializer):
	candidate_name = serializers.CharField(source="resume.candidate_name", read_only=True)
	job_title = serializers.CharField(source="job.title", read_only=True)

	class Meta:
		model = Analysis
		fields = [
			"id", "resume", "job", "candidate_name", "job_title", "seniority",
			"years_experience", "skills", "matched_skills", "missing_skills",
			"summary", "score", "strengths", "weaknesses",
			"interview_questions", "created_at",
		]
		read_only_fields = fields


class AnalyzeRequestSerializer(serializers.Serializer):
	resume_id = serializers.UUIDField()
	job_id = serializers.UUIDField()
