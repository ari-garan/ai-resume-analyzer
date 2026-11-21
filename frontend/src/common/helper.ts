import { ACCEPTED_FILE_EXTENSION, INPUT_KINDS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_LABEL } from "./constants";
import type { AnalysisSources, DocumentName, DocumentSource } from "./interfaces";

export function validateSources(sources: AnalysisSources): string {
  const entries: [DocumentName, string][] = [["resume", "Resume"], ["jd", "Job description"]];
  for (const [name, label] of entries) {
    const source = sources[name];
    if (source.kind === INPUT_KINDS.PDF) {
      if (!source.file) return `Add a PDF for the ${label.toLowerCase()} or switch to paste text.`;
      if (!source.file.name.toLowerCase().endsWith(ACCEPTED_FILE_EXTENSION)) return `${label} must be a PDF file.`;
      if (source.file.size > MAX_FILE_SIZE_BYTES) return `${label} PDF exceeds ${MAX_FILE_SIZE_LABEL}.`;
    } else if (!source.text.trim()) {
      return `Paste the ${label.toLowerCase()} text to continue.`;
    }
  }
  return "";
}

export function appendSource(data: FormData, name: DocumentName, source: DocumentSource): void {
  if (source.kind === INPUT_KINDS.PDF && source.file) data.set(`${name}_file`, source.file);
  else if (source.kind === INPUT_KINDS.TEXT) data.set(`${name}_text`, source.text.trim());
}
