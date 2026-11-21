import logging

from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.ai.agent import analyze_with_ai
from app.core.config import settings
from app.core.exceptions import AppError
from app.models import AnalysisResult, Job, Resume
from app.schemas.analysis import AnalysisData, CandidateProfile, JobRequirements, MatchingResult
from app.services.input_service import process_input

logger = logging.getLogger(__name__)


async def analyze_documents(
    db: Session,
    resume_type: str,
    resume_file,
    resume_text: str | None,
    jd_type: str,
    jd_file,
    jd_text: str | None,
) -> dict:
    normalized_resume = await process_input(resume_type, resume_file, resume_text)
    normalized_jd = await process_input(jd_type, jd_file, jd_text)
    raw, matching = await analyze_with_ai(normalized_resume, normalized_jd)
    try:
        candidate = CandidateProfile.model_validate(raw.get("candidate", {}))
        job = JobRequirements.model_validate(raw.get("job", {}))
        result = MatchingResult.model_validate(matching)
        recommendations = raw.get("recommendations", [])
        if not isinstance(recommendations, list) or not all(isinstance(item, str) for item in recommendations):
            raise ValueError("Recommendations must be a list of strings.")
        summary = raw.get("summary", "")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("Summary is required.")
    except (ValidationError, TypeError, ValueError) as exc:
        if isinstance(exc, ValidationError):
            logger.warning("Analysis validation failed: %s", exc.errors(include_input=False))
        else:
            logger.warning("Analysis validation failed (%s).", type(exc).__name__)
        raise AppError(502, "AI response did not match the required analysis schema.", "INVALID_AI_OUTPUT") from exc
    resume = Resume(
        source_type=resume_type.lower(),
        filename=resume_file.filename if resume_file else None,
        extracted_text=normalized_resume if settings.store_source_text else "",
        parsed_data=candidate.model_dump(mode="json"),
    )
    job_record = Job(
        source_type=jd_type.lower(),
        filename=jd_file.filename if jd_file else None,
        description=normalized_jd if settings.store_source_text else "",
        title=job.title,
        parsed_data=job.model_dump(mode="json"),
    )
    try:
        db.add_all([resume, job_record])
        db.flush()
        analysis = AnalysisResult(
            resume_id=resume.id,
            job_id=job_record.id,
            match_percentage=result.match_percentage,
            matching_details=result.model_dump(mode="json"),
            recommendations=recommendations,
            summary=summary.strip(),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except Exception as exc:
        db.rollback()
        logger.error("Analysis persistence failed (%s).", type(exc).__name__)
        raise AppError(500, "Analysis could not be saved.", "DATABASE_ERROR") from exc
    data = AnalysisData(
        analysis_id=analysis.id,
        candidate=candidate,
        job=job,
        matching=result,
        recommendations=recommendations,
        summary=summary.strip(),
    )
    return data.model_dump(mode="json")


def get_analysis(db: Session, analysis_id: int) -> dict:
    analysis = db.get(AnalysisResult, analysis_id)
    if analysis is None:
        raise AppError(404, "Analysis was not found.", "ANALYSIS_NOT_FOUND")
    candidate = CandidateProfile.model_validate(analysis.resume.parsed_data)
    job = JobRequirements.model_validate(analysis.job.parsed_data)
    matching = MatchingResult.model_validate(analysis.matching_details)
    return AnalysisData(
        analysis_id=analysis.id,
        candidate=candidate,
        job=job,
        matching=matching,
        recommendations=analysis.recommendations,
        summary=analysis.summary,
    ).model_dump(mode="json")
