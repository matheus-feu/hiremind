from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
	DJANGO_DEBUG=(bool, True),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"rest_framework",
	"drf_spectacular",
	"crispy_forms",
	"crispy_bootstrap5",
	"ckeditor",
	"django_filters",
	"resumes.apps.ResumesConfig",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR / "templates"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	},
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
	"default": env.db_url(
		"DATABASE_URL",
		default="postgres://hiremind:hiremind@localhost:5432/hiremind",
	)
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DATABASES["default"].setdefault("ATOMIC_REQUESTS", False)

AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

X_FRAME_OPTIONS = "SAMEORIGIN"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

REST_FRAMEWORK = {
	"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
	'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
	"PAGE_SIZE": 20,
	"DEFAULT_RENDERER_CLASSES": [
		"rest_framework.renderers.JSONRenderer",
		"rest_framework.renderers.BrowsableAPIRenderer",
	],
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"

SPECTACULAR_SETTINGS = {
	"TITLE": "HireMind AI API",
	"DESCRIPTION": "API para gerenciamento de vagas, currículos e análises de candidatos com IA",
	"VERSION": "1.0.0",
	"SERVE_INCLUDE_SCHEMA": False,
	"COMPONENT_SPLIT_REQUEST": True,
	"SCHEMA_PATH_PREFIX": r"/api/",
	"SERVERS": [
		{"url": "http://localhost:8000", "description": "Servidor de Desenvolvimento"},
	],
	"TAGS": [
		{"name": "jobs", "description": "Operações relacionadas a vagas"},
		{"name": "resumes", "description": "Operações relacionadas a currículos"},
		{"name": "analyses", "description": "Operações relacionadas a análises de candidatos"},
	],
}

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = env("OPENAI_EMBEDDING_MODEL", default="text-embedding-3-small")
CHROMA_PERSIST_DIR = env("CHROMA_PERSIST_DIR", default=str(BASE_DIR / ".chroma"))

CKEDITOR_CONFIGS = {
	"default": {
		"height": 320,
		"width": "100%",
		"toolbar": "Custom",
		"toolbar_Custom": [
			["Format", "Bold", "Italic", "Underline"],
			["NumberedList", "BulletedList", "Blockquote"],
			["Link", "Unlink"],
			["RemoveFormat", "Source"],
		],
		"removePlugins": "elementspath",
		"resize_enabled": True,
	},
}

LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
	},
	"handlers": {
		"console": {"class": "logging.StreamHandler", "formatter": "verbose"},
	},
	"root": {"handlers": ["console"], "level": "INFO"},
	"loggers": {
		"resumes": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
	},
}
