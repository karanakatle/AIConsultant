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
# AIConsultant

Local-first toolkit to analyze process/architecture diagrams (or text exports), generate readable Mermaid flows, surface low-confidence extractions for human feedback, and publish business-ready agentic AI recommendations with ROI.

## Included
- `AGENTIC_AI_WORKFLOW_PLAYBOOK.md` — implementation blueprint and business reporting structure.
- `agentic_pipeline.py` — runnable end-to-end pipeline.
- `roi_dry_run.py` — ROI calculator module used by the pipeline.
- `samples/check_processing_example.txt` — sample input.

## End-to-end quickstart
Run with sample data:

```bash
python3 agentic_pipeline.py --input samples/check_processing_example.txt --output runs
```

The pipeline writes a timestamped run folder with:
- `01_current_state_summary.md`
- `02_mermaid_high_level.mmd`
- `03_mermaid_detailed/process_flow.mmd`
- `04_assumptions_log.md`
- `05_recommendations_by_risk.md`
- `06_roi_dry_run.md`
- `review_queue.md`
- `run.json`

## Input support
- `.txt`, `.md`, `.csv`, `.log`, `.json`
- `.pdf` (if `pypdf` is installed locally)

For PDF support (optional):
```bash
python3 -m pip install pypdf
This repo now contains a local-first playbook to analyze PDFs/diagrams and produce business-ready agentic AI workflow recommendations under strict enterprise constraints.

## Files
- `AGENTIC_AI_WORKFLOW_PLAYBOOK.md` — full implementation guide, confidence policy, reporting format, and ROI example.
- `roi_dry_run.py` — executable dry-run ROI calculator using explicit assumptions.

## Run ROI example
```bash
python3 roi_dry_run.py
```
