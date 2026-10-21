# Changelog

Semua perubahan penting pada build mod Automagic dicatat di sini.

## [1.38.0-wa.1] — 2026-10-21

Rilis publik pertama **Automagic Mod — WhatsApp + Gemini**. Build ini berbasis Automagic Premium 1.38.0 (`versionCode` 4900) dan menambahkan komponen WhatsApp native tanpa aplikasi terpisah.

### Ditambahkan

#### Trigger WhatsApp

- Trigger **WhatsApp Message Received** (`wa_message_received`).
- Dukungan notifikasi `com.whatsapp` dan `com.whatsapp.w4b`.
- Mode pencocokan:
  - Any WhatsApp message
  - Exact match
  - Contains text
  - Wildcard pattern (`*` dan `?`)
  - Regex
  - Similarity match dengan ambang persentase
  - Welcome / first contact
- Filter jenis chat: semua, direct only, dan group only.
- Filter **specific contacts** dan **ignored contacts**:
  - Nama kontak, nomor telepon, dan nama grup.
  - Wildcard `*` dan `?`.
  - Pemisah koma.
- Opsi ignore case.
- Deduplikasi event notifikasi.
- Variabel trigger:
  - `wa_sender`
  - `wa_message`
  - `wa_is_group`
  - `wa_group`
  - `wa_conversation`
  - `wa_package`
  - `wa_match_mode`

#### Action balas WhatsApp

- Action **Reply to WhatsApp Message** (`wa_reply`).
- Pengiriman balasan melalui Android `RemoteInput` pada action direct reply notifikasi.
- Fallback ke wearable reply action untuk notifikasi yang menyediakannya.
- Dukungan variabel `{wa_sender}`, `{wa_message}`, `{wa_is_group}`, `{wa_group}`, `{wa_conversation}`, dan `{wa_package}`.
- Tidak menggunakan atau menyalin kode AutoResponder for WA.

#### Menu percakapan

- Mode menu pada trigger:
  - `NONE` — trigger WhatsApp biasa.
  - `ROOT` — membuat dan menjalankan menu bernomor.
  - `CHILD` — menangani satu opsi dari menu aktif.
- Menu builder pada trigger induk:
  - Nama menu.
  - Daftar opsi dengan format `Label | keyword1, keyword2`.
  - Teks menu kustom.
  - Auto-send teks menu.
  - Timeout menu.
- Dropdown menu dan opsi pada trigger anak, tanpa perlu mengetik menu key manual.
- Aksi setelah opsi:
  - `RETURN` — aktifkan kembali menu induk dan kirim ulang teksnya.
  - `STAY` — pertahankan menu tanpa mengirim ulang.
  - `EXIT` — hapus state menu.
  - `GOTO` — pindah ke menu lain.
- Registry menu di SharedPreferences `wa_menu_registry`.
- ID menu baru berbentuk `menu_<slug>`.
- Migrasi otomatis dari data lama `menuKey` / `parentMenuKey`.
- Variabel menu:
  - `wa_menu`
  - `wa_parent_menu`
  - `wa_menu_text`
  - `wa_menu_option`
- Tombol **Reset active conversation menus** untuk membersihkan state menu aktif.
- State menu disimpan per paket dan percakapan di `wa_auto_reply_state`.

#### Gemini

- Action **Gemini Reply** (`wa_gemini_reply`).
- Endpoint REST `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`.
- Header `x-goog-api-key`.
- Pengaturan:
  - Prompt.
  - API key.
  - Model (default `gemini-3.5-flash-lite`).
  - Policy-violation reply.
  - Reply prefix.
  - `max_output_tokens`.
  - `temperature`.
  - `top_k`.
  - `top_p`.
  - Stop sequences dengan pemisah `//`.
  - Error reply.
- Penanda prompt `1::` untuk user dan `2::` untuk model.
- Teks sebelum penanda pertama dipakai sebagai system instruction.
- Placeholder:
  - `%message%`
  - `%message_512%`
  - `%prev_message_1%`
  - `%prev_message_1_512%`
  - `%prev_message_2%`
  - `%prev_reply_1%`
  - `%prev_reply_1_512%`
- Penanganan khusus untuk safety block, recitation, dan policy violation.
- Reply prefix tidak ditambahkan dua kali.
- Error API, kuota, jaringan, dan respons kosong diarahkan ke error reply.

#### Riwayat percakapan

- Penyimpanan riwayat masuk dan keluar per percakapan di `wa_conversation_state`.
- Maksimal 30 entri per percakapan.
- Deduplikasi event masuk selama 15 detik.
- Riwayat dipakai oleh placeholder Gemini.
- Tidak disimpan di flow XML.

#### UI dan integrasi

- Layout pengaturan trigger WhatsApp baru.
- Layout pengaturan action Gemini.
- Registrasi komponen `wa_message_received`, `wa_reply`, dan `wa_gemini_reply` di service komponen Automagic.
- Variabel baru terdaftar di daftar variabel flow.
- Tombol bantuan notification access pada layar trigger.

### Diubah

- Trigger induk yang menangani menu sekarang dapat membuka ulang menu saat menerima pesan yang **bukan** salah satu opsi menu. Sebelumnya semua pesan diblokir selama menu aktif.
- Trigger anak dengan opsi tertentu mengabaikan field **Message match** umum; pencocokan dilakukan terhadap nomor opsi dan keyword opsi.
- Menu auto-send dan action balasan manual dapat digunakan bersamaan, tetapi action manual bersifat opsional.
- Nama default trigger/action mengikuti konfigurasi menu, misalnya `WhatsApp: any · menu Main menu › Harga`.
- Timeout menu dibatasi 0–10080 menit.

### Diperbaiki

- State menu lama tanpa key `_timeout` tidak lagi memblokir trigger induk; state tersebut dibersihkan otomatis.
- Menu yang masih aktif tidak lagi membuat trigger induk diam total ketika pengguna mengirim pesan pembuka lagi.
- Opsi menu nomor `1`, `2`, `3` dan keyword-nya sekarang dicocokkan langsung oleh trigger anak.
- Trigger anak tidak berjalan jika menu yang dipilih tidak sedang aktif untuk kontak tersebut.
- Trigger anak tidak berjalan untuk opsi yang berbeda.
- State menu dibersihkan dengan benar saat `EXIT`.
- `RETURN` mengaktifkan kembali menu induk dan mengirim ulang teks menu.
- `GOTO` memindahkan state ke menu tujuan dan mengirim teks menu tujuan.
- Migrasi menu lama tidak lagi membutuhkan pengetikan menu key manual.
- Tombol reset menghapus key menu, waktu, dan timeout sekaligus.

### Keamanan

- API key Gemini disimpan sebagai `<apiKey>` di flow XML dalam bentuk teks biasa. Jangan membagikan flow yang berisi key.
- APK tidak menyertakan API key pengguna.
- Aplikasi membutuhkan notification access untuk membaca notifikasi WhatsApp.
- Tidak ada bypass lisensi Automagic.
- Build ditandatangani kunci lokal, bukan kunci resmi Gridvision.

### Kompatibilitas

- Diuji pada Xiaomi 2311DRK48G, Android 17 (SDK 37), WhatsApp 2.26.40.76.
- Direct reply membutuhkan Android 5.0+ dan action reply dari notifikasi WhatsApp.
- WhatsApp harus mengizinkan notifikasi dan menyertakan direct reply action.
- Build tidak bisa dipasang sebagai update langsung di atas Automagic resmi karena perbedaan sertifikat.
- Data flow tetap berada di perangkat; build ini tidak mengunggah flow ke server mana pun.

### Pengujian

- Trigger induk `halo` menampilkan menu bernomor.
- Trigger induk dapat menampilkan ulang menu saat menu masih aktif.
- Trigger anak opsi `1. Harga` mengirim balasan `Harga: Rp 100.000`.
- Tombol reset state menu tersedia dan berfungsi.
- Pengaturan menu tersimpan di registry dan flow XML.
- Aplikasi berjalan setelah update build dan service notification listener aktif.

### Catatan upgrade

- Rilis ini memakai APK yang sudah diuji, dengan `versionName` tetap `1.38.0` dan `versionCode` `4900`.
- Suffix rilis `-wa.1` hanya menandai seri build mod, bukan versi internal Automagic.
- Jika sebelumnya memakai build patched dengan kunci yang sama, APK dapat dipasang sebagai update dan data flow dipertahankan.
- Jika sebelumnya memakai Automagic resmi, ekspor flow terlebih dahulu, uninstall aplikasi resmi, lalu install build ini.
- Backup flow sebelum melakukan update atau uninstall.

### Diketahui

- Balasan bergantung pada format notifikasi WhatsApp. Perubahan WhatsApp di masa depan dapat mematahkan direct reply.
- Deteksi nama grup dan pengirim dapat berbeda tergantung versi WhatsApp dan ROM.
- Riwayat percakapan hanya 30 entri dan bukan arsip chat lengkap.
- State menu memakai nama percakapan; mengganti nama kontak saat menu aktif dapat membuat state tidak cocok.
- API key Gemini di flow XML harus dilindungi sendiri oleh pengguna.

---

## Format versi

`1.38.0-wa.1`

- `1.38.0` — versi dasar Automagic.
- `wa.1` — nomor seri build mod WhatsApp/Gemini.
