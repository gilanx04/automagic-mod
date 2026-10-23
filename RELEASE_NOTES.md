Rilis keenam **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **Action Reset Conversation History**.

## Yang baru

### Reset Conversation History (`wa_reset_history`)

- Menghapus riwayat percakapan yang dipakai placeholder Gemini.
- Tiga mode: current conversation (dari trigger), kontak tertentu, atau semua.
- Hasilnya tersedia di variabel `{wa_history_status}`.

**Masalah yang diselesaikan:** selama flow dimatikan, tidak ada pesan yang tercatat
(trigger tidak jalan, balasan manual tidak terlihat Automagic). Saat flow diaktifkan
lagi, konteks yang dikirim ke Gemini masih berisi percakapan lama — akibatnya model
mengulang pertanyaan yang sudah pernah ditanyakan. Jalankan action ini sekali setelah
flow aktif kembali.

## Catatan tuning

Untuk jawaban yang terlalu panjang dan sering mengulang pertanyaan:

| Pengaturan | Saran |
| --- | --- |
| MAX OUTPUT TOKENS | `300` (rem panjang jawaban) |
| TEMPERATURE | `0.9` (atau `0.7` bila masih mengulang) |
| TOP K | `40` |
| TOP P | `0.95` |
| Jumlah pasang riwayat | tetap **3–5**, jangan 30 |

Menambah riwayat justru memperburuk pengulangan: model melihat lebih banyak contoh
balasannya sendiri lalu meniru pola itu.

## Pasang

1. Backup flow Automagic.
2. Install `Automagic_1.38.0-wa.6.apk` (update biasa bila sudah memakai build ini).
3. Install `AutomagicWaBridge_1.0.0.apk` dan aktifkan di LSPosed (scope WhatsApp)
   bila memakai action status.
4. Dokumentasi sudah built-in - tidak perlu langkah tambahan.

## Checksum

```text
56bd1fda4b6c1671e9d8beb22acb7bb1c7a38d6be711bdc0c0bb4526f8300df4  Automagic_1.38.0-wa.6.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
e6343052cb1f77b3ed3f53b4fe5de4981a63ede46eb192412082db6f911f7160  AutomagicDocs_1.38.zip
```

Sertifikat APK: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- Menghapus riwayat percakapan **tidak** menghapus chat WhatsApp asli; hanya konteks
  yang dikirim ke Gemini.
- API key Gemini tetap BYOK, disimpan sebagai teks biasa di flow XML.
