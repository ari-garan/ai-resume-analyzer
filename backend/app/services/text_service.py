def normalize_document_text(text: str) -> str:
    lines = [" ".join(line.split()) for line in text.splitlines()]
    normalized = []
    previous_blank = True
    for line in lines:
        if line:
            normalized.append(line)
            previous_blank = False
        elif normalized and not previous_blank:
            normalized.append("")
            previous_blank = True
    return "\n".join(normalized).strip()
