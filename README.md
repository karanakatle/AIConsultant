# AIConsultant (Local-First)

A local-first agentic process-mining workflow for enterprise diagrams/PDFs with:
- extraction + confidence flags,
- Mermaid workflow synthesis,
- multi-agent debate (optimizer vs risk),
- weighted proposal ranking,
- ROI output,
- sensitivity analysis,
- before/after simulation.

## One-click CLI
```bash
python3 main.py --file data/sample_check_flow.txt --out report.txt --runs runs --auto-fallback
```

## CLI arguments
- `--file` input path (`.txt/.md/.json/.pdf`)
- `--out` final report file path
- `--runs` artifacts root directory
- `--auto-fallback` run deterministically (no prompt/response copy-paste)

## Multi-agent debate + scoring
The pipeline now does:
1. Optimizer proposes structured JSON recommendations.
2. Risk agent critiques and adjusts risk/confidence.
3. Scoring engine ranks ideas using:
   - `0.4 * ROI + 0.2 * Ease + 0.2 * Confidence - 0.2 * Risk`

## Artifacts per run
- `report.md`
- `flow_mermaid.mmd`
- `extracted_text.txt`
- `proposals_ranked.json`
- `low_confidence.json`
- `sensitivity.json`
- `simulation.json`
- `pipeline_state.json`

## Sample banking input
Use `data/sample_check_flow.txt` for ATM → clearing → posting scenario testing.

## Optional dependencies
For text-based PDFs:
```bash
pip install pdfplumber
```

For scanned PDFs (OCR):
```bash
pip install pytesseract pdf2image pillow
```
System tools (if needed): Tesseract OCR, Poppler.
