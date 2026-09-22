"""Wraps PaddleOCR. `enable_mkldnn=False` is required, not cosmetic — see
docs/decisions/0002-disable-mkldnn.md for why."""

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def load_ocr_engine():
    from paddleocr import PaddleOCR

    return PaddleOCR(use_textline_orientation=False, lang="pt", enable_mkldnn=False)


def extract_text(image_path: Path, engine=None) -> str:
    """Runs OCR and returns the recognized lines joined by newlines, in reading
    (top-to-bottom) order as PaddleOCR returns them."""
    engine = engine or load_ocr_engine()
    results = engine.predict(str(image_path))
    lines: list[str] = []
    for res in results:
        lines.extend(res["rec_texts"])
    return "\n".join(lines)
