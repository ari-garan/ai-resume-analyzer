from fastapi import UploadFile

from app.core.config import settings
from app.core.constants import ALLOWED_INPUT_TYPES, MAX_TEXT_LENGTH
from app.core.exceptions import AppError
from app.services.pdf_service import extract_text_from_pdf
from app.services.text_service import normalize_document_text


async def process_input(input_type: str, file: UploadFile | None, text: str | None) -> str:
    kind = input_type.strip().lower()
    if kind not in ALLOWED_INPUT_TYPES:
        raise AppError(422, "Input type must be 'pdf' or 'text'.", "INVALID_INPUT_TYPE")
    if kind == "pdf":
        if file is None or text is not None:
            raise AppError(422, "PDF mode requires one file and no text value.", "INVALID_INPUT_SOURCE")
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise AppError(415, "Only PDF files are supported.", "UNSUPPORTED_FILE_TYPE")
        content = await file.read(settings.max_file_size_mb * 1024 * 1024 + 1)
        if len(content) > settings.max_file_size_mb * 1024 * 1024:
            raise AppError(413, "Uploaded PDF exceeds the file size limit.", "FILE_TOO_LARGE")
        normalized = extract_text_from_pdf(content)
        if len(normalized) > MAX_TEXT_LENGTH:
            raise AppError(413, "Extracted PDF text exceeds the allowed length.", "TEXT_TOO_LARGE")
        return normalized
    if file is not None:
        raise AppError(422, "Text mode does not accept a file.", "INVALID_INPUT_SOURCE")
    normalized = normalize_document_text(text or "")
    if not normalized:
        raise AppError(422, "Text input cannot be empty.", "EMPTY_TEXT")
    if len(normalized) > MAX_TEXT_LENGTH:
        raise AppError(413, "Text input exceeds the allowed length.", "TEXT_TOO_LARGE")
    return normalized
