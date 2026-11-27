# Vertical Clipper Kit

Kit templat untuk membuat **klip video vertikal 9:16 (1080x1920)** bergaya
"streamer clip": header nama channel, area gameplay besar, teks hook
raksasa yang terbaca sekilas, dan footer sosial media. Cocok untuk
Shorts / Reels / TikTok hasil potongan livestream.

Semua identitas — nama channel, warna, teks footer, logo, font — adalah
**parameter di satu file config**. Tidak ada branding yang ditanam di kode;
ganti config-nya, kit ini jadi milik channel kamu.

## Isi paket

| File | Fungsi |
|---|---|
| `overlay.py` | Overlay format standar: header + zona hook + footer (PNG transparan), atau mode kanvas penuh untuk pratinjau |
| `reaction_first.py` | Overlay varian *reaction-first*: band hook besar untuk momen reaksi streamer |
| `compose_split.py` | Pratinjau komposisi split (header + facecam + gameplay) dari satu frame sumber |
| `transcribe_ass.py` | Transkrip audio → subtitle `.ass` siap bakar (faster-whisper, timestamp per kata) |
| `config.example.py` | Contoh konfigurasi — salin jadi `config.py` dan isi identitasmu |
| `QC_CHECKLIST.md` | Checklist mutu wajib sebelum posting |
| `fonts/` | Font display Anton (SIL OFL) — unduh & tempatkan sesuai `fonts/README.md`; lisensi di `fonts/FONT_LICENSE.md` |

## Prasyarat

- Python 3.10+ dengan **Pillow**: `pip install pillow`
- **ffmpeg** (dengan libx264) terpasang dan ada di PATH
- Untuk subtitle: `pip install faster-whisper numpy`

## Cara pakai

### 1. Siapkan config

```bash
cp config.example.py config.py
```

Edit `config.py`: isi `CHANNEL_NAME`, `FOOTER_TEXT`, `BACKGROUND_COLOR`
(warna brand kamu), dan `LOGO_PATH` bila punya logo PNG transparan.

### 2. Buat overlay

```bash
python3 overlay.py --hook "DIA MELOMPAT DARI JET!" --out overlay.png
```

Hasilnya PNG 1080x1920 transparan: header di atas zona gameplay, hook di
bawah zona gameplay, footer di bawah. Pratinjau cepat dengan frame diam:

```bash
python3 overlay.py --mode canvas --frame frame.jpg --hook "GILA!" --out preview.png
```

### 3. Tumpuk ke video

Potong segmen dari sumber, skala/crop ke 1080x608 untuk zona gameplay,
lalu susun di atas latar warna brand-mu dan tumpuk overlay:

```bash
ffmpeg -ss 125 -i sumber.mp4 -f lavfi -i color=c=0x3A4756:s=1080x1920:r=30:d=30 \
  -loop 1 -framerate 30 -i overlay.png \
  -filter_complex "[0:v]fps=30,scale=1080:608[game];[1:v][game]overlay=0:570[c];[c][2:v]overlay=0:0,format=yuv420p[out]" \
  -map "[out]" -map 0:a -t 30 -c:v libx264 -profile:v high -preset veryfast \
  -crf 20 -c:a aac -b:a 128k -movflags +faststart klip-final.mp4
```

(ganti `0x3A4756` dengan warna latar config-mu dalam format hex ffmpeg.)

### 4. Varian reaction-first (khusus momen reaksi)

Untuk momen kaget/rage/jumpscare, reaksi streamer lebih menjual daripada
gameplay. Buat overlay-nya, lalu susun video mengikuti pola resep di
kepala file `reaction_first.py`:

```bash
python3 reaction_first.py overlay-reaction.png "DIA MENJERIT" "SEPERTI INI?!"
```

### 5. Subtitle bakar (opsional)

```bash
ffmpeg -i klip-final.mp4 -vn -ar 16000 audio.wav
python3 transcribe_ass.py audio.wav subs.ass
ffmpeg -i klip-final.mp4 -vf "ass=subs.ass" -c:a copy klip-sub.mp4
```

### 6. QC sebelum posting — wajib

Buka `QC_CHECKLIST.md` dan centang semuanya: h264 High + yuv420p +
faststart, loudness ±-14 LUFS, sensor kata kasar pakai beep 1 kHz,
hook terbaca di 2 detik pertama, cek 3 frame.

## Spesifikasi format

Kanvas **1080x1920** (9:16):

| Zona | Posisi | Isi |
|---|---|---|
| Header | y ≈ 466–570 | Logo 88x88 (opsional) + nama channel (font display 50) + garis pemisah |
| Gameplay | y 570, tinggi 608 | Video gameplay full-width, tanpa bingkai |
| Hook | mulai y ≈ 1236 | Font display 60, putih outline hitam + bayangan; maks. lebar 1016 px, teks dibungkus otomatis |
| Footer | y 1690 | Teks sosial media, rata tengah |

Varian reaction-first: facecam y 0–640, band hook y 640–880, gameplay
y 880–1760, footer pada band hitam y 1760–1920.

Angka-angka ini parameter di `config.py` / konstanta di kepala tiap
skrip — ubah bila kamu mengembangkan format sendiri.

## Kredit

Format ini terinspirasi gaya klip GTA 6 kreator Asakusamedia, lalu
dikembangkan dan dipakai untuk produksi channel QubixGame. Dibagikan
agar kreator klip lain bisa memakai fondasi yang sama dengan identitas
mereka sendiri.

## Lisensi

Kode: MIT (lihat `LICENSE`). Font Anton: SIL Open Font License 1.1
(lihat `fonts/FONT_LICENSE.md`).
