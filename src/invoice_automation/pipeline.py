"""Orchestrates OCR -> field extraction -> validation -> routing decision for
one invoice. This is the automation: an invoice image goes in, a routing
decision (with reasons) comes out, ready to drive a real accounts-payable
workflow (auto-post vs. queue for human review)."""

from dataclasses import dataclass, field
from pathlib import Path

from invoice_automation.extraction import extract_fields
from invoice_automation.ocr import extract_text
from invoice_automation.validators import is_valid_cnpj, parse_br_date

REQUIRED_FIELDS = ["numero_nota", "cnpj_emitente", "valor_total", "data_emissao"]


@dataclass
class PipelineResult:
    ocr_text: str
    fields: dict
    route: str  # "aprovado" | "revisao_manual"
    reasons: list[str] = field(default_factory=list)


def _validate(fields: dict) -> list[str]:
    reasons = []
    for name in REQUIRED_FIELDS:
        if fields.get(name) is None:
            reasons.append(f"campo ausente: {name}")

    if fields.get("cnpj_emitente") and not is_valid_cnpj(fields["cnpj_emitente"]):
        reasons.append("CNPJ com dígito verificador inválido")

    if fields.get("data_emissao") and parse_br_date(fields["data_emissao"]) is None:
        reasons.append("data de emissão inválida")

    if fields.get("valor_total") is not None and fields["valor_total"] <= 0:
        reasons.append("valor total não positivo")

    return reasons


def process_invoice(image_path: Path, ocr_engine=None) -> PipelineResult:
    ocr_text = extract_text(image_path, engine=ocr_engine)
    fields = extract_fields(ocr_text)
    reasons = _validate(fields)
    route = "revisao_manual" if reasons else "aprovado"
    return PipelineResult(ocr_text=ocr_text, fields=fields, route=route, reasons=reasons)
