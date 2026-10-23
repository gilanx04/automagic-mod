Rilis ketiga **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **dokumentasi offline** dan **tooling AI agent untuk flow**.

## Yang baru

### Dokumentasi offline

- Semua halaman bantuan yang sebelumnya 404 kini tersedia offline.
- 449 halaman per bahasa (en/de), 56 screenshot, plus katalog 448 komponen.
- Help memakai mekanisme offline bawaan aplikasi; Catalog dipatch agar memakai
  file lokal dan tetap bisa navigasi antar halaman.

### AI flow agent (amflow)

- CLI untuk agent: cari dokumentasi, lihat skema komponen, buat flow, validasi,
  lalu pasang dengan backup otomatis.
- Skema komponen diekstrak dari source: 223 action, 128 trigger, 89 condition.
- Validator menangkap kesalahan umum sebelum flow dipasang.
- `AGENTS.md` menjelaskan alur kerja dan aturan keamanan untuk agent.

## Pasang

1. Backup flow Automagic.
2. Install `Automagic_1.38.0-wa.3.apk` (update biasa bila sudah memakai build ini).
3. Install `AutomagicWaBridge_1.0.0.apk` dan aktifkan di LSPosed (scope WhatsApp)
   bila memakai action status.
4. Pasang `AutomagicDocs_1.38.zip` sesuai `tools/docs/install_docs.sh`.
5. Ekstrak `AutomagicTools_1.0.zip` bila ingin memakai amflow.

## Checksum

```text
505936a20bdbad2c6f0ab4a742a6d4f79e14b9c092563ca9eab0f2a0601b1062  Automagic_1.38.0-wa.3.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
e6343052cb1f77b3ed3f53b4fe5de4981a63ede46eb192412082db6f911f7160  AutomagicDocs_1.38.zip
2a97d4c9ca6352bc1101c93faae8b49e2f1e30c365637afcea3e0e8f014b39cc  AutomagicTools_1.0.zip
```

Sertifikat APK: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- Dokumentasi disimpan di data aplikasi; hilang bila aplikasi di-uninstall.
- `amflow` tidak menghapus flow yang ada dan selalu membuat backup sebelum menulis.
