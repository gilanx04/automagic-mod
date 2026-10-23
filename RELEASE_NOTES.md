Rilis keempat **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **AI Flow Agent di dalam Automagic** (Gemini BYOK, rotasi multi API key).

## Yang baru

### Action AI Flow Agent

- Merancang flow dari deskripsi bahasa alami, langsung di perangkat tanpa PC.
- Tiga tahap: pilih komponen dari katalog 441 komponen → susun XML → validasi dan
  perbaiki otomatis bila ada error.
- Hasil ditulis ke `/sdcard/Automagic/agent/`, bisa langsung dipasang atau preview.
- Variabel `{ai_flow_status}`, `{ai_flow_file}`, `{ai_flow_error}` untuk dirantai ke action lain.
- Tidak ada API key yang dibundel: provider Gemini murni BYOK, key diisi user.

### Rotasi multi API key

- Beberapa key (satu per baris) dipakai berurutan.
- Key kena limit (HTTP 429) diistirahatkan 30 menit lalu key berikutnya dipakai.
- Key tidak valid diistirahatkan 24 jam. Status cooldown tersimpan di perangkat.

### Perbaikan penting

- Definisi komponen kini ditulis sebelum `<flow>` (sebelumnya flow bisa muncul dengan
  node kosong yang tidak bisa diedit).
- `amflow install` menulis ulang `flow_check`, sehingga Automagic tidak lagi menolak
  flow hasil edit eksternal.

## Pasang

1. Backup flow Automagic.
2. Install `Automagic_1.38.0-wa.4.apk` (update biasa bila sudah memakai build ini).
3. Install `AutomagicWaBridge_1.0.0.apk` dan aktifkan di LSPosed (scope WhatsApp)
   bila memakai action status.
4. Pasang `AutomagicDocs_1.38.zip` sesuai `tools/docs/install_docs.sh`.
5. Ekstrak `AutomagicTools_1.0.zip` bila ingin memakai amflow.

## Checksum

```text
cf8719eaea937073777f5e14021b482460ee01501d5dd76e3a5865e91a70888d  Automagic_1.38.0-wa.4.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
e6343052cb1f77b3ed3f53b4fe5de4981a63ede46eb192412082db6f911f7160  AutomagicDocs_1.38.zip
2a97d4c9ca6352bc1101c93faae8b49e2f1e30c365637afcea3e0e8f014b39cc  AutomagicTools_1.0.zip
```

Sertifikat APK: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- Dokumentasi disimpan di data aplikasi; hilang bila aplikasi di-uninstall.
- `amflow` tidak menghapus flow yang ada dan selalu membuat backup sebelum menulis.
