import pymupdf

from app.core.config import settings
from app.core.constants import PDF_MAGIC_BYTES
from app.core.exceptions import AppError
from app.services.text_service import normalize_document_text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise AppError(415, "Uploaded file is not a valid PDF.", "INVALID_PDF")
    try:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as document:
            if document.is_encrypted:
                raise AppError(400, "Encrypted PDFs are not supported.", "ENCRYPTED_PDF")
            if document.page_count > settings.max_pdf_pages:
                raise AppError(413, "PDF contains more pages than allowed.", "PDF_PAGE_LIMIT_EXCEEDED")
            text = "\n".join(page.get_text() for page in document)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(400, "PDF could not be read.", "CORRUPTED_PDF") from exc
    normalized = normalize_document_text(text)
    if not normalized:
        raise AppError(422, "PDF contains no extractable text.", "PDF_TEXT_NOT_FOUND")
    return normalized
