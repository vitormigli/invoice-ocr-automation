.PHONY: run watch eval test lint

run:
	uv run uvicorn invoice_automation.api:app --host 0.0.0.0 --port 8000 --reload

watch:
	uv run python -c "from pathlib import Path; from invoice_automation.watcher import watch; watch(Path('data/inbox'), Path('data/processed'), Path('data/notifications'), Path('data/ledger.csv'))"

eval:
	uv run python evals/run_eval.py

test:
	uv run pytest

lint:
	uv run ruff check .
