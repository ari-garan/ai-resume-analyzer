from app.services.matching_service import calculate_match


def test_matching_score_is_deterministic_and_bounded():
    candidate = {
        "skills": ["Python", "Postgres", "Python"],
        "total_experience": 2,
        "education": [],
        "certifications": [],
    }
    job = {
        "required_skills": ["Python", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS"],
        "required_experience": 4,
        "education_requirements": [],
        "certifications": [],
    }
    first = calculate_match(candidate, job)
    second = calculate_match(candidate, job)
    assert first == second
    assert first["matched_skills"] == ["PostgreSQL", "Python"]
    assert first["missing_skills"] == ["Docker"]
    assert 0 <= first["match_percentage"] <= 100


def test_empty_requirements_do_not_create_automatic_points():
    result = calculate_match(
        {"skills": [], "education": ["Bachelor degree"], "certifications": []},
        {"required_skills": [], "preferred_skills": [], "education_requirements": [], "certifications": []},
    )
    assert result["match_percentage"] == 0
