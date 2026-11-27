"""Konfigurasi contoh Vertical Clipper Kit.

Salin file ini menjadi `config.py` (atau arahkan flag --config ke file ini),
lalu ganti semua nilai di bawah dengan identitas channel KAMU sendiri.
Semua skrip di kit ini membaca nilai dari sini — tidak ada identitas
yang ditanam di dalam kode.
"""

# Nama channel kamu (tampil di header overlay).
CHANNEL_NAME = "ContohChannel"

# Teks footer (sosial media), tampil di bagian bawah overlay.
FOOTER_TEXT = "Follow : ContohChannel | Youtube : @contohchannel"

# Warna latar kanvas (format "#RRGGBB"). Contoh ini memakai warna netral
# biru-abu; silakan ganti dengan warna brand kamu sendiri.
BACKGROUND_COLOR = "#3A4756"

# Warna teks hook (default putih dengan outline hitam).
HOOK_TEXT_COLOR = "#FFFFFF"
HOOK_OUTLINE_COLOR = "#000000"

# Warna band hook pada varian reaction-first (reaction_first.py).
# Secara default memakai warna latar yang sama; ganti bila ingin band
# dengan warna berbeda dari latar utama.
BAND_COLOR = "#3A4756"

# Path font display (untuk nama channel & hook). Anton dibundel di folder
# fonts/ (lisensi SIL OFL — lihat fonts/FONT_LICENSE.md). Boleh diganti
# dengan font display lain milikmu.
DISPLAY_FONT = "fonts/Anton.ttf"

# Path font teks biasa (untuk footer). Kosongkan ("") untuk memakai font
# bawaan Pillow. Contoh bila kamu punya Montserrat Bold:
# FOOTER_FONT = "/path/ke/Montserrat-Bold.ttf"
FOOTER_FONT = ""

# Path logo channel (PNG transparan, akan diskalakan ke 88x88).
# Kosongkan ("") bila tidak ingin menampilkan logo.
LOGO_PATH = ""

# Geometri kanvas (standar format kit ini — ubah hanya bila paham akibatnya).
CANVAS_W = 1080
CANVAS_H = 1920
GAMEPLAY_Y = 570       # posisi Y area gameplay
GAMEPLAY_H = 608       # tinggi area gameplay
FOOTER_Y = 1690        # posisi Y teks footer
