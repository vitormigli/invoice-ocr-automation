"""Rule-based field extraction from raw OCR text of a Brazilian invoice."""

import re

_NUMERO_RE = re.compile(r"N[ºo°]?\s*(\d{4,8})")
_CNPJ_RE = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")
_VALOR_RE = re.compile(r"R\$\s*([\d.,]+)")
_DATA_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")


def _parse_valor(raw: str) -> float | None:
    cleaned = raw.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_fields(ocr_text: str) -> dict:
    """Returns extracted fields (None for anything not found). Never raises —
    OCR text is noisy by nature; missing fields are a normal outcome the
    caller (pipeline.py) decides how to handle."""
    numero_match = _NUMERO_RE.search(ocr_text)
    cnpj_match = _CNPJ_RE.search(ocr_text)
    valor_match = _VALOR_RE.search(ocr_text)
    data_match = _DATA_RE.search(ocr_text)

    return {
        "numero_nota": numero_match.group(1) if numero_match else None,
        "cnpj_emitente": cnpj_match.group(0) if cnpj_match else None,
        "valor_total": _parse_valor(valor_match.group(1)) if valor_match else None,
        "data_emissao": data_match.group(1) if data_match else None,
    }
