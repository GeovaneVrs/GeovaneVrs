#!/usr/bin/env python3
"""Recorta as fontes OFL para o que os cards usam e grava WOFF em fonts/."""

import os
import sys

from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "fonts")

# ASCII, Latin-1 (acentos do português), travessão, aspas e setas.
UNICODES = []
UNICODES.extend(range(0x20, 0x7F))
UNICODES.extend(range(0xA0, 0x100))
UNICODES.extend([0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x2192, 0x2197])

SOURCES = {
    "serif-400.woff": "/tmp/geo/fonts/InstrumentSerif-Regular.ttf",
    "serif-italic.woff": "/tmp/geo/fonts/InstrumentSerif-Italic.ttf",
    "inter-400.woff": "/usr/share/fonts/truetype/macos/Inter-Regular.ttf",
    "inter-600.woff": "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf",
    "mono-400.woff": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
}

SAMPLE = (
    "Disponível Geovane Valerio Ciência Computação Jaboatão Guararapes "
    "soluções paixão papéis código → “” —"
)


def subset(src, dest):
    font = TTFont(src)
    options = Options()
    options.flavor = "woff"
    options.layout_features = ["kern", "liga", "calt"]
    options.desubroutinize = True
    options.name_IDs = ["*"]
    options.notdef_outline = True
    options.recommended_glyphs = True
    tool = Subsetter(options=options)
    tool.populate(unicodes=UNICODES)
    tool.subset(font)
    font.save(dest)
    cmap = set()
    for table in font["cmap"].tables:
        cmap.update(table.cmap)
    missing = [ch for ch in SAMPLE if ord(ch) not in cmap and not ch.isspace()]
    print(f"{os.path.basename(dest):22} {os.path.getsize(dest) // 1024:4} KB  missing={missing}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    missing_src = [p for p in SOURCES.values() if not os.path.exists(p)]
    if missing_src:
        sys.exit("fontes de origem ausentes:\n" + "\n".join(missing_src))
    for name, src in SOURCES.items():
        subset(src, os.path.join(OUT, name))
