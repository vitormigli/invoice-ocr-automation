# 1. Regex extraction over a document-AI/LLM extraction layer

## Status

Accepted

## Context

This project exists specifically to demonstrate a classic-OCR automation pipeline
as a companion/contrast to `doc-extraction-pipeline` (Claude vision) in the same
portfolio. Reaching for an LLM here to parse OCR text would just rebuild that other
project with worse input (garbled OCR text instead of a clean image).

## Decision

Extract invoice fields from raw OCR text with plain regex
(`src/invoice_automation/extraction.py`). No LLM anywhere in this pipeline.

## Consequences

- Zero marginal cost per document — the entire pipeline (OCR + extraction) runs on
  local CPU.
- Regex is brittle to layout variation in a way an LLM wouldn't be — this pipeline
  is tuned to the one invoice layout `generator.py` produces, not a general one.
  The routing step (`pipeline.py`) exists precisely to catch what extraction
  misses and send it to a human instead of silently guessing.
- This is the honest trade-off the eval measures: classic OCR + rules is free and
  fast but layout-fragile; `doc-extraction-pipeline`'s Claude vision approach costs
  money per document but tolerates layout variation.
