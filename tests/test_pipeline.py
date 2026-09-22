from pathlib import Path
from unittest.mock import patch

from invoice_automation.pipeline import process_invoice


def _run_with_fake_ocr(ocr_text: str):
    with patch("invoice_automation.pipeline.extract_text", return_value=ocr_text):
        return process_invoice(Path("fake.png"))


def test_clean_invoice_routes_to_aprovado():
    text = (
        "Nota Fiscal No 12345\n"
        "CNPJ: 11.222.333/0001-81\n"
        "Data de emissao: 10/05/2026\n"
        "Valor Total: R$ 500,00"
    )
    result = _run_with_fake_ocr(text)
    assert result.route == "aprovado"
    assert result.reasons == []


def test_missing_field_routes_to_revisao():
    text = "CNPJ: 11.222.333/0001-81\nValor Total: R$ 500,00"
    result = _run_with_fake_ocr(text)
    assert result.route == "revisao_manual"
    assert any("numero_nota" in r for r in result.reasons)


def test_invalid_cnpj_routes_to_revisao():
    text = (
        "Nota Fiscal No 12345\n"
        "CNPJ: 11.111.111/1111-11\n"
        "Data de emissao: 10/05/2026\n"
        "Valor Total: R$ 500,00"
    )
    result = _run_with_fake_ocr(text)
    assert result.route == "revisao_manual"
    assert any("CNPJ" in r for r in result.reasons)


def test_zero_valor_routes_to_revisao():
    text = (
        "Nota Fiscal No 12345\n"
        "CNPJ: 11.222.333/0001-81\n"
        "Data de emissao: 10/05/2026\n"
        "Valor Total: R$ 0,00"
    )
    result = _run_with_fake_ocr(text)
    assert result.route == "revisao_manual"
