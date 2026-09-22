# Invoice OCR Automation — Evaluation Results

20 synthetic invoices (10 clean, 10 corrupted).

| Metric | Value |
|---|---|
| Field accuracy (clean docs) | 100.0% |
| Routing precision (flags real problems) | 100.0% |
| Routing recall (catches all problems) | 100.0% |

## Routing confusion matrix

| | Flagged for review | Approved |
|---|---|---|
| **Actually needed review** | 9 (correct) | 0 (missed — worst case) |
| **Actually clean** | 0 (over-cautious) | 11 (correct) |
