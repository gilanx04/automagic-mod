Rilis kedua **Automagic Mod — WhatsApp + Gemini**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **posting status WhatsApp tanpa interaksi pengguna**.

## Yang baru

- Action **Post WhatsApp Status** (`wa_status`): memposting status teks ke WhatsApp tanpa membuka aplikasi, juga saat layar mati.
- Memakai composer status internal WhatsApp, jadi status benar-benar terkirim dan bisa dilihat kontak.
- Audiens mengikuti privasi status terakhir di WhatsApp.
- Action berjalan asinkron, jadi Automagic tidak freeze.
- Modul LSPosed baru `AutomagicWaBridge_1.0.0.apk` yang bridging Automagic ke composer status WhatsApp.

## Pasang

1. Backup flow Automagic.
2. Jika masih memakai Automagic resmi, ekspor flow lalu uninstall karena sertifikat build ini berbeda.
3. Install `Automagic_1.38.0-wa.2.apk`.
4. Install `AutomagicWaBridge_1.0.0.apk`, aktifkan di LSPosed, dan beri scope **WhatsApp**.
5. Aktifkan notification access untuk Automagic.
6. Nonaktifkan AutoResponder WhatsApp lain saat pengujian.

## Checksum

```text
80a61b82ad1ea4a6227b237ce569a78cca2b21b2c362ec3796fbddbb635a4e9d  Automagic_1.38.0-wa.2.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
```

Sertifikat APK Automagic: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Batasan

- Action status hanya mendukung status **teks** (foto/video belum didukung).
- Butuh root + LSPosed.
- Bridge memakai kelas internal WhatsApp; update WhatsApp bisa membuat modul perlu disesuaikan.

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- Posting status otomatis melanggar ketentuan layanan WhatsApp dan bisa memicu pembatasan akun. Gunakan dengan risiko sendiri.
- API key Gemini disimpan di flow XML sebagai teks biasa; jangan bagikan flow yang berisi key.
