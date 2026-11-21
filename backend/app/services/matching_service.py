import re

from app.core.constants import MATCHING_WEIGHTS, SKILL_ALIASES


def _normalize(values: list[str]) -> dict[str, str]:
    result = {}
    for value in values:
        label = " ".join(value.strip().split())
        key = re.sub(r"[^a-z0-9+#.]", "", label.lower())
        if key:
            result.setdefault(SKILL_ALIASES.get(key, key), label)
    return result


def _ratio(achieved: int, total: int) -> float:
    return achieved / total if total else 0.0


def calculate_match(candidate: dict, job: dict) -> dict:
    candidate_skills = _normalize(candidate.get("skills", []))
    required = _normalize(job.get("required_skills", []))
    preferred = _normalize(job.get("preferred_skills", []))
    matched_keys = required.keys() & candidate_skills.keys()
    missing_keys = required.keys() - candidate_skills.keys()
    preferred_matched = preferred.keys() & candidate_skills.keys()
    required_score = _ratio(len(matched_keys), len(required))
    preferred_score = _ratio(len(preferred_matched), len(preferred))
    required_experience = job.get("required_experience")
    candidate_experience = candidate.get("total_experience")
    experience_match = None
    experience_score = 0.0
    experience_gap = None
    if required_experience is not None and candidate_experience is not None:
        experience_match = candidate_experience >= required_experience
        experience_score = min(candidate_experience / required_experience, 1.0) if required_experience > 0 else 0.0
        experience_gap = max(required_experience - candidate_experience, 0)
    profile_evidence = candidate.get("education", []) + candidate.get("certifications", [])
    education_requirements = job.get("education_requirements", []) + job.get("certifications", [])
    education_score = 0.0
    if education_requirements:
        evidence = " ".join(profile_evidence).casefold()
        education_score = _ratio(sum(1 for item in education_requirements if item.casefold() in evidence), len(education_requirements))
    score = 100 * (
        MATCHING_WEIGHTS["required_skills"] * required_score
        + MATCHING_WEIGHTS["experience"] * experience_score
        + MATCHING_WEIGHTS["education_certifications"] * education_score
        + MATCHING_WEIGHTS["preferred_skills"] * preferred_score
    )
    return {
        "match_percentage": round(score, 2),
        "matched_skills": sorted(required[key] for key in matched_keys),
        "missing_skills": sorted(required[key] for key in missing_keys),
        "partially_matched_skills": [],
        "experience_match": experience_match,
        "experience_gap": experience_gap,
        "category_scores": {
            "required_skills": round(required_score * 100, 2),
            "experience": round(experience_score * 100, 2),
            "education_certifications": round(education_score * 100, 2),
            "preferred_skills": round(preferred_score * 100, 2),
        },
    }
