from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import viewsets

router = DefaultRouter()
router.register(r"jobs", viewsets.JobViewSet)
router.register(r"resumes", viewsets.ResumeViewSet)
router.register(r"analyses", viewsets.AnalysisViewSet)

urlpatterns = [
	path("", include(router.urls)),
]
