from pydantic import BaseModel, EmailStr, Field


class CandidateProfile(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    total_experience: float | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    previous_roles: list[str] = Field(default_factory=list)


class JobRequirements(BaseModel):
    title: str | None = None
    company: str | None = None
    required_experience: float | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class AIAnalysisOutput(BaseModel):
    candidate: CandidateProfile
    job: JobRequirements
    recommendations: list[str]
    summary: str


class MatchingResult(BaseModel):
    match_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    partially_matched_skills: list[str] = Field(default_factory=list)
    experience_match: bool | None = None
    experience_gap: float | None = None
    category_scores: dict[str, float]


class AnalysisData(BaseModel):
    analysis_id: int
    candidate: CandidateProfile
    job: JobRequirements
    matching: MatchingResult
    recommendations: list[str]
    summary: str


class AnalysisEnvelope(BaseModel):
    statusCode: int
    status: str
    message: str
    data: AnalysisData
