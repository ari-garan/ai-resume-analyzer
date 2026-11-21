from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_PATH = APP_ROOT / "frontend"
FRONTEND_BUILD_PATH = FRONTEND_PATH / "dist"
API_V1_PREFIX_DEFAULT = "/api/v1"
DEFAULT_AI_MODEL = "gemini-3.5-flash"
ALLOWED_INPUT_TYPES = frozenset({"pdf", "text"})
PDF_MAGIC_BYTES = b"%PDF-"
DEFAULT_MAX_FILE_SIZE_MB = 5
DEFAULT_MAX_PDF_PAGES = 100
DEFAULT_STORE_SOURCE_TEXT = False
DEFAULT_AI_REQUEST_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOOL_CALL_ROUNDS = 5
DEFAULT_ANALYSIS_RATE_LIMIT = "10/minute"
DEFAULT_RATE_LIMIT = "60/minute"
DEFAULT_RATE_LIMIT_STORAGE_URI = "memory://"
MATCHING_WEIGHTS = {
    "required_skills": 0.60,
    "experience": 0.25,
    "education_certifications": 0.10,
    "preferred_skills": 0.05,
}
SKILL_ALIASES = {
    "postgres": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "amazonwebservices": "aws",
    "k8s": "kubernetes",
}
API_STATUS_SUCCESS = "success"
API_STATUS_ERROR = "error"
PDF_MIME_TYPE = "application/pdf"
MAX_TEXT_LENGTH = 100_000
