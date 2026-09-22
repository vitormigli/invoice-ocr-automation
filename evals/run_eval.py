"""Generates synthetic invoices (clean and corrupted), runs them through the
real OCR pipeline, and reports field accuracy plus routing precision/recall.
No API calls — PaddleOCR runs locally (downloads model weights once, free)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from invoice_automation.generator import generate_invoice
from invoice_automation.ocr import load_ocr_engine
from invoice_automation.pipeline import process_invoice

EVALS_DIR = Path(__file__).parent
IMAGES_DIR = EVALS_DIR / "images"
N_PER_CLASS = 10


def build_dataset() -> list[dict]:
    IMAGES_DIR.mkdir(exist_ok=True)
    dataset = []
    seed = 2000
    for corrupt in (False, True):
        for _i in range(N_PER_CLASS):
            seed += 1
            meta, img = generate_invoice(seed, corrupt=corrupt)
            image_path = IMAGES_DIR / f"invoice_{seed}.png"
            img.save(image_path)
            dataset.append({"image_path": image_path, **meta})
    return dataset


def field_accuracy(truth: dict, extracted: dict) -> tuple[int, int]:
    correct, total = 0, 0
    for key, expected in truth.items():
        total += 1
        actual = extracted.get(key)
        if isinstance(expected, float) and isinstance(actual, (int, float)):
            correct += abs(expected - actual) <= 0.05
        elif str(expected) == str(actual):
            correct += 1
    return correct, total


def main() -> None:
    print("Loading PaddleOCR (first run downloads model weights, cached after that)...")
    engine = load_ocr_engine()

    dataset = build_dataset()

    total_correct_fields = total_fields = 0
    routing_tp = routing_fp = routing_tn = routing_fn = 0  # positive = "needs review"
    rows = []

    for entry in dataset:
        result = process_invoice(entry["image_path"], ocr_engine=engine)
        needed_review = not entry["expected_valid"]
        flagged_review = result.route == "revisao_manual"

        if needed_review and flagged_review:
            routing_tp += 1
        elif not needed_review and flagged_review:
            routing_fp += 1
        elif not needed_review and not flagged_review:
            routing_tn += 1
        else:
            routing_fn += 1

        if entry["expected_valid"]:
            c, t = field_accuracy(entry["truth"], result.fields)
            total_correct_fields += c
            total_fields += t

        rows.append(
            {
                "image": entry["image_path"].name,
                "expected_valid": entry["expected_valid"],
                "route": result.route,
                "fields": result.fields,
                "reasons": result.reasons,
            }
        )

    field_acc = total_correct_fields / total_fields if total_fields else 0.0
    routing_precision = routing_tp / (routing_tp + routing_fp) if (routing_tp + routing_fp) else 0.0
    routing_recall = routing_tp / (routing_tp + routing_fn) if (routing_tp + routing_fn) else 0.0

    summary = {
        "n_documents": len(dataset),
        "field_accuracy_on_clean_docs": field_acc,
        "routing_precision": routing_precision,
        "routing_recall": routing_recall,
        "routing_confusion": {
            "true_positive_flagged_for_review": routing_tp,
            "false_positive_flagged_for_review": routing_fp,
            "true_negative_approved": routing_tn,
            "false_negative_wrongly_approved": routing_fn,
        },
    }

    (EVALS_DIR / "results.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = ["# Invoice OCR Automation — Evaluation Results", ""]
    lines.append(
        f"{len(dataset)} synthetic invoices ({N_PER_CLASS} clean, {N_PER_CLASS} corrupted).\n"
    )
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Field accuracy (clean docs) | {field_acc:.1%} |")
    lines.append(f"| Routing precision (flags real problems) | {routing_precision:.1%} |")
    lines.append(f"| Routing recall (catches all problems) | {routing_recall:.1%} |")
    lines.append("")
    lines.append("## Routing confusion matrix")
    lines.append("")
    lines.append("| | Flagged for review | Approved |")
    lines.append("|---|---|---|")
    lines.append(
        f"| **Actually needed review** | {routing_tp} (correct) | "
        f"{routing_fn} (missed — worst case) |"
    )
    lines.append(f"| **Actually clean** | {routing_fp} (over-cautious) | {routing_tn} (correct) |")
    (EVALS_DIR / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
