#!/usr/bin/env python3
"""Contas puras em cima do calendário de contribuições."""

import datetime
from collections import defaultdict

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
MESES_CURTOS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def parse_count(tooltip):
    """Lê o texto do calendário do GitHub. 'No contributions…' vale 0."""
    text = " ".join(tooltip.split())
    lowered = text.lower()
    if lowered.startswith("no contribution"):
        return 0
    digits = []
    for token in text.split():
        if token.isdigit():
            digits.append(int(token))
            break
    if not digits or "contribution" not in lowered:
        raise ValueError(f"tooltip sem contagem: {text!r}")
    return digits[0]


def streaks(days):
    """Retorna (sequência atual, maior sequência).

    A sequência atual termina no último dia com contribuição. Um zero no fim
    (hoje ainda sem commit) não zera a sequência de ontem.
    """
    counts = [d["count"] for d in days]
    longest = run = 0
    for count in counts:
        if count > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    index = len(counts) - 1
    if index >= 0 and counts[index] == 0:
        index -= 1
    current = 0
    while index >= 0 and counts[index] > 0:
        current += 1
        index -= 1
    return current, longest


def month_keys(last_iso, n=12):
    year, month, _day = (int(p) for p in last_iso.split("-"))
    keys = []
    for _ in range(n):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    keys.reverse()
    return keys


def monthly(days, n=12):
    if not days:
        return []
    totals = defaultdict(int)
    for day in days:
        totals[day["date"][:7]] += day["count"]
    return [{"month": key, "total": totals[key]} for key in month_keys(days[-1]["date"], n)]


def best_day(days):
    positive = [d for d in days if d["count"] > 0]
    if not positive:
        return {"date": days[-1]["date"] if days else "", "count": 0}
    return max(positive, key=lambda d: (d["count"], d["date"]))


def data_curta(iso):
    _year, month, day = (int(p) for p in iso.split("-"))
    return f"{day} de {MESES[month - 1]}"


def data_longa(iso):
    year, month, day = (int(p) for p in iso.split("-"))
    return f"{day} de {MESES[month - 1]} de {year}"


def mes_curto(key):
    month = int(key.split("-")[1])
    return MESES_CURTOS[month - 1]


def contrib_label(n):
    return "contribuição" if n == 1 else "contribuições"


def dia_label(n):
    return "dia" if n == 1 else "dias"


def pt_int(n):
    return f"{n:,}".replace(",", ".")
