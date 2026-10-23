Rilis kelima **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **dokumentasi dibundel di APK** dan **perbaikan Gemini Reply**.

## Yang baru

### Dokumentasi & knowledge base built-in

- Dokumentasi offline (449 halaman x 2 bahasa), katalog 448 komponen, dan knowledge
  base AI agent kini ikut di dalam APK.
- Diekstrak otomatis saat dipakai (malas), jadi tidak ada langkah pemasangan manual.
- Tetap ada setelah update maupun uninstall/install ulang.
- APK bertambah ~1,4 MB (8,4 -> 9,8 MB). Versi bundel tanpa screenshot; versi
  bergambar tetap tersedia di `AutomagicDocs_1.38.zip`.

### Perbaikan Gemini Reply

- Percakapan yang dikirim ke Gemini dinormalisasi (peran sama digabung, giliran
  `model` di awal dibuang). Ini memperbaiki error generik
  "One of the parameters is invalid..." yang muncul saat riwayat percakapan kosong
  atau tidak berselang-seling.
- Penyebab asli error kini ditampilkan di belakang pesan default, mis.
  `... (HTTP 400: Please ensure that multiturn requests alternate between user and model)`.

## Pasang

1. Backup flow Automagic.
2. Install `Automagic_1.38.0-wa.5.apk` (update biasa bila sudah memakai build ini).
3. Install `AutomagicWaBridge_1.0.0.apk` dan aktifkan di LSPosed (scope WhatsApp)
   bila memakai action status.
4. Dokumentasi sudah built-in - tidak perlu langkah tambahan.

## Checksum

```text
5fa5e1d0f40d2fe24793e502143ad99918595fddfaa255ea02e5acef9b053897  Automagic_1.38.0-wa.5.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
e6343052cb1f77b3ed3f53b4fe5de4981a63ede46eb192412082db6f911f7160  AutomagicDocs_1.38.zip
2a97d4c9ca6352bc1101c93faae8b49e2f1e30c365637afcea3e0e8f014b39cc  AutomagicTools_1.0.zip
```

Sertifikat APK: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- Screenshot dokumentasi tidak dibundel agar APK tidak membengkak; teks lengkap tetap ada.
- API key Gemini tetap BYOK, disimpan sebagai teks biasa di flow XML.
