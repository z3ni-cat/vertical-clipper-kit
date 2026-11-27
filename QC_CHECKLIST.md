# Checklist QC Sebelum Posting

Jalankan semua poin ini pada file MP4 final. Klip yang gagal satu poin
pun sebaiknya diperbaiki dulu — platform dan penonton sama-sama kejam
soal file rusak.

## 1. Spesifikasi file (ffprobe)

```bash
ffprobe -v error -show_streams -show_format klip-final.mp4
```

- [ ] Codec video **h264**, profile **High** — BUKAN "High 4:4:4 Predictive"
      (profile 4:4:4 tidak bisa diputar banyak pemutar HP).
- [ ] `pix_fmt` = **yuv420p**.
- [ ] Resolusi **1080x1920**, frame rate konsisten (30 fps aman).
- [ ] **Faststart**: atom `moov` berada sebelum `mdat` (cek:
      `ffprobe -v trace klip-final.mp4 2>&1 | grep -E "type:'(moov|mdat)'"`,
      moov harus muncul lebih dulu). Tanpa faststart, video lambat mulai
      dan pratinjau di beberapa aplikasi gagal membaca durasi.
      Perbaiki dengan: `ffmpeg -i in.mp4 -c copy -movflags +faststart out.mp4`

## 2. Audio

- [ ] Loudness keseluruhan sekitar **-14 LUFS** (toleransi ±1).
      Ukur: `ffmpeg -i klip-final.mp4 -af loudnorm=print_format=json -f null -`
- [ ] Tidak ada clipping / puncak di atas -1 dBTP.
- [ ] Kata kasar **disensor dengan beep 1 kHz** (nada sine 1000 Hz),
      BUKAN dimute/dipotong — mute membuat dialog terasa patah dan
      penonton sadar ada yang hilang; beep terdengar "disengaja".
      Contoh menyisipkan beep pada rentang 12,30–12,85 detik:

      ```bash
      ffmpeg -i klip.mp4 -f lavfi -i "sine=frequency=1000:duration=0.55" \
        -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0[a]" \
        ...
      ```

      (atau bleep per kata mengikuti timestamp dari transcribe_ass.py —
      sensor per kata jauh lebih rapi daripada per segmen kasar.)

## 3. Visual

- [ ] **Hook terbaca dalam 2 detik pertama**: putar klip, jeda di detik
      ke-1 — teks hook harus sudah utuh terbaca (tidak kepotong, tidak
      tertutup elemen lain, kontras cukup di atas gameplay).
- [ ] Cek **3 frame** — awal (±detik 2), tengah, akhir:

      ```bash
      ffmpeg -ss 2 -i klip-final.mp4 -frames:v 1 cek-awal.jpg
      ffmpeg -ss <tengah> -i klip-final.mp4 -frames:v 1 cek-tengah.jpg
      ffmpeg -ss <akhir-1dtk> -i klip-final.mp4 -frames:v 1 cek-akhir.jpg
      ```

      Periksa: overlay sejajar, tidak ada area hitam tak disengaja,
      facecam tidak memotong wajah, subtitle tidak keluar bingkai.
- [ ] Subtitle bakar (bila ada): tidak ada baris yang meluber keluar
      layar; teks muncul seirama dengan ucapan.

## 4. Konten

- [ ] Judul & caption platform sesuai isi klip (tidak clickbait kosong).
- [ ] Klip tidak mengklaim hal yang tidak terjadi di dalamnya.
- [ ] Kredit sumber dicantumkan di deskripsi bila memakai footage pihak
      lain, sesuai aturan platform & pemilik konten.
