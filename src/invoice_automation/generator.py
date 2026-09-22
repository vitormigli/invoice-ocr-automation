"""Synthetic invoice image generator, for testing the OCR pipeline without any
real invoice. Deliberately includes some corrupted/incomplete examples so the
eval can measure whether the pipeline correctly routes bad scans to review."""

import random

from faker import Faker
from PIL import Image, ImageDraw, ImageFilter, ImageFont

fake = Faker("pt_BR")

_FONT_CANDIDATES = [
    "arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def generate_invoice(seed: int, *, corrupt: bool = False) -> tuple[dict, Image.Image]:
    """Generates one synthetic invoice. If corrupt=True, randomly omits or
    garbles a field, simulating a bad scan that should route to manual review."""
    fake.seed_instance(seed)
    rng = random.Random(seed)

    numero_nota = str(rng.randint(1000, 99999))
    cnpj = fake.cnpj()
    valor = round(rng.uniform(50, 5000), 2)
    data_emissao = fake.date_between(start_date="-1y", end_date="today").strftime("%d/%m/%Y")
    razao_social = fake.company()

    truth = {
        "numero_nota": numero_nota,
        "cnpj_emitente": cnpj,
        "valor_total": valor,
        "data_emissao": data_emissao,
    }

    valor_str = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    lines = [
        f"Nota Fiscal No {numero_nota}",
        f"Emitente: {razao_social}",
        f"CNPJ: {cnpj}",
        f"Data de emissao: {data_emissao}",
        f"Valor Total: R$ {valor_str}",
    ]

    expected_valid = True
    if corrupt:
        drop = rng.choice(["numero", "cnpj", "valor", "data", "blur"])
        if drop == "numero":
            lines[0] = "Nota Fiscal"
            expected_valid = False
        elif drop == "cnpj":
            lines[2] = "CNPJ: (ilegivel)"
            expected_valid = False
        elif drop == "valor":
            lines[4] = "Valor Total: (nao legivel)"
            expected_valid = False
        elif drop == "data":
            lines[3] = "Data de emissao: --/--/----"
            expected_valid = False
        # "blur" keeps all fields but degrades the image below; OCR may still
        # succeed or may not — that's the point, it's not a guaranteed failure.

    img = Image.new("RGB", (700, 260), color="white")
    draw = ImageDraw.Draw(img)
    font = _load_font(22)
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black", font=font)
        y += 40

    if corrupt and rng.random() < 0.6:
        img = img.filter(ImageFilter.GaussianBlur(radius=rng.uniform(1.0, 2.2)))

    return {"truth": truth, "expected_valid": expected_valid}, img
