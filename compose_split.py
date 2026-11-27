#!/usr/bin/env python3
"""Vertical Clipper Kit — komposisi SPLIT (pratinjau satu frame).

Alternatif layout: satu frame sumber landscape (mis. 1280x720 dari
livestream) disusun menjadi komposisi vertikal 1080x1920:

  - Band header (0-205)      : warna latar + logo (opsional) + nama channel
  - Band facecam (205-855)   : crop kotak facecam sumber, cover full-width
  - Band gameplay (855-1505) : crop gameplay (inset facecam dibuang), cover
  - Band bawah (1505-1920)   : warna latar + footer + hook di bawahnya

Kotak crop sumber (CAM_BOX / GAME_BOX di bawah) adalah contoh untuk
sumber 1280x720 dengan facecam di kiri-bawah — WAJIB disesuaikan dengan
tiap sumber: buka satu frame sumber, ukur posisi facecam-nya, ubah angka
di sini. Berguna sebagai pratinjau cepat sebelum komposisi video penuh.

Contoh:
  python3 compose_split.py frame-sumber.jpg "HOOK KAMU" preview.png
"""
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

KIT_DIR = os.path.dirname(os.path.abspath(__file__))

TOP_H = 205                 # band header
CAM_Y, CAM_H = 205, 650     # band facecam
GAME_Y, GAME_H = 855, 650   # band gameplay
# Contoh untuk sumber 1280x720, facecam kiri-bawah approx (0,255)-(265,470)
CAM_BOX = (0, 255, 265, 470)
# Gameplay: buang inset kiri -> crop (270,56)-(1280,664)
GAME_BOX = (270, 56, 1280, 664)


def load_config(path):
    spec = importlib.util.spec_from_file_location("clipper_config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def resolve(cfg, p):
    if not p:
        return ""
    if os.path.isabs(p):
        return p
    return os.path.join(KIT_DIR, p)


def get_font(cfg, which, size):
    p = resolve(cfg, getattr(cfg, which, ""))
    if p and os.path.exists(p):
        return ImageFont.truetype(p, size)
    # fallback: font display terbundel (tetap terbaca), lalu font bawaan
    dp = resolve(cfg, getattr(cfg, "DISPLAY_FONT", ""))
    if dp and os.path.exists(dp):
        return ImageFont.truetype(dp, size)
    return ImageFont.load_default()


def fill(img, box, tw, th):
    """Crop kotak lalu skala cover ke ukuran target."""
    c = img.crop(box)
    s = max(tw / c.width, th / c.height)
    c = c.resize((round(c.width * s), round(c.height * s)))
    x = (c.width - tw) // 2
    y = (c.height - th) // 2
    return c.crop((x, y, x + tw, y + th))


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def compose(cfg, frame_path, hook, out_path):
    W, H = cfg.CANVAS_W, cfg.CANVAS_H
    bg = hex2rgb(cfg.BACKGROUND_COLOR)
    src = Image.open(frame_path).convert("RGB")
    canvas = Image.new("RGB", (W, H), bg)
    canvas.paste(fill(src, CAM_BOX, W, CAM_H), (0, CAM_Y))
    canvas.paste(fill(src, GAME_BOX, W, GAME_H), (0, GAME_Y))
    d = ImageDraw.Draw(canvas)
    ink = (0, 0, 0)
    text_x = 48
    logo_path = resolve(cfg, getattr(cfg, "LOGO_PATH", ""))
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA").resize((76, 76))
        canvas.paste(logo, (48, 92), logo)
        text_x = 140
    f_brand = get_font(cfg, "DISPLAY_FONT", 46)
    d.text((text_x, 106), cfg.CHANNEL_NAME, font=f_brand, fill=ink)
    x0 = text_x + d.textlength(cfg.CHANNEL_NAME, font=f_brand) + 26
    d.line([(x0, 132), (W - 56, 132)], fill=ink, width=3)
    f_foot = get_font(cfg, "FOOTER_FONT", 38)
    tw = d.textlength(cfg.FOOTER_TEXT, font=f_foot)
    d.text(((W - tw) / 2, 1530), cfg.FOOTER_TEXT, font=f_foot, fill=ink)
    f_hook = get_font(cfg, "DISPLAY_FONT", 60)
    fill_c = hex2rgb(cfg.HOOK_TEXT_COLOR)
    outline_c = hex2rgb(cfg.HOOK_OUTLINE_COLOR)
    y = 1615
    for line in wrap(d, hook, f_hook, W - 64):
        d.text((36, y + 4), line, font=f_hook, fill=outline_c)
        d.text((32, y), line, font=f_hook, fill=fill_c,
               stroke_width=2, stroke_fill=outline_c)
        y += 76
    canvas.save(out_path)
    print("saved", out_path)


def main():
    if len(sys.argv) < 4:
        print("usage: compose_split.py <frame.jpg> <hook> <out.png> [config.py]",
              file=sys.stderr)
        sys.exit(2)
    cfg_path = sys.argv[4] if len(sys.argv) > 4 else os.path.join(KIT_DIR, "config.py")
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(KIT_DIR, "config.example.py")
        print(f"Config tidak ditemukan, memakai contoh: {cfg_path}", file=sys.stderr)
    cfg = load_config(cfg_path)
    compose(cfg, sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
