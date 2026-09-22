from invoice_automation.generator import generate_invoice


def test_clean_invoice_has_all_truth_fields():
    meta, img = generate_invoice(seed=1, corrupt=False)
    assert meta["expected_valid"] is True
    assert all(
        meta["truth"][k] for k in ["numero_nota", "cnpj_emitente", "valor_total", "data_emissao"]
    )
    assert img.size[0] > 0 and img.size[1] > 0


def test_generation_is_deterministic():
    meta1, _ = generate_invoice(seed=42)
    meta2, _ = generate_invoice(seed=42)
    assert meta1["truth"] == meta2["truth"]


def test_different_seeds_give_different_invoices():
    meta1, _ = generate_invoice(seed=1)
    meta2, _ = generate_invoice(seed=2)
    assert meta1["truth"] != meta2["truth"]
