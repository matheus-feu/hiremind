# HireMind AI

Plataforma de **análise de currículos com IA** usando Django + DRF, LangChain, RAG com ChromaDB e OpenAI.

## Recursos

- Upload de currículos em PDF, DOCX ou TXT.
- Extração de texto + geração de embeddings (OpenAI).
- Indexação vetorial em **ChromaDB** (persistente).
- Pipeline RAG: recupera trechos relevantes do currículo dado uma vaga.
- Análise estruturada via LangChain + ChatOpenAI:
  - senioridade, anos de experiência, skills (matched/missing)
  - **score de aderência (0–100)**
  - resumo profissional
  - perguntas técnicas para entrevista
- Ranking de candidatos por vaga.
- Frontend Bootstrap 5 (CRUD de vagas, currículos, ranking, detalhes da análise).
- API REST DRF (browsable) em `/api/`.

## Stack

Django 5 · DRF · LangChain · langchain-openai · langchain-chroma · ChromaDB · pypdf · python-docx · Bootstrap 5.

## Como rodar

### Opção A — Docker (recomendado)

```bash
cp .env.example .env       # ajuste OPENAI_API_KEY
docker compose up --build
```

Serviços:
- `web`: Django + Gunicorn em http://localhost:8000
- `db`: PostgreSQL 16 em localhost:5432

O entrypoint aguarda o Postgres, roda `migrate` e `collectstatic` automaticamente.

Comandos úteis:
```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py reindex_resumes
docker compose logs -f web
docker compose down -v          # remove volumes (db, chroma, media)
```

### Opção B — Local (sem Docker)

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
pip install -r requirements.txt

cp .env.example .env           # edite e coloque sua OPENAI_API_KEY

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse:
- UI: http://127.0.0.1:8000/
- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/

## Endpoints principais (API)

| Método | URL | Descrição |
| --- | --- | --- |
| GET/POST | `/api/jobs/` | CRUD de vagas |
| GET | `/api/jobs/{id}/ranking/` | Ranking de candidatos para a vaga |
| GET/POST | `/api/resumes/` | CRUD de currículos (multipart upload) |
| POST | `/api/resumes/{id}/analyze/` `{job_id}` | Roda pipeline para 1 currículo |
| POST | `/api/analyze/` `{resume_id, job_id}` | Pipeline completo |
| GET | `/api/analyses/` | Lista análises |

## Arquitetura (camadas)

```
resumes/
├── models.py              # Job, Resume, Analysis (UUID, timestamps)
├── services/
│   ├── extraction.py      # Strategy: PdfExtractor / DocxExtractor / TxtExtractor
│   ├── llm.py             # LLMProvider (factory ChatOpenAI / Embeddings)
│   ├── vector_store.py    # ChromaDB + RAG retrieval
│   ├── analysis.py        # ResumeAnalysisService (orquestrador do pipeline)
│   └── ranking.py         # CandidateRankingService
├── api_views.py + serializers.py + api_urls.py   # DRF
├── views.py + forms.py + urls.py                 # Frontend Django (CBVs)
└── templates/                                    # Bootstrap 5 + crispy
```

Padrões aplicados: **Service Layer**, **Strategy** (extractors), **Factory** (`LLMProvider`),
**Singleton** via `lru_cache` (provider e vector store), **Repository-like** (vector store wrapper),
**Class-Based Views** e separação UI/API.

## Comandos úteis

```bash
python manage.py reindex_resumes   # re-indexa todos os currículos no Chroma
```

