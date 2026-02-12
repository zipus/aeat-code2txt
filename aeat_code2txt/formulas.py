from __future__ import annotations

import re
from decimal import Decimal
from typing import Mapping

TOKEN_RE = re.compile(r"\[(\d+)\]|[+-]")


def evaluate_formula(formula: str, values: Mapping[str, Decimal]) -> Decimal:
    """
    Evaluate a simple formula containing [NN] codes and + / - operators.
    """
    tokens = TOKEN_RE.findall(formula)
    # TOKEN_RE.findall returns only code captures; we need a full scan.
    parts = []
    idx = 0
    while idx < len(formula):
        match = TOKEN_RE.search(formula, idx)
        if not match:
            break
        if match.group(0) in ("+", "-"):
            parts.append(match.group(0))
        else:
            parts.append(match.group(1))
        idx = match.end()

    if not parts:
        return Decimal(0)

    total = Decimal(0)
    op = "+"
    for part in parts:
        if part in ("+", "-"):
            op = part
            continue
        value = values.get(part, Decimal(0))
        if op == "+":
            total += value
        else:
            total -= value
    return total
