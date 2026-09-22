"""Business validation: CNPJ check digit and date parsing."""

import re
from datetime import date, datetime


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cnpj(cnpj: str) -> bool:
    d = _digits(cnpj)
    if len(d) != 14 or d == d[0] * 14:
        return False

    def check_digit(nums: str, weights: list[int]) -> int:
        total = sum(int(n) * w for n, w in zip(nums, weights, strict=True))
        r = total % 11
        return 0 if r < 2 else 11 - r

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = check_digit(d[:12], w1)
    d2 = check_digit(d[:12] + str(d1), w2)
    return d[-2:] == f"{d1}{d2}"


def parse_br_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None
