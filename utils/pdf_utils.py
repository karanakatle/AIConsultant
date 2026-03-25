from __future__ import annotations

from pathlib import Path


def extract_text_pdf(path: Path) -> str:
    """Extract text from a text-based PDF using pdfplumber if available."""
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return ""

    text_parts: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()
