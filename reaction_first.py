#!/usr/bin/env python3
"""Vertical Clipper Kit — overlay VARIAN REACTION-FIRST.

Dipakai KHUSUS untuk momen reaksi streamer (kaget / rage / sedih /
jumpscare): wajah/reaksi tampil besar lebih dulu, gameplay menyusul.
Untuk momen detail / easter egg, pakai overlay format standar (overlay.py).

Layout 1080x1920, latar video hitam:
  - y 0-640     : facecam streamer (crop inset sumber, diperbesar
                  full-width dengan pola cover)
  - y 640-880   : band warna solid + hook font display putih outline
                  hitam, RATA KIRI (maks. 2-3 baris pendek)
  - y 880-1760  : gameplay (crop yang membuang inset facecam), cover
  - y 1760-1920 : band hitam + footer putih di tengah

Skrip ini hanya membuat PNG overlay-nya (band + hook + footer). Komposisi
video dilakukan dengan ffmpeg; sesuaikan crop facecam & gameplay dengan
sumbermu. Pola resep ffmpeg (ganti <...> sesuai sumber):

  ffmpeg -ss <start> -i <src> -f lavfi -i color=c=black:s=1080x1920:r=30:d=<dur> \
    -loop 1 -framerate 30 -i overlay-reaction.png \
    -filter_complex "[0:v]fps=30,split=2[b1][b2];
      [b1]crop=<face>,scale=1080:731,crop=1080:640:0:55[face];
      [b2]crop=<game>,scale=1253:880,crop=1080:880:86:0[game];
      [1:v][face]overlay=0:0[c1];[c1][game]overlay=0:880[c2];
      [c2][2:v]overlay=0:0,format=yuv420p[out]" \
    -map "[out]" -map 0:a -t <dur> -c:v libx264 -profile:v high \
    -preset veryfast -crf 20 -c:a aac -b:a 128k -movflags +faststart <out>.mp4

Sebelum posting, jalankan QC di QC_CHECKLIST.md (ffprobe h264 High /
yuv420p / faststart + cek frame final).

Contoh:
  python3 reaction_first.py overlay-reaction.png "DIA MENJERIT" "SEPERTI INI?!"
"""
import argparse
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

KIT_DIR = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BAND_Y, BAND_H = 640, 240
FOOTER_BAND_Y = 1760


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


def make_overlay(cfg, hook_lines, out_path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    band = hex2rgb(getattr(cfg, "BAND_COLOR", cfg.BACKGROUND_COLOR)) + (255,)
    d.rectangle((0, BAND_Y, W, BAND_Y + BAND_H), fill=band)
    d.rectangle((0, BAND_Y, W, BAND_Y + 6), fill=(0, 0, 0, 255))
    d.rectangle((0, BAND_Y + BAND_H - 6, W, BAND_Y + BAND_H), fill=(0, 0, 0, 255))
    fill = hex2rgb(cfg.HOOK_TEXT_COLOR) + (255,)
    outline = hex2rgb(cfg.HOOK_OUTLINE_COLOR) + (255,)
    f = get_font(cfg, "DISPLAY_FONT", 64)
    line_h = 80
    y = BAND_Y + (BAND_H - line_h * len(hook_lines)) // 2
    for line in hook_lines:
        d.text((40, y + 5), line, font=f, fill=outline)  # bayangan
        d.text((36, y), line, font=f, fill=fill, stroke_width=3, stroke_fill=outline)
        y += line_h
    f_foot = get_font(cfg, "FOOTER_FONT", 36)
    tw = d.textlength(cfg.FOOTER_TEXT, font=f_foot)
    d.text(((W - tw) / 2, 1822), cfg.FOOTER_TEXT, font=f_foot, fill=(255, 255, 255, 255))
    img.save(out_path)
    print("saved", out_path)


def main():
    ap = argparse.ArgumentParser(
        description="Buat overlay reaction-first 1080x1920 (band hook + footer).")
    ap.add_argument("out", help="Path PNG hasil")
    ap.add_argument("hook", nargs="+", help="Baris-baris hook (1-3 baris pendek)")
    ap.add_argument("--config", default=os.path.join(KIT_DIR, "config.py"),
                    help="Path file config (default: config.py di folder kit)")
    args = ap.parse_args()

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(KIT_DIR, "config.example.py")
        print(f"Config tidak ditemukan, memakai contoh: {cfg_path}", file=sys.stderr)
    cfg = load_config(cfg_path)
    make_overlay(cfg, args.hook, args.out)


if __name__ == "__main__":
    main()
