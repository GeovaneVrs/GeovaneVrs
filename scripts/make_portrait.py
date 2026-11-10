#!/usr/bin/env python3
"""Transforma a foto do GitHub num retrato pontilhado e grava data/portrait.json.

Baixa o avatar público, recorta cabeça e ombros e guarda só os pontos.
O render dos cards não precisa da foto nem desta dependência: ele lê o JSON.

Dependências locais, fora da Action diária: pillow e rembg.
"""

import json
import os
import sys
import urllib.request

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "portrait.json")
PROFILE = os.path.join(ROOT, "profile.json")

# Recorte estável da foto atual (cabeça e colarinho), em pixels do avatar 460.
CROP = (164, 70, 298, 196)
STEP = 2.65
TARGET_H = 360


def avatar_path():
    profile = json.load(open(PROFILE, encoding="utf-8"))
    user_id = profile.get("avatar_id", 128635065)
    dest = os.path.join(ROOT, "data", "avatar.jpg")
    url = f"https://avatars.githubusercontent.com/u/{user_id}?s=460"
    request = urllib.request.Request(url, headers={"User-Agent": "profile-cards"})
    with urllib.request.urlopen(request, timeout=30) as response:
        open(dest, "wb").write(response.read())
    return dest


def cutout(path):
    from rembg import remove

    image = Image.open(path).convert("RGBA")
    return remove(image)


def dots_from(image):
    crop = image.crop(CROP)
    scale = TARGET_H / crop.height
    size = (max(1, int(crop.width * scale)), TARGET_H)
    crop = crop.resize(size, Image.Resampling.LANCZOS)
    gray = ImageEnhance.Contrast(crop.convert("RGB")).enhance(1.15).convert("L")
    alpha = crop.split()[-1]
    width, height = gray.size
    rows = []
    y = 1.0
    j = 0
    while y < height - 1:
        row = []
        x = 1.0
        i = 0
        while x < width - 1:
            xi, yi = int(x), int(y)
            lum = gray.getpixel((xi, yi))
            al = alpha.getpixel((xi, yi))
            darkness = 1 - (lum / 255) ** 0.72
            fade = 1.0
            if y > height * 0.78:
                fade = max(0.0, 1 - (y - height * 0.78) / (height * 0.22))
            if al > 110 and darkness > 0.13 and fade > 0.05:
                radius = (0.34 + 0.58 * darkness) * fade
                n = ((i * 73856093) ^ (j * 19349663)) & 1023
                jx = (n / 1023 - 0.5) * 1.15
                jy = (((n * 13) & 1023) / 1023 - 0.5) * 1.15
                row.append([round(x + jx, 2), round(y + jy, 2), round(radius, 2)])
            x += STEP
            i += 1
        if row:
            rows.append(row)
        y += STEP
        j += 1
    return {"width": width, "height": height, "rows": rows}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else avatar_path()
    portrait = dots_from(cutout(path))
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(portrait, handle, separators=(",", ":"))
        handle.write("\n")
    count = sum(len(row) for row in portrait["rows"])
    print(f"data/portrait.json  {count} pontos em {len(portrait['rows'])} linhas")


if __name__ == "__main__":
    main()
