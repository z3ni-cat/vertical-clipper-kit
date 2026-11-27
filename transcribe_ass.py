#!/usr/bin/env python3
"""Vertical Clipper Kit — transkrip audio -> subtitle ASS siap bakar.

Memakai faster-whisper (model "small", CPU int8) dengan timestamp per
kata, lalu mengelompokkan kata menjadi cue subtitle pendek
(maks. 7 kata / 3,2 detik / 42 karakter per cue) dan menulis file .ass
dengan PlayRes 1080x1920 (WAJIB eksplisit — tanpa header resolusi,
renderer subtitle akan menebak resolusi kecil dan posisi/skala teks
jadi kacau).

Prasyarat: pip install faster-whisper numpy
Masukan: file WAV (ekstrak dulu dari video: ffmpeg -i klip.mp4 audio.wav)

Contoh:
  python3 transcribe_ass.py audio.wav subs.ass
  ffmpeg -i klip.mp4 -vf "ass=subs.ass" -c:a copy klip-sub.mp4

Catatan gaya: font & posisi diatur di blok Style di bawah (nama "Sub").
Ganti Fontname dengan font yang terpasang di sistemmu bila perlu.
"""
import json
import sys
import wave as wave_mod

import numpy as np
from faster_whisper import WhisperModel

wav, ass_path = sys.argv[1], sys.argv[2]
model = WhisperModel("small", device="cpu", compute_type="int8")
wf = wave_mod.open(wav, "rb")
n = wf.getnframes()
raw = wf.readframes(n)
audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
segments, info = model.transcribe(audio, language="en", word_timestamps=True, vad_filter=True)
words = []
for s in segments:
    for w in (s.words or []):
        words.append((w.start, w.end, w.word.strip()))
print("words:", len(words), "lang:", info.language)


def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# kelompokkan kata menjadi cue: maks 7 kata atau 3.2 detik atau 42 karakter
cues, cur = [], []
for st, en, w in words:
    cur.append((st, en, w))
    dur = en - cur[0][0]
    if len(cur) >= 7 or dur >= 3.2 or len(" ".join(x[2] for x in cur)) >= 42:
        cues.append(cur)
        cur = []
if cur:
    cues.append(cur)

lines = ["""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Arial,46,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,760,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""]
for c in cues:
    text = " ".join(x[2] for x in c)
    lines.append(f"Dialogue: 0,{ts(c[0][0])},{ts(c[-1][1])},Sub,,0,0,0,,{text}")
open(ass_path, "w").write("\n".join(lines) + "\n")
print("cues:", len(cues), "->", ass_path)
