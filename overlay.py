#!/usr/bin/env python3
"""Vertical Clipper Kit — overlay format standar (v4).

Menghasilkan overlay PNG 1080x1920 untuk klip vertikal 9:16:

  - Header: logo (opsional) + nama channel + garis pemisah, tepat di atas
    area gameplay.
  - Area gameplay (y=GAMEPLAY_Y, tinggi GAMEPLAY_H): dibiarkan TRANSPARAN
    pada mode overlay (default), atau diisi warna latar pada mode kanvas.
  - Hook: teks besar font display, putih dengan outline hitam + bayangan
    halus, tepat di bawah area gameplay. Hook adalah teks pertama yang
    dibaca penonton — buat singkat dan jelas.
  - Footer: teks sosial media di dekat bagian bawah.

Dua mode:
  --mode overlay  (default) PNG transparan, tinggal ditumpuk di atas video
                  dengan ffmpeg. Latar di belakang gameplay tidak digambar;
                  warnai latar videomu sesuai BACKGROUND_COLOR di config.
  --mode canvas   Kanvas penuh berwarna BACKGROUND_COLOR + satu frame
                  gameplay ditempel (untuk pratinjau / thumbnail diam).

Semua identitas (nama channel, warna, footer, font, logo) dibaca dari
file config — lihat config.example.py.

Contoh:
  python3 overlay.py --hook "DIA MELOMPAT DARI JET!" --out overlay.png
  python3 overlay.py --mode canvas --frame frame.jpg --hook "GILA!" --out preview.png
"""
import argparse
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

KIT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(path):
    spec = importlib.util.spec_from_file_location("clipper_config", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def resolve(cfg, p):
    """Path relatif di config diartikan relatif terhadap file config."""
    if not p:
        return ""
    if os.path.isabs(p):
        return p
    return os.path.join(KIT_DIR, p)


def font(cfg, which, size):
    p = resolve(cfg, getattr(cfg, which, ""))
    if p and os.path.exists(p):
        return ImageFont.truetype(p, size)
    # fallback: font display terbundel (tetap terbaca), lalu font bawaan
    dp = resolve(cfg, getattr(cfg, "DISPLAY_FONT", ""))
    if dp and os.path.exists(dp):
        return ImageFont.truetype(dp, size)
    return ImageFont.load_default()


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


def draw_header(d, canvas, cfg, text_fill):
    """Logo + nama channel + garis. Menggambar di canvas & draw context."""
    W = cfg.CANVAS_W
    gy = cfg.GAMEPLAY_Y
    logo_path = resolve(cfg, getattr(cfg, "LOGO_PATH", ""))
    text_x = 56
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA").resize((88, 88))
        canvas.paste(logo, (56, gy - 104), logo)
        text_x = 160
    f_brand = font(cfg, "DISPLAY_FONT", 50)
    d.text((text_x, gy - 92), cfg.CHANNEL_NAME, font=f_brand, fill=text_fill)
    x0 = text_x + d.textlength(cfg.CHANNEL_NAME, font=f_brand) + 28
    d.line([(x0, gy - 62), (W - 56, gy - 62)], fill=text_fill, width=3)


def draw_hook(d, cfg, hook, top_y):
    W = cfg.CANVAS_W
    fill = hex2rgb(cfg.HOOK_TEXT_COLOR) + (255,)
    outline = hex2rgb(cfg.HOOK_OUTLINE_COLOR) + (255,)
    f_hook = font(cfg, "DISPLAY_FONT", 60)
    y = top_y
    for line in wrap(d, hook, f_hook, W - 64):
        d.text((36, y + 4), line, font=f_hook, fill=outline)  # bayangan
        d.text((32, y), line, font=f_hook, fill=fill,
               stroke_width=2, stroke_fill=outline)
        y += 76
    return y


def draw_footer(d, cfg, text_fill):
    f_foot = font(cfg, "FOOTER_FONT", 38)
    tw = d.textlength(cfg.FOOTER_TEXT, font=f_foot)
    d.text(((cfg.CANVAS_W - tw) / 2, cfg.FOOTER_Y), cfg.FOOTER_TEXT,
           font=f_foot, fill=text_fill)


def make_overlay(cfg, hook, out_path):
    W, H = cfg.CANVAS_W, cfg.CANVAS_H
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    ink = (0, 0, 0, 255)
    draw_header(d, canvas, cfg, ink)
    draw_hook(d, cfg, hook, cfg.GAMEPLAY_Y + cfg.GAMEPLAY_H + 58)
    draw_footer(d, cfg, ink)
    canvas.save(out_path)
    print("saved", out_path)


def make_canvas(cfg, hook, frame_path, out_path):
    W, H = cfg.CANVAS_W, cfg.CANVAS_H
    bg = hex2rgb(cfg.BACKGROUND_COLOR)
    canvas = Image.new("RGB", (W, H), bg)
    game = Image.open(frame_path).convert("RGB").resize((W, cfg.GAMEPLAY_H))
    canvas.paste(game, (0, cfg.GAMEPLAY_Y))
    d = ImageDraw.Draw(canvas)
    draw_header(d, canvas, cfg, (0, 0, 0))
    draw_hook(d, cfg, hook, cfg.GAMEPLAY_Y + cfg.GAMEPLAY_H + 58)
    draw_footer(d, cfg, (0, 0, 0))
    canvas.save(out_path)
    print("saved", out_path)


def main():
    ap = argparse.ArgumentParser(description="Buat overlay klip vertikal 1080x1920.")
    ap.add_argument("--hook", required=True, help="Teks hook (singkat, huruf besar enak dibaca)")
    ap.add_argument("--out", required=True, help="Path PNG hasil")
    ap.add_argument("--mode", choices=["overlay", "canvas"], default="overlay")
    ap.add_argument("--frame", help="Frame gameplay (wajib untuk --mode canvas)")
    ap.add_argument("--config", default=os.path.join(KIT_DIR, "config.py"),
                    help="Path file config (default: config.py di folder kit)")
    args = ap.parse_args()

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        example = os.path.join(KIT_DIR, "config.example.py")
        print(f"Config tidak ditemukan: {cfg_path}\n"
              f"Salin {example} menjadi config.py lalu sesuaikan isinya.",
              file=sys.stderr)
        # tetap jalan memakai config contoh agar pengguna bisa melihat hasil
        cfg_path = example
    cfg = load_config(cfg_path)

    if args.mode == "canvas":
        if not args.frame:
            ap.error("--mode canvas membutuhkan --frame")
        make_canvas(cfg, args.hook, args.frame, args.out)
    else:
        make_overlay(cfg, args.hook, args.out)


if __name__ == "__main__":
    main()
