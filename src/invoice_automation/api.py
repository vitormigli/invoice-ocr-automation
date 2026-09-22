"""FastAPI service exposing POST /process for one-off invoice processing
(the watcher.py automation is the batch/folder path; this is the on-demand one)."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from invoice_automation.pipeline import process_invoice

app = FastAPI(title="Invoice OCR Automation")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/process")
async def process(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI's documented pattern
    if file.content_type not in ("image/png", "image/jpeg"):
        raise HTTPException(400, f"Unsupported content type: {file.content_type}")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        result = process_invoice(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {
        "fields": result.fields,
        "route": result.route,
        "reasons": result.reasons,
    }
