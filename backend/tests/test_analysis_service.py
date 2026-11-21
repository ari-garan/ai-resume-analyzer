import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models import Job, Resume
from app.services import analysis_service
from app.services.matching_service import calculate_match


@pytest.mark.asyncio
async def test_analysis_does_not_retain_source_text_by_default(monkeypatch):
    candidate = {
        "name": "Jordan Lee",
        "email": "jordan.lee@example.com",
        "phone": None,
        "total_experience": 2.5,
        "skills": ["Python"],
        "education": [],
        "certifications": [],
        "projects": [],
        "previous_roles": [],
    }
    job = {
        "title": "Backend Engineer",
        "company": "Example Co",
        "required_experience": 3,
        "required_skills": ["Python"],
        "preferred_skills": [],
        "education_requirements": [],
        "certifications": [],
        "responsibilities": [],
    }

    async def fake_analysis(resume_text, jd_text):
        return (
            {"candidate": candidate, "job": job, "recommendations": [], "summary": "Relevant Python experience."},
            calculate_match(candidate, job),
        )

    monkeypatch.setattr(analysis_service, "analyze_with_ai", fake_analysis)
    monkeypatch.setattr(analysis_service.settings, "store_source_text", False)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        await analysis_service.analyze_documents(
            db,
            "text",
            None,
            "Jordan Lee - private resume text",
            "text",
            None,
            "Private job description text",
        )
        assert db.query(Resume).one().extracted_text == ""
        assert db.query(Job).one().description == ""
    engine.dispose()
