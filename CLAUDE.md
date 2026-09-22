# Project instructions for Claude

This project follows the rules of the portfolio master plan:

1. No client code or data — synthetic invoices only (see `src/invoice_automation/generator.py`).
2. No committed secrets — this project needs none (no paid API is called;
   `gitleaks` still runs on pre-commit and in CI as a safety net).
3. Every project reports numeric evaluation metrics — see `evals/results.md`.
4. Everything runs with a single command: `docker compose up` or `make run`.
5. README in English, with a short "Resumo em português" section at the end.
   Header banner + badges matching the other portfolio repos.
6. Small, descriptive commits using Conventional Commits.
7. Prefer simplicity — regex extraction, no document-AI framework; a poll loop
   for the "watcher", no message queue.

## Layout

- `src/invoice_automation/ocr.py` — PaddleOCR wrapper. `enable_mkldnn=False` is
  required on this CPU/Windows setup — see
  `docs/decisions/0002-disable-mkldnn.md` before touching this file.
- `src/invoice_automation/extraction.py` — regex field extraction from OCR text.
- `src/invoice_automation/pipeline.py` — OCR → extract → validate → route.
- `src/invoice_automation/watcher.py` — the automation: polls an inbox folder,
  processes each file, logs to a CSV ledger, writes a notification file for
  anything routed to manual review.
- `evals/run_eval.py` — generates synthetic invoices (clean and corrupted),
  runs them through the real OCR pipeline, and reports field accuracy and
  routing precision/recall; the only network call this project ever makes is a
  one-time PaddleOCR model download, and it's free.
