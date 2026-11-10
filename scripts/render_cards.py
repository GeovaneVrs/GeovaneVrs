#!/usr/bin/env python3
"""Desenha os cards animados do README em cards/.

Cada arquivo é um SVG autossuficiente: o GitHub deixa passar a tag img, e dentro
dela funcionam CSS, SMIL e fontes embutidas. Não há JavaScript nem pedido externo.

STATIC=1 desenha o último quadro, sem animação, para conferir o layout.
"""

import base64
import json
import os
from html import escape

from stats import (
    best_day,
    contrib_label,
    data_curta,
    data_longa,
    dia_label,
    mes_curto,
    monthly,
    pt_int,
    streaks,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
STATIC = os.environ.get("STATIC") == "1"

W = 900
GAP = 12
SLOT = W / 3
BOTTOM = 14

PAPER = "#f4f3ef"
INK = "#161616"
INK_SOFT = "#3c3c40"
MUTED = "#6e6e73"
RULE = "#e4e1da"
BLUE = "#2f5bff"
BLUE_DEEP = "#1d3fbf"

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Inter, system-ui, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Inter", "normal", 400, "inter-400.woff"),
    "sans-b": ("Inter", "normal", 600, "inter-600.woff"),
    "mono": ("JetBrains Mono", "normal", 400, "mono-400.woff"),
}

BLUE_SCALE = ["#e7e9f2", "#c5d4ff", "#8aabff", "#3d6bff", "#1a3fd4"]

CSS = """
@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes pop { 0% { opacity: 0; transform: scale(.35); } 70% { opacity: 1; transform: scale(1.12); } 100% { opacity: 1; transform: none; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .28; } }
@keyframes nudge { 0%, 100% { transform: none; } 50% { transform: translateX(5px); } }
@keyframes swing {
  0% { opacity: 0; transform: translateY(64px) rotate(-6deg) scale(.94); }
  58% { opacity: 1; transform: translateY(-7px) rotate(1.4deg) scale(1.02); }
  100% { opacity: 1; transform: none; }
}
@keyframes sweep {
  0%, 58% { opacity: 0; transform: translateX(-80px) skewX(-18deg); }
  70% { opacity: .34; }
  88%, 100% { opacity: 0; transform: translateX(460px) skewX(-18deg); }
}
@keyframes ring {
  0% { opacity: .55; transform: scale(.4); }
  100% { opacity: 0; transform: scale(2.2); }
}
@keyframes blink { 0%, 45% { opacity: 1; } 50%, 100% { opacity: 0; } }
.rise { opacity: 0; animation: rise .7s cubic-bezier(.16,.8,.24,1) both; transform-box: fill-box; }
.fade { opacity: 0; animation: fade .8s ease-out both; }
.grow { transform-box: fill-box; transform-origin: bottom; transform: scaleY(0); animation: grow .75s cubic-bezier(.16,.84,.28,1) both; }
.pop { opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .42s ease-out both; }
.live { animation: pulse 1.7s ease-in-out infinite; }
.nudge { transform-box: fill-box; animation: nudge 1.7s ease-in-out infinite; }
.swing { opacity: 0; transform-box: fill-box; transform-origin: 50% 60%; animation: swing 1.05s cubic-bezier(.16,.84,.22,1) both; }
.sheen { opacity: 0; transform-box: fill-box; animation: sweep 6.4s ease-in-out infinite both; }
.ring { opacity: 0; transform-box: fill-box; transform-origin: center; animation: ring 1.15s ease-out both; }
.caret { animation: blink 1.05s steps(1) infinite; }
@media (prefers-reduced-motion: reduce) {
  .rise, .fade, .grow, .pop, .live, .nudge, .swing, .caret { animation: none !important; opacity: 1 !important; transform: none !important; }
  .sheen, .ring, .count-step { display: none !important; }
  .count-final { opacity: 1 !important; }
}
"""

_FONT_CSS = {}


def font_css(keys):
    cached = _FONT_CSS.get(tuple(keys))
    if cached:
        return cached
    faces = []
    for key in keys:
        family, style, weight, filename = FONT_FILES[key]
        raw = open(os.path.join(FONTS, filename), "rb").read()
        b64 = base64.b64encode(raw).decode()
        faces.append(
            "@font-face{"
            f"font-family:'{family}';font-style:{style};font-weight:{weight};"
            "font-display:block;"
            f"src:url(data:font/woff;base64,{b64}) format('woff');"
            "}"
        )
    _FONT_CSS[tuple(keys)] = "".join(faces)
    return _FONT_CSS[tuple(keys)]


def esc(value):
    return escape(str(value), quote=True)


def at(delay):
    return f'style="animation-delay:{delay:.2f}s"'


def svg(width, height, body, fonts, label, bottom=BOTTOM):
    css = font_css(fonts) + CSS
    if STATIC:
        css += (
            ".rise,.fade,.grow,.pop,.live,.nudge,.swing,.caret{animation:none!important;opacity:1!important;transform:none!important}"
            ".sheen,.ring,.count-step{display:none!important}.count-final{opacity:1!important}"
        )
    width_attr = round(width, 3)
    height_attr = round(height + bottom, 3)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_attr}" height="{height_attr}" '
        f'viewBox="0 0 {width_attr} {height_attr}" role="img" aria-label="{esc(label)}">\n'
        f"<title>{esc(label)}</title>\n"
        f"<style><![CDATA[{css}]]></style>\n"
        f"{body}\n</svg>\n"
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"cards/{name}  {len(content) // 1024} KB")


def third(index):
    """Caixa colorida dentro do terço, com 12px de respiro entre os cards."""
    if index == 0:
        return 0, SLOT - GAP / 2
    if index == 1:
        return GAP / 2, SLOT - GAP
    return GAP / 2, SLOT - GAP / 2


def count_up(number, x, y, size, fill, begin):
    """Conta de 0 até o inteiro. O valor final fica por baixo, para quem prefere menos movimento."""
    final = (
        f'<text class="count-final" x="{x}" y="{y}" font-family="{SERIF}" font-size="{size}" '
        f'fill="{fill}" opacity="0">{esc(number)}</text>'
    )
    if STATIC or not str(number).isdigit():
        return (
            f'<text x="{x}" y="{y}" font-family="{SERIF}" font-size="{size}" fill="{fill}">{esc(number)}</text>'
        )
    target = int(number)
    frames = list(range(target + 1))
    step = 0.16 if target <= 6 else 0.9 / max(target, 1)
    steps = []
    for i, value in enumerate(frames):
        on = begin + i * step
        off = f'<set attributeName="opacity" to="0" begin="{on + step:.2f}s"/>' if i < len(frames) - 1 else ""
        steps.append(
            f'<text class="count-step" x="{x}" y="{y}" font-family="{SERIF}" font-size="{size}" '
            f'fill="{fill}" opacity="0">{value}'
            f'<set attributeName="opacity" to="1" begin="{on:.2f}s"/>{off}</text>'
        )
    reveal = begin + len(frames) * step
    final = (
        f'<text class="count-final" x="{x}" y="{y}" font-family="{SERIF}" font-size="{size}" '
        f'fill="{fill}" opacity="0">{esc(number)}'
        f'<set attributeName="opacity" to="1" begin="{reveal:.2f}s"/></text>'
    )
    return "".join(steps) + final


def portrait_markup(origin_x, origin_y, box_h):
    path = os.path.join(ROOT, "data", "portrait.json")
    if not os.path.exists(path):
        return ""
    data = json.load(open(path, encoding="utf-8"))
    scale = box_h / data["height"]
    parts = []
    for index, row in enumerate(data["rows"]):
        circles = "".join(
            f'<circle cx="{origin_x + dot[0] * scale:.1f}" cy="{origin_y + dot[1] * scale:.1f}" '
            f'r="{max(0.35, dot[2] * scale):.2f}"/>'
            for dot in row
        )
        parts.append(f'<g class="fade" fill="{INK}" {at(0.18 + index * 0.011)}>{circles}</g>')
    return "".join(parts)


def hero(profile):
    h = 408
    bio = "".join(
        f'<text class="rise" {at(0.42 + i * 0.08)} x="48" y="{312 + i * 28}" '
        f'font-family="{SANS}" font-size="18" fill="{INK_SOFT}">{esc(line)}</text>'
        for i, line in enumerate(profile["bio"])
    )
    shine = INK if STATIC else "url(#shine)"
    shine_anim = "" if STATIC else (
        '<animateTransform attributeName="gradientTransform" type="translate" '
        'values="-160 0; 460 0; 460 0" keyTimes="0;0.28;1" dur="6s" begin="1.3s" repeatCount="indefinite"/>'
    )
    handle = profile["links"]["github"].replace("https://", "")
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="240" y2="0">
    <stop offset="0" stop-color="{INK}"/>
    <stop offset="0.4" stop-color="{INK}"/>
    <stop offset="0.5" stop-color="{BLUE}"/>
    <stop offset="0.6" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>
    {shine_anim}
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="28" fill="none" stroke="{RULE}"/>
  <rect class="live" x="48" y="52" width="9" height="9" rx="2" fill="{BLUE}"/>
  <text class="rise" {at(0.05)} x="66" y="61" font-family="{SANS}" font-size="13" letter-spacing="1.5" fill="{BLUE}">{esc(profile["eyebrow"].upper())}</text>
  <text class="rise" {at(0.12)} x="46" y="168" font-family="{SERIF}" font-size="104" fill="{INK}">{esc(profile["first"])}</text>
  <text class="rise" {at(0.24)} x="46" y="272" font-family="{SERIF}" font-style="italic" font-size="108" fill="{shine}">{esc(profile["last"])}</text>
  {bio}
  <text class="rise" {at(0.62)} x="48" y="378" font-family="{SANS}" font-size="15" fill="{BLUE}">{esc(handle)}  →</text>
  {portrait_markup(500, 36, 340)}
</g>
"""
    label = (
        f'{profile["first"]} {profile["last"]}. {profile["bio"][0]} '
        f'{profile["bio"][1]} {profile["eyebrow"]}.'
    )
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans"], label))


def tile(item, index):
    x, width = third(index)
    h = 228
    delay = 3.15 + index * 0.18
    lines = "".join(
        f'<text class="rise" {at(delay + 0.28 + i * 0.06)} x="{x + 22}" y="{168 + i * 22}" '
        f'font-family="{SANS}" font-size="15" fill="{item["fg"]}">{esc(line)}</text>'
        for i, line in enumerate(item["lines"])
    )
    size = 58 if len(item["number"]) <= 3 else 46
    number = count_up(item["number"], x + 22, 112, size, item["fg"], delay + 0.34)
    body = f"""
<defs>
  <clipPath id="card"><rect x="{x}" y="0" width="{width}" height="{h}" rx="22"/></clipPath>
</defs>
<g class="swing" {at(delay)}>
  <g clip-path="url(#card)">
    <rect x="{x}" y="0" width="{width}" height="{h}" rx="22" fill="{item["bg"]}"/>
    <rect class="sheen" {at(delay + 1.3)} x="{x - 80}" y="-30" width="64" height="{h + 60}" fill="{item.get("sheen", "#ffffff")}"/>
    <circle class="ring" {at(delay + 0.15)} cx="{x + width - 28}" cy="28" r="8" fill="none" stroke="{item["fg"]}" stroke-width="1.6"/>
    <text x="{x + 22}" y="40" font-family="{MONO}" font-size="13" letter-spacing="1.6" fill="{item["fg"]}">{esc(item["label"])}</text>
    <g class="nudge" {at(delay + 0.8)}>
      <path d="M{x + width - 40} 34 h14 M{x + width - 32} 28 l6 6 l-6 6" fill="none" stroke="{item["fg"]}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
    {number}
    <text x="{x + 22}" y="140" font-family="{SERIF}" font-style="italic" font-size="24" fill="{item["fg"]}">{esc(item["word"])}</text>
    {lines}
  </g>
</g>
"""
    write(f"{item['id']}.svg", svg(SLOT, h, body, ["serif", "serif-i", "sans", "mono"], item["alt"]))


def activity(data):
    h = 360
    months = data["months"]
    best = max(months, key=lambda m: (m["total"], m["month"]))
    top = max(best["total"], 1)
    x0, x1, base, max_h, gap = 32, 560, 300, 138, 8
    bw = (x1 - x0 - gap * (len(months) - 1)) / len(months)
    bars = []
    for i, month in enumerate(months):
        partial = i == len(months) - 1
        is_best = month is best and month["total"] > 0
        height = 6 if month["total"] == 0 else max(10, round(month["total"] / top * max_h))
        x = x0 + i * (bw + gap)
        if is_best:
            fill = BLUE
        elif partial:
            fill = "#c5d0ee"
        elif month["total"] == 0:
            fill = "#e6e8f0"
        else:
            fill = "#6d90ff"
        label = mes_curto(month["month"])
        bars.append(
            f'<g>'
            f'<title>{label}: {pt_int(month["total"])} {contrib_label(month["total"])}</title>'
            f'<rect class="grow" {at(2.15 + i * 0.05)} x="{x:.1f}" y="{base - height}" width="{bw:.1f}" height="{height}" rx="4" fill="{fill}"/>'
            f'<text x="{x + bw / 2:.1f}" y="{base + 20}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
            f'</g>'
        )
        if is_best:
            bars.append(
                f'<text class="pop" {at(2.7)} x="{x + bw / 2:.1f}" y="{base - height - 8}" text-anchor="middle" '
                f'font-family="{MONO}" font-size="12" fill="{BLUE}">{pt_int(month["total"])}</text>'
            )
    current = data["current_streak"]
    longest = data["longest_streak"]
    if current == 0:
        streak_note = "nenhum dia seguido agora"
    elif current >= longest:
        streak_note = f"{dia_label(current)} seguidos, a maior sequência"
    else:
        streak_note = f"{dia_label(current)} seguidos · maior {pt_int(longest)}"
    stats = [
        (pt_int(current), streak_note),
        (f'{pt_int(data["active_days"])} / {pt_int(data["span_days"])}', "dias com contribuição"),
        (pt_int(data["best_day"]["count"]), f'no dia mais cheio · {data_curta(data["best_day"]["date"])}'),
    ]
    side = []
    for i, (big, note) in enumerate(stats):
        y = 132 + i * 78
        side.append(
            f'<text class="rise" {at(2.25 + i * 0.08)} x="588" y="{y}" font-family="{SERIF}" font-size="34" fill="{INK}">{esc(big)}</text>'
            f'<text class="rise" {at(2.32 + i * 0.08)} x="588" y="{y + 22}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(note)}</text>'
        )
        if i < 2:
            side.append(f'<line x1="588" y1="{y + 40}" x2="868" y2="{y + 40}" stroke="{RULE}"/>')
    total = data["total"]
    body = f"""
<defs><clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath></defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="28" fill="none" stroke="{RULE}"/>
  <text class="rise" {at(1.95)} x="32" y="40" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{MUTED}">OS ÚLTIMOS 12 MESES</text>
  <text class="rise" {at(2.02)} x="32" y="82" font-family="{SERIF}" font-size="40" fill="{INK}">{pt_int(total)}</text>
  <text class="rise" {at(2.08)} x="128" y="82" font-family="{SERIF}" font-style="italic" font-size="24" fill="{INK_SOFT}">{contrib_label(total)}</text>
  {''.join(bars)}
  {''.join(side)}
</g>
"""
    label = f'{pt_int(total)} {contrib_label(total)} nos últimos 12 meses. Sequência de {current} {dia_label(current)}.'
    write("activity.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"], label))


def heatmap(data):
    days = data["days"]
    cell, step = 11, 14
    origin_x, origin_y = 44, 78
    cols = max(d["col"] for d in days) + 1
    cells = []
    seen = set()
    months = []
    for day in days:
        col, row = day["col"], day["row"]
        month_starts = col == 0 or (row == 0 and day["date"][8:10] <= "07")
        if month_starts and day["date"][:7] not in seen:
            seen.add(day["date"][:7])
            months.append((col, mes_curto(day["date"][:7])))
        level = day["level"] if day["count"] else 0
        color = BLUE_SCALE[min(level, len(BLUE_SCALE) - 1)]
        delay = 1.05 + col * 0.022 + row * 0.012
        count = day["count"]
        tip = f'{data_longa(day["date"])}: {pt_int(count)} {contrib_label(count)}'
        cells.append(
            f'<rect class="pop" {at(delay)} x="{origin_x + col * step}" y="{origin_y + row * step}" '
            f'width="{cell}" height="{cell}" rx="2" fill="{color}"><title>{esc(tip)}</title></rect>'
        )
    month_labels = []
    last_x = -999
    for col, name in months:
        x = origin_x + col * step
        if x - last_x < 32 or col > cols - 2:
            continue
        last_x = x
        month_labels.append(
            f'<text x="{x}" y="{origin_y - 8}" font-family="{MONO}" font-size="11" fill="{MUTED}">{name}</text>'
        )
    day_names = [(1, "seg"), (3, "qua"), (5, "sex")]
    day_labels = "".join(
        f'<text x="8" y="{origin_y + row * step + 9}" font-family="{MONO}" font-size="10" fill="{MUTED}">{name}</text>'
        for row, name in day_names
    )
    right = origin_x + cols * step
    legend_y = origin_y + 7 * step + 22
    legend = "".join(
        f'<rect x="{right - 118 + i * 16}" y="{legend_y - 9}" width="11" height="11" rx="2" fill="{color}"/>'
        for i, color in enumerate(BLUE_SCALE)
    )
    h = legend_y + 16
    total = data["total"]
    body = f"""
<defs><clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath></defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="28" fill="none" stroke="{RULE}"/>
  <text class="rise" {at(0.9)} x="32" y="42" font-family="{SERIF}" font-style="italic" font-size="28" fill="{INK}">Cada dia, em azul</text>
  <text class="fade" {at(1.0)} x="{W - 32}" y="40" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{MUTED}">ATUALIZADO TODO DIA</text>
  {day_labels}
  {''.join(month_labels)}
  {''.join(cells)}
  <text x="{right - 168}" y="{legend_y}" font-family="{MONO}" font-size="11" fill="{MUTED}">menos</text>
  {legend}
  <text x="{right - 28}" y="{legend_y}" font-family="{MONO}" font-size="11" fill="{MUTED}">mais</text>
</g>
"""
    label = f'Gráfico de contribuições em azul: {pt_int(total)} {contrib_label(total)} no último ano.'
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"], label))


def quote(profile):
    h = 118
    body = f"""
<defs>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="#8eb4ff"/>
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{h}" fill="{PAPER}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="28" fill="none" stroke="{RULE}"/>
  <rect class="fade" x="418" y="28" width="64" height="3" rx="1.5" fill="url(#edge)"/>
  <text class="rise" {at(4.35)} x="{W / 2}" y="78" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="24" fill="{INK}">“{esc(profile["quote"])}”</text>
</g>
"""
    write("quote.svg", svg(W, h, body, ["serif", "serif-i"], profile["quote"]))


def load():
    profile = json.load(open(os.path.join(ROOT, "profile.json"), encoding="utf-8"))
    path = os.path.join(ROOT, "data", "contributions.json")
    if not os.path.exists(path):
        raise SystemExit("falta data/contributions.json — rode scripts/fetch_contributions.py")
    raw = json.load(open(path, encoding="utf-8"))
    days = sorted(raw["days"], key=lambda d: d["date"])
    current, longest = streaks(days)
    busiest = best_day(days)
    summary = {
        "days": days,
        "months": monthly(days),
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "active_days": sum(1 for d in days if d["count"] > 0),
        "span_days": len(days),
        "best_day": busiest,
    }
    return profile, summary


def main():
    profile, summary = load()
    hero(profile)
    heatmap(summary)
    activity(summary)
    for index, item in enumerate(profile["tiles"]):
        tile(item, index)
    quote(profile)
    print(
        f'{summary["total"]} {contrib_label(summary["total"])}, '
        f'sequência {summary["current_streak"]}, '
        f'dia mais cheio {summary["best_day"]["date"]} ({summary["best_day"]["count"]})'
    )


if __name__ == "__main__":
    main()
