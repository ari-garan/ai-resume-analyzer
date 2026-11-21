import type { INPUT_KINDS } from "./constants";

export type InputKind = typeof INPUT_KINDS[keyof typeof INPUT_KINDS];
export type DocumentName = "resume" | "jd";

export interface DocumentSource {
  kind: InputKind;
  file: File | null;
  text: string;
}

export type AnalysisSources = Record<DocumentName, DocumentSource>;

export interface CandidateProfile {
  name: string | null;
  email: string | null;
  phone: string | null;
  total_experience: number | null;
  skills: string[];
  education: string[];
  certifications: string[];
  projects: string[];
  previous_roles: string[];
}

export interface JobRequirements {
  title: string | null;
  company: string | null;
  required_experience: number | null;
  required_skills: string[];
  preferred_skills: string[];
  education_requirements: string[];
  certifications: string[];
  responsibilities: string[];
}

export interface MatchingResult {
  match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  partially_matched_skills: string[];
  experience_match: boolean | null;
  experience_gap: number | null;
  category_scores: Record<string, number>;
}

export interface AnalysisData {
  analysis_id: number;
  candidate: CandidateProfile;
  job: JobRequirements;
  matching: MatchingResult;
  recommendations: string[];
  summary: string;
}

export interface ApiEnvelope<T> {
  statusCode: number;
  status: "success" | "error";
  message: string;
  data: T;
  errorCode?: string;
}
