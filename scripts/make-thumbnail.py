#!/usr/bin/env python3
"""Build YouTube thumbnail collages from the deck's cover art.

Reads the 52 releases out of src/data/discography.json in the same
chronological order the deck presents them, pairs each with its jacket in
public/covers/, and renders 1280x720 (16:9) thumbnails.

    python3 scripts/make-thumbnail.py                 # all variants
    python3 scripts/make-thumbnail.py --variant split # just one

Output lands in youtube/ next to the upload description.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "public" / "covers"
DATA = ROOT / "src" / "data" / "discography.json"
OUT = ROOT / "youtube"

W, H = 1280, 720

FONT_SANS = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_HEAVY = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_SERIF = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"

BG = (9, 10, 17)
GOLD = (255, 197, 92)
WHITE = (255, 255, 255)

TITLE_JP = "岡村孝子"
TITLE_EN = "Takako Okamura"
KICKER = "1985 — 2019 · SOLO WORKS"
LINE2 = "全曲ダイジェスト"
LINE3 = "34 SINGLES + 18 ALBUMS"

HERO_ID = "1987-02-04-s-夢をあきらめないで"


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9\u3040-\u30ff\u4e00-\u9faf]+", "-", s.lower())
    return s.strip("-")[:40] or "release"


def deck_order() -> list[dict]:
    """Flatten discography.json the way src/lib/slides.ts does."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    flat: list[tuple[str, str, int, dict]] = []
    for yi, year in enumerate(data["years"]):
        for si, s in enumerate(year.get("singles", [])):
            flat.append(("single", s.get("date") or str(year["year"]), yi * 100 + si, s))
        for ai, a in enumerate(year.get("albums", [])):
            flat.append(("album", a.get("date") or str(year["year"]), yi * 100 + 50 + ai, a))
    flat.sort(key=lambda r: (r[1], r[2]))

    out = []
    for kind, date, _, o in flat:
        sid = f"{date}-{'s' if kind == 'single' else 'a'}-{slug(o['title'])}"
        hits = glob.glob(str(COVERS / f"{glob.escape(sid)}.*"))
        if not hits:
            raise SystemExit(f"no cover art for slide {sid} ({o['title']})")
        out.append({"id": sid, "kind": kind, "date": date, "title": o["title"], "path": hits[0]})
    return out


def load(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def contain(im: Image.Image, w: int, h: int) -> Image.Image:
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def blurred_fill(im: Image.Image, w: int, h: int, *, darken=0.5, blur=7) -> Image.Image:
    """Cover-fit crop of `im`, blurred and dimmed — the backdrop behind a tile."""
    r = max(w / im.width, h / im.height)
    big = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    x = (big.width - w) // 2
    y = (big.height - h) // 2
    tile = big.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(tile).enhance(darken)


def draw_tile(base: Image.Image, im: Image.Image, box: tuple[int, int, int, int], *, pad=2) -> None:
    x0, y0, x1, y1 = box
    tw, th = x1 - x0 - 2 * pad, y1 - y0 - 2 * pad
    if tw < 4 or th < 4:
        return
    base.paste(blurred_fill(im, tw, th), (x0 + pad, y0 + pad))
    art = contain(im, tw, th)
    ax = x0 + pad + (tw - art.width) // 2
    ay = y0 + pad + (th - art.height) // 2
    base.paste(art, (ax, ay))
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([ax, ay, ax + art.width - 1, ay + art.height - 1], outline=(255, 255, 255, 46))


def square_mosaic(items: list[dict], region: tuple[int, int, int, int], cols: int, rows: int) -> Image.Image:
    """Even grid of square-ish cells; a short final row is centred."""
    x0, y0, x1, y1 = region
    rw, rh = x1 - x0, y1 - y0
    cw, ch = rw / cols, rh / rows
    out = Image.new("RGB", (rw, rh), BG)
    for i, it in enumerate(items):
        row, col = divmod(i, cols)
        in_row = min(cols, len(items) - row * cols)
        offset = (cols - in_row) / 2
        cx = (col + offset) * cw
        draw_tile(out, load(it["path"]), (round(cx), round(row * ch), round(cx + cw), round((row + 1) * ch)))
    return out


def prepare(items: list[dict]) -> None:
    for it in items:
        im = load(it["path"])
        it["_im"] = im
        it["_ar"] = im.width / im.height


def justified_mosaic(items: list[dict], w: int, h: int, gap: int = 3) -> Image.Image:
    """Contact-sheet layout: items run in order across rows that each span the
    full width, with rows as evenly sized as the count allows.

    Row heights follow from how many jackets land in each row, so the row count
    that brings the stack closest to `h` is chosen, then everything is scaled
    the rest of the way.
    """
    prepare(items)
    n = len(items)

    best = None
    for rows_n in range(2, 16):
        base, extra = divmod(n, rows_n)
        sizes = [base + (1 if i < extra else 0) for i in range(rows_n)]
        if min(sizes) < 3:
            continue
        rows, i = [], 0
        for s in sizes:
            rows.append(items[i : i + s])
            i += s
        heights = [(w - gap * (len(r) - 1)) / sum(x["_ar"] for x in r) for r in rows]
        total = sum(heights) + gap * (rows_n - 1)
        if best is None or abs(total - h) < best[0]:
            best = (abs(total - h), rows, heights, total)
    if best is None:
        raise SystemExit(f"cannot lay out {n} covers")
    _, rows, heights, total = best

    k = (h - gap * (len(rows) - 1)) / (total - gap * (len(rows) - 1))
    heights = [x * k for x in heights]

    out = Image.new("RGB", (w, h), BG)
    y = 0.0
    for row, rh in zip(rows, heights):
        row_w = sum(it["_ar"] * rh for it in row) + gap * (len(row) - 1)
        x = (w - row_w) / 2
        for it in row:
            tw = it["_ar"] * rh
            draw_tile(out, it["_im"], (round(x), round(y), round(x + tw), round(y + rh)), pad=0)
            x += tw + gap
        y += rh + gap
    return out


def scrim(size: tuple[int, int], axis: str, a: float, b: float, alpha: float = 255, color=BG) -> Image.Image:
    """Linear alpha ramp: opaque at `b`, transparent at `a`.

    Pass a > b to have the scrim strongest at the low-coordinate end.
    """
    w, h = size
    if axis == "h":
        t = np.clip((np.arange(w) - a) / (b - a if b != a else 1e-6), 0, 1)[None, :]
    else:
        t = np.clip((np.arange(h) - a) / (b - a if b != a else 1e-6), 0, 1)[:, None]
    t = np.broadcast_to(t, (h, w))
    layer = Image.new("RGBA", size, color + (0,))
    layer.putalpha(Image.fromarray((t * alpha).astype(np.uint8)))
    return layer


def flat(size: tuple[int, int], alpha: float, color=BG) -> Image.Image:
    """A uniform translucent wash, for knocking a busy collage back."""
    layer = Image.new("RGBA", size, color + (0,))
    layer.putalpha(Image.new("L", size, int(alpha)))
    return layer


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, index=index)


def tracked(d: ImageDraw.ImageDraw, xy, text, f, fill, tracking=0.0, anchor="la"):
    """Draw text with letter-spacing (PIL has none)."""
    if tracking == 0:
        d.text(xy, text, font=f, fill=fill, anchor=anchor)
        return
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += cw + tracking


def vignette(im: Image.Image, strength=0.42) -> Image.Image:
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    m = np.clip(r / 1.45, 0, 1) ** 2 * strength
    out = np.asarray(im).astype(np.float32) * (1 - m[..., None])
    return Image.fromarray(out.astype(np.uint8))


def enrich(im: Image.Image, sat=1.12, con=1.05) -> Image.Image:
    im = ImageEnhance.Color(im).enhance(sat)
    return ImageEnhance.Contrast(im).enhance(con)


# ---------------------------------------------------------------- variants


def variant_split(items: list[dict]) -> Image.Image:
    """Dark text panel on the left, 8x7 jacket mosaic on the right."""
    panel_w = 470
    base = Image.new("RGB", (W, H), BG)
    base.paste(enrich(square_mosaic(items, (panel_w, 0, W, H), cols=8, rows=7)), (panel_w, 0))
    base = Image.alpha_composite(base.convert("RGBA"), scrim((W, H), "h", panel_w + 160, panel_w - 40)).convert("RGB")

    d = ImageDraw.Draw(base, "RGBA")
    x = 52
    tracked(d, (x, 74), KICKER, font(FONT_SANS, 21), GOLD, tracking=3.4)
    d.text((x, 120), TITLE_JP, font=font(FONT_HEAVY, 100), fill=WHITE)
    d.text((x, 244), TITLE_EN, font=font(FONT_SANS, 33), fill=(196, 205, 226))
    d.rectangle([x, 298, x + 92, 304], fill=GOLD)
    d.text((x, 332), LINE2, font=font(FONT_SERIF, 52, index=2), fill=GOLD)
    tracked(d, (x, 418), LINE3, font(FONT_SANS, 22), (206, 214, 234), tracking=1.6)
    return vignette(base, 0.3)


def variant_wall(items: list[dict]) -> Image.Image:
    """Full-bleed contact sheet of all 52 jackets with a bottom scrim."""
    base = enrich(justified_mosaic(items, W, H), 1.08, 0.98)
    base = Image.alpha_composite(base.convert("RGBA"), scrim((W, H), "v", H * 0.32, H + 1, alpha=246))
    base = Image.alpha_composite(base, scrim((W, H), "v", H * 0.16, 0, alpha=120))
    base = Image.alpha_composite(base, scrim((W, H), "h", W * 0.44, 0, alpha=130)).convert("RGB")

    d = ImageDraw.Draw(base, "RGBA")
    x = 58
    tracked(d, (x, H - 262), KICKER, font(FONT_SANS, 21), GOLD, tracking=3.4)
    d.text((x, H - 216), TITLE_JP, font=font(FONT_HEAVY, 96), fill=WHITE)
    d.text((x, H - 92), LINE2, font=font(FONT_SERIF, 46, index=2), fill=GOLD)
    tracked(d, (x + 386, H - 76), LINE3, font(FONT_SANS, 22), (214, 221, 238), tracking=1.6)
    return vignette(base, 0.34)


def variant_hero(items: list[dict]) -> Image.Image:
    """One big signature jacket on the left, the rest as a mosaic behind it."""
    base = enrich(justified_mosaic(items, W, H), 1.05, 0.96)
    base = Image.alpha_composite(base.convert("RGBA"), flat((W, H), 104))
    base = Image.alpha_composite(base, scrim((W, H), "v", H * 0.30, H, alpha=196))
    base = Image.alpha_composite(base, scrim((W, H), "h", W * 0.66, W * 0.30, alpha=170)).convert("RGB")

    hero = next((i for i in items if i["id"] == HERO_ID), items[0])
    art = contain(load(hero["path"]), 400, 400)
    hx, hy = 76, (H - art.height) // 2 - 14
    d = ImageDraw.Draw(base, "RGBA")
    d.rectangle([hx - 10, hy - 10, hx + art.width + 10, hy + art.height + 10], fill=(6, 7, 12, 236), outline=GOLD + (170,), width=2)
    base.paste(art, (hx, hy))

    x = hx + art.width + 54
    tracked(d, (x, hy + 40), KICKER, font(FONT_SANS, 21), GOLD, tracking=3.4)
    d.text((x, hy + 84), TITLE_JP, font=font(FONT_HEAVY, 92), fill=WHITE)
    d.text((x, hy + 204), TITLE_EN, font=font(FONT_SANS, 32), fill=(200, 209, 229))
    d.rectangle([x, hy + 258, x + 88, hy + 264], fill=GOLD)
    d.text((x, hy + 292), LINE2, font=font(FONT_SERIF, 52, index=2), fill=GOLD)
    tracked(d, (x, hy + 374), LINE3, font(FONT_SANS, 22), fill=(206, 214, 234), tracking=1.6)
    return vignette(base, 0.3)


VARIANTS = {"split": variant_split, "wall": variant_wall, "hero": variant_hero}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=[*VARIANTS, "all"], default="all")
    args = ap.parse_args()

    items = deck_order()
    OUT.mkdir(exist_ok=True)
    todo = list(VARIANTS) if args.variant == "all" else [args.variant]

    print(f"{len(items)} covers -> {len(todo)} thumbnail(s)")
    for name in todo:
        im = VARIANTS[name](items)
        assert im.size == (W, H), im.size
        png = OUT / f"thumbnail-{name}.png"
        jpg = OUT / f"thumbnail-{name}.jpg"
        im.save(png, optimize=True)
        im.save(jpg, quality=92, subsampling=1, optimize=True)
        print(f"  {png.relative_to(ROOT)}  {png.stat().st_size/1e6:.2f} MB")
        print(f"  {jpg.relative_to(ROOT)}  {jpg.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
