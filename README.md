# Automagic Mod — WhatsApp + Gemini

Build mod dari **Automagic Premium 1.38.0** yang menambahkan trigger dan action WhatsApp native, menu percakapan bernomor, filter kontak, serta balasan AI Google Gemini.

Repo ini berisi dokumentasi dan APK mod. Source code asli Automagic tidak disertakan dan tidak dilisensikan ulang di sini.

> **Bukan build resmi.** APK ditandatangani dengan kunci lokal `Automagic Patched`, bukan sertifikat Gridvision Engineering GmbH. Baca bagian [Peringatan](#peringatan) sebelum memasang.

## Rilis

| Properti | Nilai |
| --- | --- |
| Versi rilis | `1.38.0-wa.6` |
| `versionName` APK | `1.38.0` |
| `versionCode` | `4900` |
| Paket | `ch.gridvision.ppam.androidautomagic` |
| Ukuran APK | 10.321.506 byte (9.84 MB) |
| APK | [`Automagic_1.38.0-wa.6.apk`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.6/Automagic_1.38.0-wa.6.apk) |
| Modul bridge (LSPosed) | [`AutomagicWaBridge_1.0.0.apk`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.6/AutomagicWaBridge_1.0.0.apk) |
| Dokumentasi offline | [`AutomagicDocs_1.38.zip`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.6/AutomagicDocs_1.38.zip) |
| Tools agent | [`AutomagicTools_1.0.zip`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.6/AutomagicTools_1.0.zip) |
| Checksum | [`SHA256SUMS`](https://github.com/gilanx04/automagic-mod/releases/download/v1.38.0-wa.6/SHA256SUMS) |
| Diuji pada | Xiaomi 2311DRK48G, Android 17 (SDK 37), WhatsApp 2.26.40.76, LSPosed 2.2.1 |

```text
505936a20bdbad2c6f0ab4a742a6d4f79e14b9c092563ca9eab0f2a0601b1062  Automagic_1.38.0-wa.6.apk
0ae9a8b3933404a8fdc0ad6a6d4a2ca9b4a34e46e90cf846251252324357ddd9  AutomagicWaBridge_1.0.0.apk
e6343052cb1f77b3ed3f53b4fe5de4981a63ede46eb192412082db6f911f7160  AutomagicDocs_1.38.zip
2a97d4c9ca6352bc1101c93faae8b49e2f1e30c365637afcea3e0e8f014b39cc  AutomagicTools_1.0.zip
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
| Error reply | Balasan saat API key salah, kuota habis, jaringan gagal, atau Gemini tidak tersedia. Jika nilainya masih default, penyebab asli (mis. `HTTP 400: ...`) ditambahkan di belakangnya. |

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

### 7. Dokumentasi offline

Halaman bantuan bawaan Automagic menampilkan **404** karena seluruh isi
`automagic4android.com/automagic/1.38/` sudah dihapus dari server. Rilis ini
memulihkannya memakai arsip `web.archive.org`:

- **Help (F1)** — 449 halaman per bahasa (en/de). `HelpActivity` sudah mendukung
  mode offline: bila `files/help/<lang>/<page>.html` ada dan `version.txt` berisi
  `1.38`, halaman dimuat lewat `file://` tanpa menyentuh jaringan.
- **Catalog** — 448 komponen. `CatalogActivity` dipatch agar memakai
  `files/catalog/<lang>/catalog.html` bila tersedia, melewati cek jaringan, dan
  mengizinkan navigasi `file://` di dalam WebView.
- **Cakupan** — 219 action, 127 trigger, 88 condition; seluruhnya cocok dengan ID
  komponen di APK, ditambah 4 halaman untuk komponen buatan mod ini
  (`wa_reply`, `wa_status`, `wa_gemini_reply`, `wa_message_received`).
- **Built-in** — dibundel di `assets/amdocs/`, diekstrak otomatis saat dipakai.

**Dokumentasi sudah dibundel di dalam APK** (sejak `wa.5`). Tidak perlu langkah
pemasangan manual:

- Berkas disimpan di `assets/amdocs/` (HTML en/de + katalog + knowledge base agent).
- Diekstrak **malas** ke data aplikasi saat pertama dibuka: satu halaman saat
  halaman itu dibuka, katalog saat katalog dibuka, knowledge base saat action
  `ai_flow_agent` pertama kali dijalankan.
- Karena ikut APK, dokumentasi tetap ada setelah update maupun uninstall/install ulang.
- Varian bundel ini **tanpa screenshot** (tag `<img>` dibuang) agar APK tetap ~9,8 MB.
  Versi bergambar tetap tersedia terpisah di `AutomagicDocs_1.38.zip`.

### 8. AI flow agent (amflow)

`tools/amflow/` berisi alat agar agent (LLM) bisa merancang dan mengedit flow:

| Perintah | Fungsi |
| --- | --- |
| `amflow.py docs "<kata>"` | cari dokumentasi komponen |
| `amflow.py list [kategori]` | daftar ID komponen (223 action, 128 trigger, 89 condition) |
| `amflow.py component <id>` | tag, tipe, dan contoh nyata komponen |
| `amflow.py new "<nama>"` | buat file flow |
| `amflow.py add <file> <id> --from-example` | tambah komponen + container + koneksi |
| `amflow.py validate <file>` | validasi struktur, tag, koneksi, keterjangkauan |
| `amflow.py install <file>` | backup + gabung ke `flows.xml` |

Skema komponen (`schema.json`) diekstrak dari source hasil decompile; 198 dari 223
action, 127 dari 128 trigger, dan 64 dari 89 condition sudah memiliki daftar tag.
Panduan lengkap untuk agent ada di `tools/amflow/AGENTS.md`.

Contoh:

```bash
python3 tools/amflow/amflow.py new "Backup harian"
python3 tools/amflow/amflow.py add "Backup harian.flow.xml" periodic_timer \
    --category trigger --from-example --set interval=86400
python3 tools/amflow/amflow.py add "Backup harian.flow.xml" http_request \
    --from-example --set url=https://example.com/upload --set httpMethod=POST
python3 tools/amflow/amflow.py validate "Backup harian.flow.xml"
python3 tools/amflow/amflow.py install "Backup harian.flow.xml" --restart
```

`install` selalu membuat backup `flows.xml_amflow_<timestamp>.bak` dan tidak pernah
menghapus flow yang sudah ada.

### 9. Action Reset Conversation History

Action baru: **Reset Conversation History** (`wa_reset_history`) — menghapus riwayat
percakapan yang dipakai placeholder Gemini.

| Pengaturan | Keterangan |
| --- | --- |
| What to reset | Current conversation (dari trigger), Specific contact, All conversations |
| Contact / conversation | untuk mode Specific, mendukung variabel |
| Package | default `com.whatsapp` |

Hasil jumlah yang dihapus disimpan di `{wa_history_status}`.

**Kapan perlu:** setelah flow dimatikan lama lalu diaktifkan lagi. Selama flow mati
tidak ada pesan yang tercatat (trigger tidak jalan, balasan manual tidak terlihat),
sehingga konteks yang dikirim ke Gemini menjadi basi — model lalu cenderung
mengulang pertanyaan lama. Jalankan action ini sekali setelah flow aktif kembali.

### 10. Action AI Flow Agent

Action baru: **AI Flow Agent** (`ai_flow_agent`) — merancang flow Automagic dari
deskripsi bahasa alami, langsung di perangkat.

| Pengaturan | Keterangan |
| --- | --- |
| Flow request | Deskripsi flow dalam bahasa bebas, mendukung variabel `{...}` |
| Flow name | Nama file flow hasil (opsional) |
| Model | Default `gemini-3.5-flash-lite` |
| Gemini API keys | **Satu key per baris**; key kena limit otomatis dilewati |
| Install generated flow | Langsung pasang ke Automagic (default: preview saja) |
| Fix attempts | Berapa kali model diminta memperbaiki XML yang tidak valid |

Alur kerja di dalam action:

1. **Pilih komponen** — katalog 441 komponen (21 KB) dikirim ke model.
2. **Susun flow** — model menerima tag, contoh nyata, dan dokumentasi komponen terpilih.
3. **Validasi & perbaiki** — XML diperiksa (tipe komponen, container vs definisi,
   koneksi, nama duplikat); bila ada error, model diminta memperbaikinya.

Hasil ditulis ke `/sdcard/Automagic/agent/<nama>.flow.xml`, dan variabel
`{ai_flow_status}`, `{ai_flow_file}`, `{ai_flow_error}` diisi untuk dipakai action lain.

**Rotasi API key:** key dipakai berurutan. HTTP 429 / kuota habis → key diberi
cooldown 30 menit lalu key berikutnya dipakai; key tidak valid diistirahatkan 24 jam.
Status disimpan di SharedPreferences `amagent_keys`, jadi tidak hilang saat flow
dijalankan ulang.

> Provider saat ini **Gemini (BYOK)** — tidak ada API key yang dibundel di APK; user
> mengisi sendiri. Key tersimpan sebagai teks biasa di flow XML.

### 11. Memori jangka panjang Gemini

Tiga lapis memori agar model tidak "buta waktu" dan tidak lupa hal penting, tanpa
mengirim seluruh riwayat.

| Lapis | Isi | Biaya kuota |
| --- | --- | --- |
| Waktu | label `[3 jam lalu]` pada tiap giliran, `%now%`, `%last_seen%` | 0 |
| Fakta | `%memory%` — persona + catatan stabil per kontak | 0 |
| Ringkasan | `%summary%` — pesan lama dipadatkan tiap N pesan | 1 panggilan / N pesan |

#### Placeholder baru

| Placeholder | Isi |
| --- | --- |
| `%now%` | waktu sekarang, mis. `Jum, 23 Okt 2026 22:55` |
| `%last_seen%` | kapan terakhir bicara, mis. `3 hari lalu` |
| `%memory%` | daftar fakta (persona + catatan) |
| `%summary%` | ringkasan pesan lama |

Contoh prompt:

```
%memory%

Konteks: sekarang %now%. Terakhir kamu bicara dengan Melani %last_seen%.

Ringkasan obrolan sebelumnya:
%summary%

1:: %prev_message_0_3_512%
2:: %prev_reply_0_3_512%
1:: %message_512%
```

Teks sebelum penanda `1::` pertama dikirim sebagai `system_instruction`.

#### Action Gemini Memory (`wa_memory`)

| Pilihan | Fungsi |
| --- | --- |
| Set a fact | simpan/ganti satu fakta |
| Remove a fact | hapus satu fakta |
| Clear all facts | hapus semua fakta |
| Reset facts + summary | hapus fakta dan ringkasan |
| Install built-in persona | pasang persona bawaan (12 fakta) |
| Show memory | tampilkan fakta dan ringkasan |

Persona bawaan dipasang otomatis saat percakapan pertama kali memakai action Gemini.
Hasil aksi disimpan di `{wa_memory_status}`.

#### Pengaturan Gemini Reply

| Pengaturan | Default | Keterangan |
| --- | --- | --- |
| Include message timestamps | aktif | label waktu pada tiap giliran |
| Summarize every N messages | `10` | `0` = matikan ringkasan otomatis |

**Mengapa bukan embedding/RAG?** Untuk chat dua orang, embedding 768 dimensi
(~7,5 KB JSON) jauh lebih besar daripada teks aslinya (belasan byte), butuh satu
panggilan API tambahan per pesan, dan retrieval semantik hampir selalu kalah dari
recency pada percakapan berurutan. Tiga lapis di atas mencapai hasil yang sama
dengan ~500 token.

### 12. Riwayat percakapan

- Disimpan per paket dan percakapan di SharedPreferences privat `wa_conversation_state`.
- Maksimal 30 entri per percakapan.
- Hanya mencatat pesan yang lewat trigger (masuk) dan action (keluar). Pesan yang
  dikirim manual saat flow mati **tidak** tercatat.
- Bisa dihapus dengan action **Reset Conversation History**.
- Fakta dan ringkasan jangka panjang disimpan terpisah di `wa_memory_state`
  (per percakapan), dikelola action **Gemini Memory**.
- Event masuk dideduplikasi selama 15 detik.
- Dipakai oleh placeholder Gemini.
- Tidak disimpan di flow XML.

## Pemasangan

1. **Backup flow** dari Automagic sebelum memasang build mod.
2. Jika perangkat masih memakai Automagic resmi, APK ini **tidak bisa** dipasang sebagai update karena sertifikatnya berbeda. Ekspor flow, uninstall versi resmi, lalu install APK ini dan impor kembali flow. Jika perangkat sudah memakai build patched dengan kunci yang sama, update biasa bisa dilakukan.
3. Install `Automagic_1.38.0-wa.7.apk`.
4. Install `AutomagicWaBridge_1.0.0.apk`, aktifkan di LSPosed dengan scope **WhatsApp** (hanya perlu untuk action status).
5. Dokumentasi offline sudah ikut di dalam APK — tidak ada langkah tambahan.
6. Buka Automagic dan aktifkan **Notification access** untuk Automagic di pengaturan Android.
7. Nonaktifkan AutoResponder WhatsApp lain selama pengujian agar tidak ada balasan ganda.
8. Buat flow dan aktifkan.

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
- Dokumentasi offline disimpan di data aplikasi; hilang bila aplikasi di-uninstall.
- Skema komponen untuk `amflow` diekstrak otomatis, jadi sebagian condition belum punya daftar tag.
- Android 11+ membatasi background service dan notification listener. Automagic adalah aplikasi lama yang tidak lagi dirawat, jadi perilakunya bisa berbeda di setiap ROM.
- Tidak ada jaminan build ini berjalan di semua perangkat. Uji pada perangkat yang tidak dipakai untuk pekerjaan penting.

## Verifikasi APK

```bash
sha256sum -c SHA256SUMS
apksigner verify --print-certs Automagic_1.38.0-wa.6.apk
aapt2 dump badging Automagic_1.38.0-wa.6.apk | head -3
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
