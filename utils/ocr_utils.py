from __future__ import annotations

from pathlib import Path
from typing import Tuple, List


def ocr_pdf(path: Path) -> Tuple[str, List[dict]]:
    """Run local OCR via pytesseract+pdf2image if installed.

    Returns:
        (full_text, low_confidence_tokens)
    """
    try:
        import pytesseract  # type: ignore
        from pdf2image import convert_from_path  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "OCR dependencies missing. Install: pip install pytesseract pdf2image pillow"
        ) from exc

    images = convert_from_path(str(path))
    full_text: list[str] = []
    low_conf: List[dict] = []

    for page_idx, img in enumerate(images, start=1):
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i, token in enumerate(data.get("text", [])):
            token = (token or "").strip()
            if not token:
                continue
            conf_raw = data.get("conf", ["0"])[i]
            try:
                conf = float(conf_raw)
            except Exception:
                conf = 0.0
            full_text.append(token)
            if conf < 60:
                low_conf.append({"page": page_idx, "token": token, "confidence": conf})

    return " ".join(full_text), low_conf
