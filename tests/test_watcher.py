from unittest.mock import patch

from invoice_automation.pipeline import PipelineResult
from invoice_automation.watcher import process_one


def _fake_result(route: str, reasons: list[str]) -> PipelineResult:
    return PipelineResult(
        ocr_text="fake ocr text",
        fields={
            "numero_nota": "123",
            "cnpj_emitente": "11.222.333/0001-81",
            "valor_total": 100.0,
            "data_emissao": "10/05/2026",
        },
        route=route,
        reasons=reasons,
    )


def test_process_one_moves_file_and_writes_ledger(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    notifications = tmp_path / "notifications"
    ledger = tmp_path / "ledger.csv"
    inbox.mkdir()
    image_path = inbox / "invoice_001.png"
    image_path.write_bytes(b"fake image bytes")

    with patch(
        "invoice_automation.watcher.process_invoice", return_value=_fake_result("aprovado", [])
    ):
        process_one(image_path, inbox, processed, notifications, ledger)

    assert not image_path.exists()
    assert (processed / "invoice_001.png").exists()
    assert ledger.exists()
    assert "aprovado" in ledger.read_text(encoding="utf-8")


def test_process_one_writes_notification_on_manual_review(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    notifications = tmp_path / "notifications"
    ledger = tmp_path / "ledger.csv"
    inbox.mkdir()
    image_path = inbox / "invoice_002.png"
    image_path.write_bytes(b"fake image bytes")

    with patch(
        "invoice_automation.watcher.process_invoice",
        return_value=_fake_result("revisao_manual", ["campo ausente: numero_nota"]),
    ):
        process_one(image_path, inbox, processed, notifications, ledger)

    assert (notifications / "invoice_002.png.json").exists()


def test_process_one_does_not_notify_on_approval(tmp_path):
    inbox = tmp_path / "inbox"
    processed = tmp_path / "processed"
    notifications = tmp_path / "notifications"
    ledger = tmp_path / "ledger.csv"
    inbox.mkdir()
    image_path = inbox / "invoice_003.png"
    image_path.write_bytes(b"fake image bytes")

    with patch(
        "invoice_automation.watcher.process_invoice", return_value=_fake_result("aprovado", [])
    ):
        process_one(image_path, inbox, processed, notifications, ledger)

    assert not notifications.exists()
