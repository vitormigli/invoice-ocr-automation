"""The automation itself: polls an inbox folder for new invoice images, runs
each through the pipeline, appends the outcome to a CSV ledger, moves the file
to processed/, and writes a notification file for anything needing review —
the local, dependency-free stand-in for "post to Slack" or "send an email"."""

import csv
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

from invoice_automation.pipeline import process_invoice

LEDGER_COLUMNS = [
    "file", "numero_nota", "cnpj_emitente", "valor_total", "data_emissao",
    "route", "reasons", "processed_at",
]


def _ensure_ledger(ledger_path: Path) -> None:
    if not ledger_path.exists():
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with ledger_path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(LEDGER_COLUMNS)


def _notify(notifications_dir: Path, filename: str, result) -> None:
    notifications_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "file": filename,
        "route": result.route,
        "reasons": result.reasons,
        "fields": result.fields,
        "timestamp": datetime.now().isoformat(),
    }
    (notifications_dir / f"{filename}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def process_one(image_path: Path, inbox: Path, processed: Path, notifications: Path,
                 ledger_path: Path, ocr_engine=None) -> None:
    _ensure_ledger(ledger_path)
    result = process_invoice(image_path, ocr_engine=ocr_engine)

    with ledger_path.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            image_path.name,
            result.fields.get("numero_nota"),
            result.fields.get("cnpj_emitente"),
            result.fields.get("valor_total"),
            result.fields.get("data_emissao"),
            result.route,
            "; ".join(result.reasons),
            datetime.now().isoformat(),
        ])

    if result.route == "revisao_manual":
        _notify(notifications, image_path.name, result)

    processed.mkdir(parents=True, exist_ok=True)
    shutil.move(str(image_path), str(processed / image_path.name))


def watch(inbox: Path, processed: Path, notifications: Path, ledger_path: Path,
          *, poll_seconds: float = 2.0, max_iterations: int | None = None) -> None:
    """Polls `inbox` for image files and processes each one found. Runs
    forever unless max_iterations is set (used by tests/one-shot runs)."""
    from invoice_automation.ocr import load_ocr_engine

    engine = load_ocr_engine()
    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        for image_path in sorted(inbox.glob("*.png")):
            process_one(image_path, inbox, processed, notifications, ledger_path, ocr_engine=engine)
        iterations += 1
        if max_iterations is None:
            time.sleep(poll_seconds)
