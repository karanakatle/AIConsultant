from __future__ import annotations

import json
from pathlib import Path

from utils.ocr_utils import ocr_pdf
from utils.pdf_utils import extract_text_pdf


def run_extractor(path: Path) -> dict:
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md", ".csv", ".log"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return {"text": text, "low_conf": [], "source": "text"}

    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {"text": json.dumps(payload, indent=2), "low_conf": [], "source": "json"}

    if suffix != ".pdf":
        raise ValueError(f"Unsupported input: {path}")

    text_pdf = extract_text_pdf(path)
    if text_pdf:
        return {"text": text_pdf, "low_conf": [], "source": "pdf-text"}

    ocr_text, low_conf = ocr_pdf(path)
    return {"text": ocr_text, "low_conf": low_conf, "source": "ocr"}
