# -*- coding: utf-8 -*-
"""Generate app.ico from icon_source.png (user-provided purple M icon).

If icon_source.png is missing, falls back to drawing a generic purple M icon.
"""
import os
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "icon_source.png")
OUT = os.path.join(BASE_DIR, "app_icon.ico")
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
PRIMARY = (124, 58, 237)   # #7c3aed
WHITE = (255, 255, 255)


def _draw_fallback_m(draw, size):
    """Draw a bold blocky 'M' that fills most of the icon."""
    margin = int(size * 0.22)
    top = margin
    bottom = size - margin
    left = margin
    right = size - margin
    mid_x = size // 2
    mid_y = int(size * 0.58)
    stem = max(2, int(size * 0.12))
    draw.rectangle([left, top, left + stem, bottom], fill=WHITE)
    draw.rectangle([right - stem, top, right, bottom], fill=WHITE)
    for i in range(mid_x - left - stem):
        y = top + i * (mid_y - top) // (mid_x - left - stem)
        draw.rectangle([left + i, y, left + i + stem, y + stem], fill=WHITE)
    for i in range(right - stem - mid_x):
        y = mid_y + i * (bottom - mid_y) // (right - stem - mid_x)
        draw.rectangle([mid_x + i, y, mid_x + i + stem, y + stem], fill=WHITE)
    draw.rectangle([mid_x - stem // 2, mid_y, mid_x + stem // 2, bottom], fill=WHITE)


def _build_fallback(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size, size), radius=size // 5, fill=PRIMARY)
    _draw_fallback_m(draw, size)
    return img


def make_icon():
    if os.path.isfile(SRC):
        im = Image.open(SRC).convert("RGBA")
        w, h = im.size
        # Use a corner sample as the pad color so non-square sources stay seamless
        bg = im.getpixel((2, 2))
        size = max(w, h)
        square = Image.new("RGBA", (size, size), bg)
        offset = ((size - w) // 2, (size - h) // 2)
        square.paste(im, offset, im)
        square.save(OUT, format="ICO", sizes=SIZES)
    else:
        frames = [_build_fallback(s[0]) for s in SIZES]
        frames[0].save(OUT, format="ICO", sizes=SIZES)
    print(f"Created icon: {OUT}")


if __name__ == "__main__":
    make_icon()
