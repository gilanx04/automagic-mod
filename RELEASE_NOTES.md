Rilis ketujuh **Automagic Mod**, berbasis Automagic Premium 1.38.0.

Fokus rilis ini: **memori jangka panjang Gemini**.

## Yang baru

### 1. Gemini tidak lagi buta waktu

Setiap giliran riwayat diberi label relatif:

```
1:: [3 hari lalu] kamu sayang aku?
2:: [3 hari lalu] sayang banget dong ayangg
1:: [2 jam lalu] sayang kemana?
1:: sekarang — kamu udah makan?
```

Placeholder baru: `%now%`, `%last_seen%`. Sebelumnya timestamp disimpan tetapi
tidak pernah dikirim ke model.

### 2. Fakta jangka panjang (`%memory%`)

Persona dan catatan stabil dikirim setiap kali, hanya ~150 token:

```
- nama: Gilang
- pasangan: Melani
- pekerjaan: sibuk 08:00-21:00 nganter orderan
- sifat_melani: manja dan sering ngeyel, saat sakit tetap minum es
- gaya_balasan: maksimal 2 kalimat pendek, jangan mengulang pertanyaan
```

Dikelola lewat action baru **Gemini Memory** (`wa_memory`): set, remove, clear,
reset, install persona bawaan, show memory.

### 3. Ringkasan otomatis (`%summary%`)

Pesan lama dipadatkan menjadi 4 kalimat setiap 10 pesan. Ingatan bisa membentang
berminggu-minggu tanpa mengirim seluruh riwayat. Bisa dimatikan (isi `0`).

**Biaya:** satu panggilan API tambahan per 10 pesan. Lapis waktu dan fakta
**tanpa** tambahan kuota.

### 4. Dokumentasi offline kini ikut ter-update

Dulu halaman lama tidak pernah diganti karena ekstraksi hanya memeriksa
keberadaan berkas. Sekarang ada penanda versi bundel.

## Mengapa bukan embedding / RAG

Untuk percakapan dua orang, embedding justru lebih boros:

| Masalah | Angka |
| --- | --- |
| Embedding > teks | "sayang kemana?" = 14 karakter, embedding 768 dim ≈ 7,5 KB JSON |
| Kuota | satu panggilan `:embedContent` per pesan |
| Relevansi | chat berurutan: yang relevan hampir selalu yang terbaru, bukan yang mirip |

Tiga lapis di atas mencapai hasil yang sama dengan ~500 token.

## Catatan

- Persona bawaan memakai nama Gilang/Melani. Untuk kontak lain jalankan
  **Gemini Memory → Reset facts + summary**.
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
