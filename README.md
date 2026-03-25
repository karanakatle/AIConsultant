# AIConsultant (Local-First)

This repo now includes a **modular BMAD-style workflow analyzer** that runs locally and can process process-flow or architecture documents.

## What you get
- `main.py` + `orchestrator.py` for end-to-end execution.
- `agents/` modules for extractor, flow builder, understanding, optimization, ROI, and report generation.
- `utils/` modules for PDF text extraction, OCR fallback, and chunking.
- `prompts/` with reusable agent prompts.
- `samples/check_processing_example.txt` for immediate demo.

## Run end-to-end (non-interactive fallback)
```bash
python3 main.py --input samples/check_processing_example.txt --output runs --auto-fallback
```

This produces a timestamped folder with:
- `report.md`
- `flow_mermaid.mmd`
- `extracted_text.txt`
- `low_confidence.json`
- `pipeline_state.json`

## Run with manual Copilot/LLM loop
```bash
python3 main.py --input samples/check_processing_example.txt --output runs
```
The pipeline prints each prompt. Paste into Copilot/LLM, then paste responses back.

## Optional dependencies
For text-based PDFs:
```bash
pip install pdfplumber
```

For scanned PDFs (OCR):
```bash
pip install pytesseract pdf2image pillow
```
Also install system tools (outside Python) if needed:
- Tesseract OCR
- Poppler

## Existing reference docs
- `AGENTIC_AI_WORKFLOW_PLAYBOOK.md`
- `roi_dry_run.py`
