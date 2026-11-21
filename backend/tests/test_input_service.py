import io

import pymupdf
import pytest
from fastapi import UploadFile

from app.core.exceptions import AppError
from app.services.input_service import process_input


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    data = document.tobytes()
    document.close()
    return data


@pytest.mark.asyncio
@pytest.mark.parametrize("resume_kind,jd_kind", [("pdf", "pdf"), ("pdf", "text"), ("text", "pdf"), ("text", "text")])
async def test_independent_input_combinations(resume_kind, jd_kind):
    resume_file = UploadFile(filename="resume.pdf", file=io.BytesIO(make_pdf("Resume content"))) if resume_kind == "pdf" else None
    jd_file = UploadFile(filename="job.pdf", file=io.BytesIO(make_pdf("Job content"))) if jd_kind == "pdf" else None
    resume_text = None if resume_kind == "pdf" else "Resume content"
    jd_text = None if jd_kind == "pdf" else "Job content"
    assert await process_input(resume_kind, resume_file, resume_text) == "Resume content"
    assert await process_input(jd_kind, jd_file, jd_text) == "Job content"


@pytest.mark.asyncio
async def test_empty_text_is_rejected():
    with pytest.raises(AppError) as error:
        await process_input("text", None, " \n ")
    assert error.value.status_code == 422


@pytest.mark.asyncio
async def test_text_normalization_preserves_section_breaks():
    result = await process_input("text", None, "Summary\n  Python developer\n\nExperience\nFastAPI")
    assert result == "Summary\nPython developer\n\nExperience\nFastAPI"


@pytest.mark.asyncio
async def test_pdf_extracted_text_obeys_length_limit(monkeypatch):
    from app.services import input_service

    monkeypatch.setattr(input_service, "MAX_TEXT_LENGTH", 5)
    upload = UploadFile(filename="resume.pdf", file=io.BytesIO(b"%PDF-test"))
    monkeypatch.setattr(input_service, "extract_text_from_pdf", lambda _: "123456")
    with pytest.raises(AppError) as error:
        await process_input("pdf", upload, None)
    assert error.value.status_code == 413
    assert error.value.error_code == "TEXT_TOO_LARGE"


def test_pdf_page_count_is_limited(monkeypatch):
    from app.core.config import settings
    from app.services.pdf_service import extract_text_from_pdf

    document = pymupdf.open()
    document.new_page()
    document.new_page()
    content = document.tobytes()
    document.close()
    monkeypatch.setattr(settings, "max_pdf_pages", 1)
    with pytest.raises(AppError) as error:
        extract_text_from_pdf(content)
    assert error.value.status_code == 413
    assert error.value.error_code == "PDF_PAGE_LIMIT_EXCEEDED"
