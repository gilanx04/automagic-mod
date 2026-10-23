Rilis kedelapan **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **editor memori Gemini**.

## Yang baru

### 1. Memori kini bisa diedit seperti teks

Dulu fakta hanya bisa diubah satu per satu lewat action — merepotkan untuk 12 fakta.
Sekarang ada editor:

**Edit action Gemini → scroll bawah → Buka editor memori**

```
KONTAK / PERCAKAPAN   [ Sayangkuu 💗💋  ▾ ]
                      [ Kontak baru... ]

☑ Pasang persona bawaan otomatis untuk kontak ini
12 fakta · terakhir: 2 jam lalu

FAKTA — satu per baris, format key: value
  nama: Gilang
  pasangan: Melani
  pekerjaan: sibuk 08:00-21:00 nganter orderan
  pantangan: suka minum es saat sakit

RINGKASAN OTOMATIS (boleh diedit)
  ...

[ Simpan ] [ Muat ulang ]
[ Persona bawaan ] [ Hapus semua ]
```

### 2. Saklar persona otomatis benar-benar bekerja

Saklar langsung mengubah isi kotak fakta:

| Saklar | Akibat |
| --- | --- |
| dinyalakan | baris persona yang belum ada langsung ditambahkan |
| dimatikan | baris persona dihapus, fakta buatanmu tetap |

Matikan untuk kontak kerja supaya persona Gilang tidak ikut terkirim ke Gemini.

### 3. Perbaikan penting

- **Kontak kedua tidak tersimpan.** Menambah kontak baru membuat daftar dibangun
  ulang dan Spinner memilih item pertama, sehingga kontak yang baru diketik tertimpa
  dan fakta masuk ke kontak yang salah. Ini bug yang kamu temukan saat uji.
- **Kunci ganda di `%memory%`.** Persona dulu menimpa seluruh daftar; sekarang hanya
  melengkapi kunci yang belum ada.
- **Simpan mematikan persona otomatis.** Sekarang hanya `Hapus semua` yang
  mematikannya.

## Catatan

- Nama kontak harus sama persis dengan `{wa_conversation}` dari trigger, **termasuk
  emoji**. `Sayangkuu` dan `Sayangkuu 💗💋` adalah dua memori berbeda — kalau ragu,
  pakai `Kontak baru...` lalu salin nama dari notifikasi WhatsApp.
- Ringkasan memakai model dan API key yang sama dengan action Gemini.
- Memori disimpan di `wa_memory_state`, terpisah dari riwayat percakapan.

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
