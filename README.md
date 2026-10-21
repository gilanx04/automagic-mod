# Automagic Mod — WhatsApp + Gemini

Build mod dari **Automagic Premium 1.38.0** yang menambahkan trigger dan action WhatsApp native, menu percakapan bernomor, filter kontak, serta balasan AI Google Gemini.

Repo ini berisi dokumentasi dan APK mod. Source code asli Automagic tidak disertakan dan tidak dilisensikan ulang di sini.

> **Bukan build resmi.** APK ditandatangani dengan kunci lokal `Automagic Patched`, bukan sertifikat Gridvision Engineering GmbH. Baca bagian [Peringatan](#peringatan) sebelum memasang.

## Rilis

| Properti | Nilai |
| --- | --- |
| Versi rilis | `1.38.0-wa.2` |
| `versionName` APK | `1.38.0` |
| `versionCode` | `4900` |
| Paket | `ch.gridvision.ppam.androidautomagic` |
| Ukuran APK | 8.813.735 byte (8,81 MB) |
| APK | [`Automagic_1.38.0-wa.2.apk`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.2/Automagic_1.38.0-wa.2.apk) |
| Modul bridge (LSPosed) | [`AutomagicWaBridge_1.0.0.apk`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.2/AutomagicWaBridge_1.0.0.apk) |
| Checksum | [`SHA256SUMS`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.2/SHA256SUMS) |
| Diuji pada | Xiaomi 2311DRK48G, Android 17 (SDK 37), WhatsApp 2.26.40.76, LSPosed 2.2.1 |

```text
80a61b82ad1ea4a6227b237ce569a78cca2b21b2c362ec3796fbddbb635a4e9d  Automagic_1.38.0-wa.2.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
```

## Fitur

### 1. Trigger WhatsApp Message Received

Trigger baru: **WhatsApp Message Received** (`wa_message_received`).

- Membaca notifikasi WhatsApp dan WhatsApp Business (`com.whatsapp`, `com.whatsapp.w4b`).
- Mode pencocokan pesan:
  - Any WhatsApp message
  - Exact match
  - Contains text
  - Pattern / wildcard (`*` dan `?`)
  - Expert pattern (regex)
  - Similarity match dengan ambang persentase
  - Welcome / first contact
- Filter jenis chat: semua, direct only, atau group only.
- Filter kontak:
  - Daftar kontak yang diizinkan (specific contacts).
  - Daftar kontak yang diabaikan (ignored contacts).
  - Mendukung nama kontak, nomor telepon, nama grup, dan wildcard `*` / `?`.
  - Pemisah koma.
- Opsi ignore case.
- Deduplikasi event agar notifikasi yang diperbarui tidak memicu flow berulang.
- Variabel trigger: `wa_sender`, `wa_message`, `wa_is_group`, `wa_group`, `wa_conversation`, `wa_package`, `wa_match_mode`.

### 2. Action Reply to WhatsApp Message

Action baru: **Reply to WhatsApp Message** (`wa_reply`).

- Mengirim balasan langsung dari notifikasi memakai **Android `RemoteInput`**.
- Mendukung action reply normal dan fallback wearable action.
- Tidak memakai atau menyalin kode AutoResponder for WA.
- Variabel yang tersedia: `{wa_sender}`, `{wa_message}`, `{wa_is_group}`, `{wa_group}`, `{wa_conversation}`, `{wa_package}`.

Balasan hanya bisa dikirim jika notifikasi WhatsApp menyediakan action direct reply. Jika WhatsApp tidak menyertakannya, action akan gagal dengan pesan yang jelas.

### 3. Menu percakapan bernomor

Menu dibuat dari trigger **induk** dan dijalankan oleh trigger **anak**.

#### Trigger induk (Root)

Pilih **Conversation menu → Start a menu with this trigger**.

Isi:

- **Menu name** — nama menu, misalnya `Main menu`.
- **Options** — satu opsi per baris:

```text
Harga | harga, price
Jam Buka | jam, buka, open
Admin | admin, cs
```

Label sebelum `|` selalu menjadi keyword. Keyword setelah `|` adalah alias tambahan. Nomor urut selalu diterima, jadi `1`, `2`, dan `3` otomatis cocok dengan urutan opsi.

- **Menu text** — opsional. Jika kosong, teks dibuat otomatis dalam format bernomor.
- **Auto-send menu** — kirim teks menu otomatis saat trigger induk berjalan.
- **Timeout** — lama menu aktif, dalam menit (0–10080).

Jika **Auto-send menu** aktif, jangan menambahkan action **Reply to WhatsApp Message** yang mengirim teks menu lagi pada flow yang sama. Auto-send dan action manual adalah dua jalur terpisah; memakai keduanya dapat menghasilkan balasan ganda.

Saat menu aktif, trigger induk tidak akan dijalankan lagi untuk pesan yang cocok dengan salah satu opsi. Jika pesan **bukan** opsi menu, trigger induk boleh membuka ulang menu. Ini memungkinkan pengguna mengetik `halo` lagi untuk memunculkan menu tanpa menunggu timeout.

#### Trigger anak (Child)

Pilih **Conversation menu → Menu option (child trigger)**.

Isi:

- **Active menu** — pilih menu dari daftar.
- **Option** — pilih opsi dari daftar.
- **After this option**:
  - `Return to main menu (send it again)` — aktifkan kembali menu induk dan kirim ulang teksnya.
  - `Stay in this menu` — biarkan menu tetap aktif tanpa mengirim ulang.
  - `Exit menu` — hapus state menu.
  - `Go to another menu` — pindah ke menu lain.

Trigger anak hanya berjalan jika menu yang dipilih sedang aktif untuk kontak tersebut. Pencocokan opsi (nomor atau keyword) mengabaikan field **Message match** umum, sehingga satu flow anak cukup menangani satu opsi.

#### Tombol reset

Tombol **Reset active conversation menus** di layar trigger menghapus semua state menu aktif. Berguna saat menguji atau ketika state lama menyangkut.

#### Variabel menu

- `wa_menu` — ID menu yang sedang dijalankan.
- `wa_parent_menu` — ID menu induk pada trigger anak.
- `wa_menu_text` — teks menu yang dihasilkan.
- `wa_menu_option` — nomor opsi yang dipilih.

State menu disimpan di SharedPreferences `wa_auto_reply_state`; definisi menu disimpan di `wa_menu_registry`. ID menu baru berbentuk `menu_<slug>`. Data lama dengan `menuKey` / `parentMenuKey` dimigrasikan otomatis.

### 4. Action Gemini Reply

Action baru: **Gemini Reply** (`wa_gemini_reply`).

Mengirim prompt ke Google Gemini melalui REST:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
Header: x-goog-api-key: <API key>
```

Pengaturan:

| Pengaturan | Keterangan |
| --- | --- |
| Prompt | Prompt utama. Bisa memakai penanda percakapan dan placeholder. |
| API key | Disimpan di flow XML sebagai `<apiKey>`. Lihat [Keamanan](#keamanan). |
| Model | Default `gemini-3.5-flash-lite`. Bisa diisi nama model lain. |
| Policy-violation reply | Balasan saat Gemini memblokir konten. |
| Reply prefix | Awalan yang ditambahkan ke balasan jika belum ada. |
| `max_output_tokens` | Batas token output. |
| `temperature` | 0.0–2.0. |
| `top_k` | Bilangan bulat positif. |
| `top_p` | 0.0–1.0. |
| Stop sequences | Dipisahkan `//`, misalnya `1://2://3::`. |
| Error reply | Balasan saat API key salah, kuota habis, jaringan gagal, atau Gemini tidak tersedia. |

#### Penanda prompt

- Teks sebelum penanda pertama menjadi **system instruction**.
- `1::` menandai giliran **user**.
- `2::` menandai giliran **model**.

Contoh:

```text
Anda adalah asisten WhatsApp yang ramah.

1:: %prev_message_1_512%
2:: %prev_reply_1_512%
1:: %message_512%
```

#### Placeholder

| Placeholder | Arti |
| --- | --- |
| `%message%` | Pesan masuk saat ini. |
| `%message_512%` | Pesan masuk, dipotong maksimal 512 karakter. |
| `%prev_message_1%` | Pesan masuk sebelumnya (offset 1 = terbaru). |
| `%prev_message_1_512%` | Sama, dipotong 512 karakter. |
| `%prev_message_2%` | Pesan masuk kedua sebelumnya. |
| `%prev_reply_1%` | Balasan keluar terakhir. |
| `%prev_reply_1_512%` | Balasan keluar terakhir, dipotong 512 karakter. |

Offset 1 berarti data terbaru sebelum pesan saat ini. Placeholder dengan akhiran angka kedua membatasi panjang teks.

Riwayat percakapan disimpan maksimal 30 entri per percakapan, terdiri dari pesan masuk dan balasan keluar. Ini bukan arsip chat lengkap.

### 5. Action Post WhatsApp Status

Action baru: **Post WhatsApp Status** (`wa_status`).

- Memposting **status WhatsApp berisi teks** tanpa interaksi pengguna, juga saat layar mati.
- Memakai composer status internal WhatsApp, jadi status benar-benar terkirim ke server dan muncul di tab **My status**.
- Audiens mengikuti **pengaturan privasi status terakhir** yang dipakai di WhatsApp (My contacts / Everyone / exclude).
- Teks mendukung placeholder dan variabel Automagic seperti action lain.
- Action berjalan asinkron (tidak membekukan UI Automagic) dan mengembalikan error yang jelas bila modul bridge tidak aktif.

Pengaturan:

| Pengaturan | Keterangan |
| --- | --- |
| Status text | Teks status. Mendukung placeholder `{...}`. |

> Action ini membutuhkan **modul LSPosed** `Automagic WA Bridge` (terlampir di rilis ini) yang diaktifkan untuk WhatsApp. Tanpa modul tersebut action akan gagal dengan pesan: *"The WhatsApp bridge module did not handle the request…"*.

#### Cara kerja

1. Automagic mengirim broadcast terurut ke receiver WhatsApp yang sudah diekspor
   (`com.whatsapp.infra.systemreceivers.boot.BootReceiver`) dengan aksi `com.automagic.wa.bridge.SEND_STATUS`.
2. Modul bridge (berjalan di proses WhatsApp) menerima broadcast, mengambil wake lock, lalu memanggil
   composer status internal (`X.7o8.A03` → `X.7o8.A05`) untuk membuat dan mengirim status.
3. Modul mengembalikan result code (`1` sukses, `2` gagal) ke Automagic lewat ordered broadcast.
4. Log modul ada di `/data/data/com.whatsapp/files/wa_bridge.log`.

#### Batasan

- Hanya **status teks**. Status berisi foto atau video belum didukung (butuh pipeline upload media WhatsApp).
- audience mengikuti privasi status terakhir, tidak bisa dipilih per-flow.
- Jika WhatsApp di-update, nama kelas internal bisa berubah dan modul perlu disesuaikan.

### 6. Modul bridge LSPosed

Modul terpisah: `AutomagicWaBridge_1.0.0.apk` (paket `com.automagic.wa.bridge`).

- Dibangun dengan libxposed API 102 (`META-INF/xposed/java_init.list`).
- Hanya diaktifkan untuk **WhatsApp** (`com.whatsapp`).
- Tidakmengumpulkan data apa pun; satu-satunya file yang dibuat adalah log di direktori data WhatsApp.
- Diperlukan root + LSPosed (Zygisk) pada perangkat.

Pemasangan modul:

1. Install `AutomagicWaBridge_1.0.0.apk`.
2. Buka **LSPosed → Modules**, aktifkan **Automagic WA Bridge**.
3. Centang scope **WhatsApp** (hanya `com.whatsapp`; `com.whatsapp.w4b` tidak didukung).
4. Force-stop WhatsApp, lalu jalankan flow yang memakai action **Post WhatsApp Status**.

### 7. Riwayat percakapan

- Disimpan per paket dan percakapan di SharedPreferences privat `wa_conversation_state`.
- Maksimal 30 entri.
- Event masuk dideduplikasi selama 15 detik.
- Dipakai oleh placeholder Gemini.
- Tidak disimpan di flow XML.

## Pemasangan

1. **Backup flow** dari Automagic sebelum memasang build mod.
2. Jika perangkat masih memakai Automagic resmi, APK ini **tidak bisa** dipasang sebagai update karena sertifikatnya berbeda. Ekspor flow, uninstall versi resmi, lalu install APK ini dan impor kembali flow. Jika perangkat sudah memakai build patched dengan kunci yang sama, update biasa bisa dilakukan.
3. Install `Automagic_1.38.0-wa.2.apk`.
4. Install `AutomagicWaBridge_1.0.0.apk`, aktifkan di LSPosed dengan scope **WhatsApp** (hanya perlu untuk action status).
5. Buka Automagic dan aktifkan **Notification access** untuk Automagic di pengaturan Android.
6. Nonaktifkan AutoResponder WhatsApp lain selama pengujian agar tidak ada balasan ganda.
7. Buat flow dan aktifkan.

APK ini **tidak** menghapus atau melewati pemeriksaan lisensi. Gunakan hanya jika Anda memiliki lisensi atau instalasi Automagic yang sah.

## Mulai cepat

### Menu WhatsApp

1. Buat flow baru.
2. Tambahkan trigger **WhatsApp Message Received**.
3. Isi kontak, misalnya `Pi Coding Agent`.
4. Pilih **Message match → Exact match**, isi `halo`.
5. Pilih **Conversation menu → Start a menu with this trigger**.
6. Isi menu:

```text
Main menu
Harga | harga, price
Jam Buka | jam, buka, open
Admin | admin, cs
```

7. Aktifkan **Auto-send menu**, timeout 30 menit, lalu simpan.
8. Tambahkan action **Reply to WhatsApp Message** jika ingin balasan tambahan; jika menu sudah auto-send, action ini opsional.
9. Buat flow anak untuk setiap opsi, pilih menu dan opsi dari dropdown, lalu tambahkan action balasan.

### Status WhatsApp

1. Buat flow baru.
2. Tambahkan action **Post WhatsApp Status**.
3. Isi **Status text**, misalnya `Halo dari Automagic`.
4. Jalankan flow. Status terkirim ke audiens status terakhir yang dipakai di WhatsApp.

### Gemini

1. Buat flow dengan trigger WhatsApp.
2. Tambahkan action **Gemini Reply**.
3. Isi prompt, API key, dan model.
4. Gunakan `%message_512%` untuk pesan saat ini, atau placeholder riwayat.
5. Simpan dan uji dengan pesan masuk.

## Keamanan

- **API key Gemini disimpan dalam flow XML sebagai teks biasa.** Jangan membagikan file flow yang berisi API key. Hapus key sebelum ekspor, atau gunakan key khusus dengan batas kuota.
- Aplikasi membaca isi notifikasi WhatsApp. Aktifkan notification access hanya di perangkat tepercaya.
- Jika memakai Gemini, isi prompt dan pesan yang diproses dikirim ke server Google sesuai kebijakan dan harga API Gemini.
- APK ini tidak berisi API key. Key hanya diisi di perangkat.

## Kompatibilitas dan batasan

- Diuji pada Android 17 (SDK 37), Xiaomi 2311DRK48G, WhatsApp 2.26.40.76.
- Minimal Android 5.0 untuk direct reply; build APK sendiri memakai `minSdkVersion` 14, tetapi fitur balasan membutuhkan Android 5.0+.
- WhatsApp harus menampilkan notifikasi dengan action direct reply. Jika notifikasi dimatikan, diringkas, atau formatnya berubah, balasan bisa gagal.
- Deteksi grup dan nama kontak bergantung pada metadata notifikasi WhatsApp.
- State menu disimpan per paket dan nama percakapan. Mengganti nama kontak saat menu aktif dapat membuat state tidak cocok.
- Timeout menu maksimal 7 hari.
- Riwayat hanya 30 entri; bukan pengganti arsip chat.
- Action **Post WhatsApp Status** butuh modul LSPosed `Automagic WA Bridge` dan scope WhatsApp aktif.
- Action status hanya mendukung status **teks**. Posting status foto atau video di luar cakupan rilis ini karena memerlukan pipeline upload media internal WhatsApp.
- Bridge memakai kelas internal WhatsApp (`X.7o8`, `X.81l`, `X.2Cz`). Nama kelas bisa berubah saat WhatsApp di-update, lalu modul perlu disesuaikan.
- Audiens status mengikuti privasi status terakhir di WhatsApp, tidak bisa dipilih per-flow.
- Android 11+ membatasi background service dan notification listener. Automagic adalah aplikasi lama yang tidak lagi dirawat, jadi perilakunya bisa berbeda di setiap ROM.
- Tidak ada jaminan build ini berjalan di semua perangkat. Uji pada perangkat yang tidak dipakai untuk pekerjaan penting.

## Verifikasi APK

```bash
sha256sum -c SHA256SUMS
apksigner verify --print-certs Automagic_1.38.0-wa.2.apk
aapt2 dump badging Automagic_1.38.0-wa.2.apk | head -3
```

Sertifikat build ini:

```text
CN=Automagic Patched, O=Local, C=ID
SHA-256: 54d8197cb9a2c41d418935ea07e12ebd8f8663dd7c3f4f02fd92f327ef709a51
```

Sertifikat tersebut **berbeda** dari sertifikat resmi Gridvision Engineering GmbH. Karena itu, build ini tidak bisa menjadi update langsung untuk aplikasi resmi.

## Peringatan

Automagic Premium adalah perangkat lunak komersial yang sudah tidak dikembangkan. Repo ini tidak memberikan lisensi, hak distribusi, atau hak cipta atas Automagic. APK disediakan untuk preservasi dan penggunaan pribadi oleh pemilik lisensi yang sah. Jika Anda pemegang hak cipta dan ingin konten ini dihapus, buka issue di repo ini.

Gunakan dengan risiko sendiri. Backup flow dan data penting sebelum memasang build mod.
