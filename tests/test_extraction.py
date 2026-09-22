from invoice_automation.extraction import extract_fields


def test_extracts_all_fields_from_clean_text():
    text = (
        "Nota Fiscal No 12345\n"
        "Emitente: Acme Ltda\n"
        "CNPJ: 12.345.678/0001-95\n"
        "Data de emissao: 10/05/2026\n"
        "Valor Total: R$ 1.234,56"
    )
    fields = extract_fields(text)
    assert fields["numero_nota"] == "12345"
    assert fields["cnpj_emitente"] == "12.345.678/0001-95"
    assert fields["valor_total"] == 1234.56
    assert fields["data_emissao"] == "10/05/2026"


def test_missing_fields_are_none_not_raised():
    fields = extract_fields("Texto sem nenhum campo reconhecivel.")
    assert fields["numero_nota"] is None
    assert fields["cnpj_emitente"] is None
    assert fields["valor_total"] is None
    assert fields["data_emissao"] is None


def test_valor_parses_thousands_separator():
    fields = extract_fields("Valor Total: R$ 12.345,00")
    assert fields["valor_total"] == 12345.00


def test_numero_requires_plausible_digit_count():
    # A 2-digit number shouldn't match — real invoice numbers here are 4-8 digits.
    fields = extract_fields("No 12 itens no carrinho")
    assert fields["numero_nota"] is None
