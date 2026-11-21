# SkillBridge

FastAPI service that accepts PDF or pasted resume and job description content, extracts structured profiles with an LLM, calculates a deterministic match score in Python, and stores results in MySQL.

## Requirements

- Python 3.11 or newer
- Node.js 22.12 or newer and npm
- MySQL 8 or compatible MySQL server
- A Gemini API key for the analysis endpoint

## Setup

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item .env.example .env
```

Create the database:

```sql
CREATE DATABASE resume_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'resume_app'@'127.0.0.1' IDENTIFIED BY 'replace_with_a_strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, REFERENCES, INDEX, ALTER
  ON resume_analyzer.* TO 'resume_app'@'127.0.0.1';
```

Set `DATABASE_URL`, `GEMINI_API_KEY`, and `AI_MODEL` in `.env`. The default model is `gemini-3.5-flash`, called through Google's Gemini Python SDK with function calling and schema-constrained JSON output. Database tables are created when the application starts if the database is configured. The API currently requires a database because each analysis result is persisted and can be retrieved later. Never use a MySQL root account for the application and never commit `.env`.

MySQL stores parsed candidate and job details, match scores, recommendations, and summaries so `GET /api/v1/analysis/{analysis_id}` can return a saved report. Without persistence the app could still analyze documents, but this implementation requires a database session for analysis and retrieval. SQLAlchemy supports SQLite for a single-user local setup by setting `DATABASE_URL=sqlite:///./resume_analyzer.db`; use MySQL for a shared deployment.

For a local MySQL setup, create a dedicated application account and grant it access only to this database. `STORE_SOURCE_TEXT=false` is the default: raw resume and job text is not retained, though extracted profile details and analysis results are saved for retrieval. Set it to `true` only when raw-text retention is required and covered by your privacy policy.

Resume and job text are sent to Gemini for analysis. Check the data-use terms for the selected Gemini API tier before processing personal data; the API key itself stays on the backend.

## Run

```powershell
uvicorn app.main:app --app-dir backend --reload --port 8001
```

For local frontend development, start the backend in one terminal and Vite in another:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite interface at <http://127.0.0.1:5173/>. Vite proxies `/api` requests to FastAPI on port 8001. The React interface supports PDF upload or pasted text for each input, drag and drop, input validation, loading and error states, and a detailed results view.

To build the frontend for FastAPI static serving, run `npm run build` from `frontend/`, then open <http://127.0.0.1:8001/>. FastAPI serves the generated `frontend/dist` directory.

Swagger UI: <http://127.0.0.1:8001/docs>

Run backend tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -c backend\pytest.ini backend\tests -q
```

## API

All responses use the envelope `{ "statusCode": 200, "status": "success", "message": "...", "data": ... }`. Errors use `status: "error"`, `data: null`, and an `errorCode`.

### Health

`GET /api/v1/health`

### Analyze

`POST /api/v1/analysis` as `multipart/form-data`. Resume and job input types are independent:

| Field | Values | When to provide |
|---|---|---|
| `resume_type` | `pdf`, `text` | Always |
| `resume_file` | PDF file | `resume_type=pdf` |
| `resume_text` | Text | `resume_type=text` |
| `jd_type` | `pdf`, `text` | Always |
| `jd_file` | PDF file | `jd_type=pdf` |
| `jd_text` | Text | `jd_type=text` |

Each PDF is limited by `MAX_FILE_SIZE_MB` (5 MB) and `MAX_PDF_PAGES` (100) by default; text and extracted PDF content are limited to 100,000 characters. Scanned PDFs without embedded text are rejected. The endpoint is limited by `RATE_LIMIT_ANALYSIS` (10 requests per minute by default); other endpoints use `RATE_LIMIT_DEFAULT`. Set `RATE_LIMIT_STORAGE_URI` to a shared Redis URL when running multiple workers; the default in-memory limiter is intended for local development or a single process.

Example with text input:

```powershell
curl.exe -X POST http://127.0.0.1:8001/api/v1/analysis `
  -F "resume_type=text" `
  -F "resume_text=Python developer with 4 years of FastAPI and MySQL experience" `
  -F "jd_type=text" `
  -F "jd_text=Backend developer. Required skills: Python, FastAPI, PostgreSQL. 3 years experience."
```

The matching score uses these fixed weights from `backend/app/core/constants.py`: required skills 60%, experience 25%, education and certifications 10%, preferred skills 5%. Missing evidence scores zero. The LLM can request only registered tools; Python calculates the score and the LLM cannot override it.

### Retrieve an analysis

`GET /api/v1/analysis/{analysis_id}`

## Configuration

See `.env.example` for all supported settings. Keep credentials in `.env` or your deployment secret manager. JWT authentication is intentionally not enabled in this MVP because it has no user accounts or private user-scoped records. Add authentication before exposing user-specific data in a multi-user deployment.

## Project layout

```text
backend/
  app/
    ai/           Gemini structured-output agent and allowlisted registry
    api/v1/       Analysis and health routes
    core/         Settings, constants, exceptions, response envelope
    database/     SQLAlchemy engine and declarative base
    models/       Resume, job, and analysis tables
    schemas/      Pydantic request/response data models
    services/     Input processing, PDF extraction, matching, orchestration
  tests/          Backend and frontend delivery integration tests
  requirements.txt
  pytest.ini
frontend/
  src/
    common/       Shared constants, interfaces, input helpers
    components/   Document input and analysis results
    pages/        Analysis workflow page
    routes/       React Router definitions
    services/     FastAPI client
  index.html
  vite.config.ts
  package.json
```

Vite currently requires Node.js 20.19+ or 22.12+; this project uses the Node 22 line. [Vite setup requirements](https://vite.dev/guide/)

The Python code under `backend/app/` is the backend: its `/api/v1/analysis` route invokes the AI tool-calling flow and deterministic matching service. The React app stays under `frontend/`; during development Vite proxies API calls to FastAPI, and a production build is served by FastAPI from `frontend/dist`.

## Notes

- Uploaded PDFs are processed in memory; original file bytes are not persisted.
- Parsed resume and job details are stored in MySQL for analysis retrieval. Raw source text is not retained unless `STORE_SOURCE_TEXT=true`.
- OCR, user accounts, JWT, and MCP are out of the MVP scope.
- Database schema creation uses SQLAlchemy metadata for the assignment MVP; use Alembic migrations before production schema evolution.
- This MVP has no user authentication or per-user authorization. Do not expose it publicly with real resume data until authentication, authorization for retrieval, deletion and retention workflows, TLS, backups, and operational monitoring are in place.
- Do not log or return full resume contents, API keys, credentials, local paths, or provider error details.
