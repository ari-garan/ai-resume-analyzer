import json
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from app.services.matching_service import calculate_match


class CandidateMatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skills: list[str]
    total_experience: float | None
    education: list[str]
    certifications: list[str]


class JobMatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required_skills: list[str]
    preferred_skills: list[str]
    required_experience: float | None
    education_requirements: list[str]
    certifications: list[str]


def build_tools() -> tuple[list[dict], dict[str, Callable]]:
    tools = [
        {"type": "function", "name": "calculate_match", "description": "Calculate deterministic weighted matching. Call after extracting profile and job requirements.", "parameters": {"type": "object", "properties": {"candidate": {"type": "object", "properties": {"skills": {"type": "array", "items": {"type": "string"}}, "total_experience": {"type": ["number", "null"]}, "education": {"type": "array", "items": {"type": "string"}}, "certifications": {"type": "array", "items": {"type": "string"}}}, "required": ["skills", "total_experience", "education", "certifications"], "additionalProperties": False}, "job": {"type": "object", "properties": {"required_skills": {"type": "array", "items": {"type": "string"}}, "preferred_skills": {"type": "array", "items": {"type": "string"}}, "required_experience": {"type": ["number", "null"]}, "education_requirements": {"type": "array", "items": {"type": "string"}}, "certifications": {"type": "array", "items": {"type": "string"}}}, "required": ["required_skills", "preferred_skills", "required_experience", "education_requirements", "certifications"], "additionalProperties": False}}, "required": ["candidate", "job"], "additionalProperties": False}, "strict": True},
    ]
    handlers = {"calculate_match": lambda args: calculate_match(args["candidate"], args["job"])}
    return tools, handlers


def execute_tool(name: str, arguments: str, handlers: dict[str, Callable]) -> str:
    if name not in handlers:
        raise ValueError("Requested tool is not registered.")
    values = json.loads(arguments)
    if not isinstance(values, dict):
        raise ValueError("Tool arguments must be a JSON object.")
    if name == "calculate_match":
        if set(values) != {"candidate", "job"}:
            raise ValueError("Candidate and job matching data are required.")
        values["candidate"] = CandidateMatchInput.model_validate(values["candidate"]).model_dump()
        values["job"] = JobMatchInput.model_validate(values["job"]).model_dump()
    return json.dumps(handlers[name](values), ensure_ascii=False)
