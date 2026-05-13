from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
	path("admin/", admin.site.urls),
	# API Schema e Documentação
	path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
	path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
	# API Endpoints
	path("api/", include("resumes.api_urls")),
	path("", include("resumes.urls")),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
