# Changelog

Semua perubahan penting pada build mod Automagic dicatat di sini.

## [1.38.0-wa.9] — 2026-10-24

Rilis kesembilan: **isolasi riwayat per kontak** dan pemisahan persona.

### Ditambahkan

#### Tombol Hapus riwayat di editor

- Menghapus pesan tersimpan **dan** ringkasan otomatis untuk kontak yang dipilih.
- Fakta memori tidak terpengaruh.
- Hasil ditampilkan di layar: jumlah pesan + ringkasan yang dihapus.

#### Isolasi riwayat per nama kontak

- Kunci penyimpanan sekarang memakai nama kontak persis + hash SHA-1 (8 heksadesimal).
- Sebelumnya nama disaring menjadi `_` dan dipotong 120 karakter, sehingga
  `Sayangkuu 💗💋` dan `Sayangkuu 💋💗` sama-sama menjadi `Sayangkuu_____` dan
  riwayatnya bercampur. Hal yang sama berlaku pada memori.
- Data berkunci lama dipindahkan otomatis saat pertama kali dibaca; tidak ada riwayat
  yang hilang saat upgrade.

### Diperbaiki

- **Ringkasan otomatis tidak ikut dihapus** saat riwayat direset, sehingga ringkasan
  persona lama tetap dikirim lewat `%summary%` setelah riwayatnya kosong.
  - `wa_reset_history` kini juga mengosongkan ringkasan (per kontak atau semua).
  - `WaMemoryStore.clearAllSummaries()` ditambahkan.
- **Penjaga tabrakan memori**: bila data pada sebuah kunci ternyata milik kontak lain,
  data itu tidak dipakai.

### Diubah

- Flow **Auto Reply Melani** sekarang hanya menangani `Sayangkuu 💗💋`. `Pi Coding
  Agent` dikeluarkan dari filter agar persona Gilang tidak bocor ke chat lain.
- Flow baru **Pi Coding Agent - Developer**: persona developer terpisah, dipicu
  keyword `!dev` (mode CONTAINS) agar tidak terjadi balasan berulang bila kontak itu
  ternyata bot.

### Catatan

- Ringkasan dipadatkan dari riwayat; begitu riwayat direset, ringkasan lama otomatis
  dianggap basi.
- Dokumen: 451 halaman/bahasa.

## [1.38.0-wa.8] — 2026-10-24

Rilis kedelapan: **editor memori Gemini** dan perbaikan persona otomatis.

### Ditambahkan

#### Editor memori (Gemini Memory)

Activity baru untuk melihat dan mengubah memori sebagai teks, bukan satu fakta
per action.

- Daftar kontak (Spinner) untuk berpindah percakapan, plus **Kontak baru...**.
- Kotak **FAKTA**: teks bebas, satu fakta per baris `key: value`, font monospace.
- Kotak **RINGKASAN**: ringkasan otomatis bisa dilihat dan diedit.
- **Simpan** / **Muat ulang**, **Persona bawaan**, **Hapus semua**.
- Label status: jumlah fakta, status persona otomatis, kapan terakhir bicara.
- Dibuka dari tombol **Buka editor memori** di pengaturan action
  **Reply with Google Gemini** dan **Gemini Memory**.

#### Saklar persona otomatis

- Saklar **Pasang persona bawaan otomatis untuk kontak ini** langsung mengubah isi
  kotak fakta: menyalakan menambahkan baris persona yang belum ada, mematikan
  menghapusnya. Fakta buatan user tidak disentuh.
- Pemasangan otomatis saat flow berjalan memakai aturan yang sama.

#### API memori

- `WaMemoryStore.installPersona()` — menambah persona yang belum ada (aditif).
- `WaMemoryStore.removePersona()` — mencabut persona berdasarkan nama kunci.
- `WaMemoryStore.replaceFacts()` — menulis ulang seluruh daftar.
- `WaMemoryStore.setNoSeed()`, `conversations()`, `Memory.noSeed`.

### Diperbaiki

- **Kontak baru tidak tersimpan saat menambah kontak kedua.** Membangun ulang
  daftar kontak membuat Spinner memilih item pertama dan menimpa percakapan yang
  baru diketik; fakta lalu masuk ke kontak yang salah. Kontak yang sedang dibuka
  sekarang selalu ikut masuk daftar sebelum adapter dipasang.
- **`installPersona` menghasilkan kunci ganda.** Persona dulu menimpa seluruh
  daftar; kini hanya melengkapi kunci yang belum ada, sehingga `%memory%` tidak
  memuat kunci yang sama dua kali.
- **Menyimpan fakta mematikan persona otomatis.** Sebelumnya setiap **Simpan**
  menyalakan `noSeed`; sekarang hanya saat daftar benar-benar kosong.
- **Saklar persona hanya menyimpan status** tanpa mengubah data, sehingga tidak
  bisa dibuktikan dari editor.

### Catatan

- Nama kontak harus sama persis dengan `{wa_conversation}` dari trigger, termasuk
  emoji. Kontak `Sayangkuu` dan `Sayangkuu 💗💋` adalah dua memori berbeda.
- Dokumen: 451 halaman/bahasa, 443 komponen di katalog.

## [1.38.0-wa.7] — 2026-10-23

Rilis ketujuh: **memori jangka panjang Gemini** (waktu, fakta, ringkasan).

### Ditambahkan

#### Label waktu pada riwayat

- Setiap giliran riwayat yang dikirim ke Gemini diberi label relatif, mis.
  `[3 jam lalu] kamu udah makan?`.
- Opsi **Include message timestamps** (default aktif) untuk mematikan.
- Sebelumnya timestamp disimpan tetapi tidak pernah dikirim, sehingga model tidak
  tahu jeda antar pesan.

#### Placeholder memori

| Placeholder | Isi |
| --- | --- |
| `%now%` | waktu sekarang, mis. `Jum, 23 Okt 2026 22:55` |
| `%last_seen%` | kapan terakhir bicara, mis. `3 hari lalu` |
| `%memory%` | fakta jangka panjang (persona + catatan) |
| `%summary%` | ringkasan pesan lama |

#### Action Gemini Memory (`wa_memory`)

- Mode: set, remove, clear facts, reset facts + summary, install built-in persona,
  show memory.
- Persona bawaan 12 fakta (nama, panggilan, pekerjaan, sifat, emosi yang
  diizinkan, aturan balasan) dipasang otomatis saat percakapan pertama kali
  memakai action Gemini.
- Hasil aksi disimpan di `{wa_memory_status}`.

#### Ringkasan otomatis

- Opsi **Summarize every N messages** (default 10, `0` = mati).
- Pesan lama dipadatkan menjadi maksimal 4 kalimat, dikirim lewat `%summary%`.
- Berjalan di thread terpisah setelah balasan terkirim, jadi tidak menambah latensi.
- Memakai satu panggilan API tambahan per N pesan.

#### Penyimpanan

- `WaMemoryStore` — SharedPreferences `wa_memory_state`, per paket + percakapan.
- Fakta bawaan ditandai `builtin` agar bisa dibedakan dari catatan buatan user.

### Diperbaiki

- **Dokumentasi offline tidak ikut diperbarui saat APK di-update.** Ekstraksi dulu
  hanya memeriksa "berkas sudah ada", sehingga halaman versi lama tetap dipakai
  selamanya. Sekarang ada penanda `bundle.txt` berisi versi bundel; dokumentasi,
  katalog, dan knowledge base diekstrak ulang saat versi berubah.

### Diubah

- `build_knowledge.py` menerima variabel lingkungan `AMFLOW_DOCS` untuk memilih
  sumber HTML (mis. build tanpa gambar).
- Prompt contoh pada flow Gemini kini memakai `%memory%`, `%now%`, `%last_seen%`,
  dan `%summary%`.

### Catatan

- Dokumen: 451 halaman/bahasa, 443 komponen di katalog.
- Persona bawaan memakai nama Gilang/Melani; untuk kontak lain jalankan
  **Gemini Memory → Reset facts + summary**.

## [1.38.0-wa.6] — 2026-10-23

Rilis keenam: action **Reset Conversation History**.

### Ditambahkan

#### Action Reset Conversation History (`wa_reset_history`)

- Menghapus riwayat percakapan yang dipakai placeholder Gemini (`%prev_message_*`,
  `%prev_reply_*`).
- Tiga mode: **Current conversation** (dari variabel `{wa_conversation}`),
  **Specific contact**, dan **All conversations**.
- Hasil jumlah entri yang dihapus disimpan di `{wa_history_status}`.
- Berguna setelah flow dimatikan lama: selama flow mati tidak ada pesan yang tercatat,
  sehingga konteks ke Gemini menjadi basi dan model mengulang pertanyaan lama.

#### API riwayat percakapan

- `WaConversationStore.clear()`, `clearAll()`, `conversations()`, dan `size()`.

#### Dokumentasi

- Halaman `action_wa_reset_history` ditambahkan (en/de) dan ikut dibundel di APK.
- Knowledge base agent diperbarui (225 action).

## [1.38.0-wa.5] — 2026-10-23

Rilis kelima: **dokumentasi & knowledge base dibundel di APK**, plus perbaikan
penting pada Gemini Reply.

### Ditambahkan

#### Dokumentasi built-in

- HTML dokumentasi (en/de, 449 halaman/bahasa), katalog, dan knowledge base AI agent
  dibundel di `assets/amdocs/` (905 berkas, +1,4 MB pada APK).
- Kelas `DocsInstaller` mengekstrak **malas**: satu halaman saat dibuka, katalog saat
  katalog dibuka, knowledge base saat action agent pertama dijalankan.
- Dokumentasi tetap ada setelah update maupun uninstall/install ulang — tidak perlu
  `install_docs.sh` atau zip lagi.
- Varian bundel tanpa screenshot (tag `<img>` dibuang); versi bergambar tetap
  tersedia di `AutomagicDocs_1.38.zip`.

### Diperbaiki

#### Gemini Reply: `INVALID_ARGUMENT`

- Percakapan yang dikirim ke Gemini kini **dinormalisasi**: giliran dengan peran sama
  digabung dan giliran `model` di awal dibuang. Sebelumnya placeholder riwayat yang
  kosong menghasilkan urutan `user,user` (atau diawali `model`), dan Gemini menolak
  seluruh permintaan dengan `INVALID_ARGUMENT`.
- Pesan error generik tidak lagi menyembunyikan penyebab: bila `Error reply` masih
  default, penyebab asli ditambahkan dalam tanda kurung, mis.
  `... (HTTP 400: Please ensure that multiturn requests alternate between user and model)`.
- Prompt dengan placeholder `%prev_message_0_3_512%` / `%prev_reply_0_3_512%` tetap
  didukung (format: `%prev_message_<offset>_<limit>%`).

#### Build

- `apktool` menyimpan cache dex dan melaporkan "smali has not changed"; skrip build
  sekarang menghapus cache tersebut sehingga setiap perubahan smali selalu ikut.

## [1.38.0-wa.4] — 2026-10-23

Rilis keempat: **AI Flow Agent di dalam Automagic** (Gemini BYOK + rotasi multi API key).

### Ditambahkan

#### Action AI Flow Agent (`ai_flow_agent`)

- Merancang flow dari deskripsi bahasa alami, langsung di perangkat.
- Tiga tahap: pilih komponen dari katalog → susun XML → validasi & perbaiki otomatis.
- Memakai knowledge base on-device: `catalog.txt` (441 komponen), `catalog.json`
  (tag + contoh nyata), `docs_index.json` (448 halaman dokumentasi).
- Hasil ditulis ke `/sdcard/Automagic/agent/<nama>.flow.xml`; opsi langsung pasang.
- Variabel hasil: `{ai_flow_status}`, `{ai_flow_file}`, `{ai_flow_error}`.
- Eksekusi asinkron memakai `androidautomagiclib.util.cj`, jadi UI tidak membeku.

#### Rotasi API key Gemini

- Beberapa key (satu per baris) dipakai berurutan.
- HTTP 429 / kuota habis → key diistirahatkan 30 menit, key berikutnya dipakai.
- Key tidak valid diistirahatkan 24 jam.
- Status cooldown disimpan di SharedPreferences `amagent_keys`.
- Tidak ada API key yang dibundel; provider Gemini murni BYOK.

#### Tooling agent (CLI)

- `agent.py` — versi CLI dari agent (multi key, endpoint kustom, `--install`).
- `mock_gemini.py` — server Gemini tiruan untuk menguji tanpa API key.
- `build_knowledge.py` — membangun knowledge base on-device.

### Diperbaiki

- **Urutan elemen flow**: definisi komponen wajib ditulis sebelum `<flow>`.
  Sebelumnya `amflow` menaruh `<flow>` lebih dulu sehingga container tidak
  ter-resolve (nama kosong dan tidak bisa diedit). `amflow` kini menata ulang otomatis.
- **Integritas flows.xml**: `amflow install` sekarang menulis ulang `flow_check`
  (`SHA1("89389812312" + isi flows.xml)`) sehingga Automagic tidak lagi menampilkan
  "The flow definitions have been modified outside of Automagic".
- `--replace` untuk menimpa flow dengan nama sama, `--enable` untuk mengaktifkan
  flow saat dibuat, `--from-example` menyalin tag berulang (mis. 7 `<weekday>`).
- Action menyimpan hasil parse `periodic_timer`/`time` dengan benar.

## [1.38.0-wa.3] — 2026-10-23

Rilis ketiga: **restorasi dokumentasi offline** dan **tooling AI agent untuk merancang flow**.

### Ditambahkan

#### Dokumentasi offline

- Halaman bantuan bawaan (404) dipulihkan dari arsip `web.archive.org`.
- 449 halaman per bahasa (en/de): 219 action, 127 trigger, 88 condition,
  4 panduan, 6 referensi, plus halaman indeks.
- 4 halaman baru untuk komponen mod ini: `wa_reply`, `wa_status`,
  `wa_gemini_reply`, `wa_message_received`.
- `HelpActivity` memakai fitur offline bawaan: `files/help/<lang>/*.html` +
  `version.txt` = `1.38`.
- `CatalogActivity` dipatch: memakai `files/catalog/<lang>/catalog.html` bila ada,
  melewati cek jaringan, dan mengizinkan navigasi `file://` di WebView.
- 56 screenshot ikut dipulihkan.

#### AI flow agent (amflow)

- `tools/amflow/amflow.py`: `docs`, `list`, `component`, `new`, `add`, `validate`,
  `install`.
- `schema.json` diekstrak otomatis dari source decompile: 223 action, 128 trigger,
  89 condition, dengan daftar tag untuk 198 action / 127 trigger / 64 condition.
- Contoh komponen nyata diambil dari `flows.xml` (36 action, 20 trigger,
  10 condition) untuk dipakai `--from-example`.
- Validator memeriksa: tipe komponen dikenal, definisi vs container, nama duplikat,
  koneksi ke ID tak dikenal, node tidak terhubung, dan tag di luar skema.
- `install` membuat backup `flows.xml_amflow_<timestamp>.bak` dan tidak menghapus
  flow yang sudah ada.
- `tools/amflow/AGENTS.md`: panduan kerja untuk agent.

### Diperbaiki

- Container `actioncontainer`/`conditioncontainer` memakai teks elemen, sedangkan
  `triggercontainer` memakai child `<trigger>`; keduanya kini ditangani validator.
- Nama komponen hanya unik per kategori, sehingga trigger dan condition boleh
  bernama sama.
- `triggercontainer` kosong diperlakukan sebagai flow manual (peringatan, bukan error).

## [1.38.0-wa.2] — 2026-10-21

Rilis kedua: menambah **posting status WhatsApp tanpa interaksi** lewat action baru dan modul LSPosed terpisah.

### Ditambahkan

#### Action Post WhatsApp Status

- Action baru **Post WhatsApp Status** (`wa_status`).
- Memposting status WhatsApp berisi teks tanpa membuka UI WhatsApp, juga saat layar mati.
- Memakai composer status internal WhatsApp sehingga status benar-benar terkirim ke server.
- Audiens mengikuti privasi status terakhir yang dipakai di WhatsApp.
- Teks status mendukung placeholder `{...}` seperti action lain.
- Eksekusi asinkron: tidak membekukan UI Automagic, dan error dikembalikan ke flow.

#### Modul bridge LSPosed

- Modul terpisah `AutomagicWaBridge_1.0.0.apk` (paket `com.automagic.wa.bridge`).
- libxposed API 102, scope hanya `com.whatsapp`.
- Menerima broadcast `com.automagic.wa.bridge.SEND_STATUS`, mengambil wake lock, lalu membuat dan mengirim status lewat composer internal WhatsApp.
- Mengembalikan result code ke Automagic (1 sukses, 2 gagal).
- Log modul: `/data/data/com.whatsapp/files/wa_bridge.log`.

### Batasan

- Hanya status **teks** yang didukung. Posting status foto atau video **tidak termasuk** dalam cakupan rilis ini (butuh pipeline upload media WhatsApp).
- Hanya paket `com.whatsapp`; WhatsApp Business (`com.whatsapp.w4b`) belum didukung untuk action status.
- Bridge bergantung pada nama kelas internal WhatsApp, jadi perlu disesuaikan bila WhatsApp di-update.
- Memerlukan root + LSPosed.

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
- Menu auto-send dan action balasan manual adalah dua jalur terpisah. Gunakan auto-send saja atau action saja untuk menghindari balasan ganda.
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
