from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limiter import limiter
from app.core.responses import success_response
from app.database.connection import get_db
from app.schemas.analysis import AnalysisEnvelope
from app.services.analysis_service import analyze_documents, get_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisEnvelope, summary="Analyze a resume against a job description")
@limiter.limit(settings.rate_limit_analysis)
async def analyze(
    request: Request,
    resume_type: Annotated[str, Form(description="pdf or text")],
    jd_type: Annotated[str, Form(description="pdf or text")],
    resume_file: Annotated[UploadFile | None, File(description="Required when resume_type is pdf")] = None,
    resume_text: Annotated[str | None, Form(description="Required when resume_type is text")] = None,
    jd_file: Annotated[UploadFile | None, File(description="Required when jd_type is pdf")] = None,
    jd_text: Annotated[str | None, Form(description="Required when jd_type is text")] = None,
    db: Session = Depends(get_db),
):
    data = await analyze_documents(db, resume_type, resume_file, resume_text, jd_type, jd_file, jd_text)
    return success_response("Analysis completed successfully.", data)


@router.get("/{analysis_id}", response_model=AnalysisEnvelope, summary="Retrieve a saved analysis")
def retrieve_analysis(analysis_id: int, db: Session = Depends(get_db)):
    return success_response("Analysis retrieved successfully.", get_analysis(db, analysis_id))
