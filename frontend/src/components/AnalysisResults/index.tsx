import type { CSSProperties } from "react";
import type { AnalysisData } from "../../common/interfaces";
import { PERCENTAGE_DECIMAL_PLACES } from "../../common/constants";

export default function AnalysisResults({ data }: { data: AnalysisData }) {
  const { candidate, job, matching } = data;
  const score = Number(matching.match_percentage) || 0;
  return <section className="results" aria-live="polite" aria-label="Analysis results">
    <section className="result-overview">
      <div className="result-summary"><span className="section-kicker">02 / ASSESSMENT · #{data.analysis_id}</span><h2>Your match report</h2><p>{data.summary}</p></div>
      <div className="score-meter" style={{ "--score": `${Math.max(0, Math.min(score, 100)) * 3.6}deg` } as CSSProperties}><strong>{score.toFixed(PERCENTAGE_DECIMAL_PLACES)}%</strong><span>MATCH</span></div>
    </section>
    <div className="result-grid">
      <ProfileCard label="Candidate profile" title={candidate.name || "Candidate"} skills={candidate.skills} years={candidate.total_experience} yearLabel="years experience" />
      <ProfileCard label="Role requirements" title={job.title || "Job role"} skills={job.required_skills} years={job.required_experience} yearLabel="years required" />
    </div>
    <article className="result-card skill-results">
      <div className="result-card-heading"><span className="section-kicker">SKILL COVERAGE</span><h3>Where the candidate stands</h3></div>
      <div className="skill-columns">
        <SkillColumn title="Matched" items={matching.matched_skills} className="matched" />
        <SkillColumn title="Missing" items={matching.missing_skills} className="missing" />
        {!!matching.partially_matched_skills.length && <SkillColumn title="Partial" items={matching.partially_matched_skills} className="partial" />}
      </div>
      <div className="score-breakdown">{Object.entries(matching.category_scores).map(([name, value]) => <div className="score-breakdown-item" key={name}><span>{name.replaceAll("_", " ")}</span><strong>{value.toFixed(PERCENTAGE_DECIMAL_PLACES)}%</strong></div>)}</div>
    </article>
    <article className="result-card recommendation-card"><span className="section-kicker">NEXT STEPS</span><h3>Make the next move</h3>{data.recommendations.length ? <ol>{data.recommendations.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ol> : <p className="muted-copy">No recommendations were returned.</p>}</article>
  </section>;
}

function ProfileCard({ label, title, skills, years, yearLabel }: { label: string; title: string; skills: string[]; years: number | null; yearLabel: string }) {
  return <article className="result-card profile-result"><span className="section-kicker">{label.toUpperCase()}</span><h3>{title}</h3>{years !== null && <p className="experience-line">{years} {yearLabel}</p>}<div className="skill-chip-list">{skills.length ? skills.map((skill) => <span className="skill-chip" key={skill}>{skill}</span>) : <p className="muted-copy">No skills were identified.</p>}</div></article>;
}

function SkillColumn({ title, items, className }: { title: string; items: string[]; className: string }) {
  return <div className={`skill-column ${className}`}><h4>{title}</h4><ul>{items.length ? items.map((item) => <li key={item}>{item}</li>) : <li className="empty-skill">None identified</li>}</ul></div>;
}
