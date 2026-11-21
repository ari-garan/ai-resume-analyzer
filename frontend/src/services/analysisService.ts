import { API_ENDPOINT } from "../common/constants";
import type { AnalysisData, AnalysisSources, ApiEnvelope } from "../common/interfaces";
import { appendSource } from "../common/helper";

export async function analyzeDocuments(sources: AnalysisSources): Promise<AnalysisData> {
  const form = new FormData();
  form.set("resume_type", sources.resume.kind);
  form.set("jd_type", sources.jd.kind);
  appendSource(form, "resume", sources.resume);
  appendSource(form, "jd", sources.jd);
  const response = await fetch(API_ENDPOINT, { method: "POST", body: form });
  let payload: ApiEnvelope<AnalysisData | null>;
  try {
    payload = await response.json() as ApiEnvelope<AnalysisData | null>;
  } catch {
    throw new Error("The analysis service returned an invalid response.");
  }
  if (!response.ok || payload.status !== "success" || !payload.data) {
    throw new Error(payload.message || "The analysis could not be completed.");
  }
  return payload.data;
}
