#!/usr/bin/env python3
"""Baixa o calendário público de contribuições e grava data/contributions.json.

Não precisa de token. O GitHub publica o mesmo quadro do perfil em
https://github.com/users/<user>/contributions
"""

import datetime
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stats import parse_count  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "contributions.json")
PROFILE = os.path.join(ROOT, "profile.json")

TD_RE = re.compile(r"<td\b[^>]*\bdata-date=\"[^\"]+\"[^>]*>", re.I)
TIP_RE = re.compile(
    r"<tool-tip\b[^>]*\bfor=\"(contribution-day-component-\d+-\d+)\"[^>]*>(.*?)</tool-tip>",
    re.I | re.S,
)
TOTAL_RE = re.compile(r"([\d,]+)\s+contributions\s+in the last year", re.I)


def fetch_html(username):
    url = f"https://github.com/users/{username}/contributions"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; profile-cards/1.0)",
            "Accept": "text/html",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def parse_calendar(html):
    tips = {}
    for match in TIP_RE.finditer(html):
        tips[match.group(1)] = re.sub(r"\s+", " ", match.group(2)).strip()

    days = []
    for td in TD_RE.findall(html):
        date = re.search(r'data-date="([^"]+)"', td).group(1)
        level = int(re.search(r'data-level="(\d)"', td).group(1))
        ident = re.search(r'id="(contribution-day-component-\d+-\d+)"', td).group(1)
        row_s, col_s = ident.rsplit("-", 2)[-2:]
        tooltip = tips.get(ident, "")
        count = parse_count(tooltip) if tooltip else 0
        days.append(
            {
                "date": date,
                "count": count,
                "level": level,
                "row": int(row_s),
                "col": int(col_s),
            }
        )
    days.sort(key=lambda d: d["date"])
    reported = None
    found = TOTAL_RE.search(html)
    if found:
        reported = int(found.group(1).replace(",", ""))
    return days, reported


def main():
    profile = json.load(open(PROFILE, encoding="utf-8"))
    username = profile["username"]
    html = fetch_html(username)
    days, reported = parse_calendar(html)
    if len(days) < 300:
        sys.exit(f"calendário curto demais ({len(days)} dias); nada foi gravado")
    payload = {
        "username": username,
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_reported": reported,
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    total = sum(d["count"] for d in days)
    print(f"gravei {len(days)} dias, {total} contribuições (GitHub informa {reported})")


if __name__ == "__main__":
    main()
