import { useRef } from "react";

import { INPUT_KINDS, MAX_FILE_SIZE_LABEL } from "../../common/constants";
import type { DocumentName, DocumentSource } from "../../common/interfaces";

interface Props {
  name: DocumentName;
  title: string;
  description: string;
  source: DocumentSource;
  onUpdate: (name: DocumentName, update: Partial<DocumentSource>) => void;
}

export default function DocumentInput({ name, title, description, source, onUpdate }: Props) {
  const fileInput = useRef<HTMLInputElement>(null);
  const isResume = name === "resume";
  const update = (value: Partial<DocumentSource>) => onUpdate(name, value);
  const fileId = `${name}_file`;
  const textId = `${name}_text`;

  return <article className="source-card">
    <div className="card-title-row">
      <div className={`source-icon ${isResume ? "resume-icon" : "job-icon"}`} aria-hidden="true">{isResume ? "▤" : "▣"}</div>
      <div><h3>{title} <span>*</span></h3><p>{description}</p></div>
    </div>
    <div className="segmented" role="group" aria-label={`${title} input type`}>
      <button type="button" className={`segment${source.kind === INPUT_KINDS.PDF ? " active" : ""}`} aria-pressed={source.kind === INPUT_KINDS.PDF} onClick={() => update({ kind: INPUT_KINDS.PDF })}>Upload PDF</button>
      <button type="button" className={`segment${source.kind === INPUT_KINDS.TEXT ? " active" : ""}`} aria-pressed={source.kind === INPUT_KINDS.TEXT} onClick={() => update({ kind: INPUT_KINDS.TEXT })}>Paste text</button>
    </div>
    {source.kind === INPUT_KINDS.PDF ? <div className="source-body">
      <label className="dropzone" htmlFor={fileId}
        onDragOver={(event) => event.preventDefault()}
        onDragEnter={(event) => { event.preventDefault(); event.currentTarget.classList.add("dragging"); }}
        onDragLeave={(event) => event.currentTarget.classList.remove("dragging")}
        onDrop={(event) => {
          event.preventDefault();
          event.currentTarget.classList.remove("dragging");
          const file = event.dataTransfer.files[0] || null;
          if (file && fileInput.current) {
            const transfer = new DataTransfer();
            transfer.items.add(file);
            fileInput.current.files = transfer.files;
          }
          update({ file });
        }}>
        <input ref={fileInput} id={fileId} key={source.file?.name || "empty"} type="file" accept="application/pdf,.pdf" onChange={(event) => update({ file: event.target.files?.[0] || null })} />
        <span className="upload-icon" aria-hidden="true">↑</span>
        <strong>{source.file ? "Choose a different PDF" : `Drop ${isResume ? "your PDF" : "the job PDF"} here`}</strong>
        <span className="drop-sub">or <span className="browse-link">browse files</span></span>
        <span className="file-limit">PDF only · up to {MAX_FILE_SIZE_LABEL}</span>
      </label>
      {source.file && <div className="selected-file"><span className="selected-file-icon">PDF</span><span className="selected-file-details"><strong>{source.file.name}</strong><small>{(source.file.size / 1024 / 1024).toFixed(2)} MB</small></span><button className="remove-file" type="button" aria-label={`Remove ${source.file.name}`} onClick={() => update({ file: null })}>×</button></div>}
    </div> : <div className="source-body">
      <label className="visually-hidden" htmlFor={textId}>Paste {title.toLowerCase()}</label>
      <textarea id={textId} rows={8} value={source.text} onChange={(event) => update({ text: event.target.value })} placeholder={isResume ? "Paste the candidate’s resume here…" : "Paste the role, requirements, and responsibilities…"} />
      <div className="textarea-footer"><span>{isResume ? "Include skills, experience, and education" : "Include requirements and preferred skills"}</span><span>{source.text.length.toLocaleString()} characters</span></div>
    </div>}
  </article>;
}
