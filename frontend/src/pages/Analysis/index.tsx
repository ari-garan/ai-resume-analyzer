import { useState, type FormEvent } from "react";

import AnalysisResults from "../../components/AnalysisResults";
import DocumentInput from "../../components/DocumentInput";
import { INPUT_KINDS } from "../../common/constants";
import { validateSources } from "../../common/helper";
import type { AnalysisData, AnalysisSources, DocumentName, DocumentSource } from "../../common/interfaces";
import { analyzeDocuments } from "../../services/analysisService";

const INITIAL_SOURCE: DocumentSource = { kind: INPUT_KINDS.PDF, file: null, text: "" };

export default function AnalysisPage() {
  const [sources, setSources] = useState<AnalysisSources>({ resume: { ...INITIAL_SOURCE }, jd: { ...INITIAL_SOURCE } });
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);

  function updateSource(name: DocumentName, update: Partial<DocumentSource>) {
    setSources((current) => ({ ...current, [name]: { ...current[name], ...update } }));
    setError("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    const message = validateSources(sources);
    if (message) {
      setError(message);
      document.querySelector(".input-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    setLoading(true);
    try {
      setResult(await analyzeDocuments(sources));
    } catch (requestError) {
      setError(requestError instanceof TypeError ? "Could not reach the analysis service. Check that the API is running and configured." : requestError instanceof Error ? requestError.message : "The analysis could not be completed.");
    } finally {
      setLoading(false);
    }
  }

  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="/" aria-label="SkillBridge home"><span className="brand-mark"><i /><i /><i /></span><span>SkillBridge</span></a><nav className="top-nav" aria-label="Main navigation"><a className="nav-active" href="#analyzer">Analyzer</a></nav><div className="local-status"><span className="status-dot" /> Analysis workspace</div></header>
    <main id="analyzer">
      <section className="intro"><div className="eyebrow"><span className="eyebrow-line" /> TALENT, WITH CLARITY</div><h1>Find the fit.<br /><span>See what’s missing.</span></h1><p className="intro-copy">Compare a resume with a role and get a grounded match score, strengths, and next steps.</p><div className="intro-meta"><span className="meta-icon">✳</span> Evidence-based matching <span className="meta-divider" /> Source PDFs aren’t stored</div></section>
      <form className="workspace" onSubmit={submit} noValidate><section className="input-panel" aria-label="Analysis inputs">
        <div className="panel-heading"><div><span className="section-kicker">01 / INPUTS</span><h2>Set up your comparison</h2></div><span className="required-note"><span>*</span> Required</span></div>
        <div className="source-grid"><DocumentInput name="resume" title="Candidate resume" description="Who are we evaluating?" source={sources.resume} onUpdate={updateSource} /><DocumentInput name="jd" title="Job description" description="What does the role require?" source={sources.jd} onUpdate={updateSource} /></div>
        <div className="form-feedback" role="alert" aria-live="polite">{error}</div>
        <div className="submit-row"><div className="privacy-note"><span>◈</span> PDFs are processed in memory; originals aren’t saved.</div><button className={`analyze-button${loading ? " loading" : ""}`} type="submit" disabled={loading}><span className="button-label">{loading ? "Analyzing documents…" : "Analyze match"}</span><span className="button-arrow">→</span><span className="spinner" /></button></div>
      </section></form>
      {result && <AnalysisResults data={result} />}
      <footer className="footer"><span>SkillBridge - Resume insight, made practical.</span><span>Match score is deterministic and evidence-based.</span></footer>
    </main>
  </div>;
}
