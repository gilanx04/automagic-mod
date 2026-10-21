Rilis publik pertama **Automagic Mod — WhatsApp + Gemini**, berbasis Automagic Premium 1.38.0.

Build ini menambahkan komponen WhatsApp native tanpa aplikasi terpisah:

- Trigger **WhatsApp Message Received** dengan mode exact, contains, wildcard, regex, similarity, dan welcome.
- Filter kontak allow/ignore dengan nama, nomor, nama grup, dan wildcard `*` / `?`.
- Action **Reply to WhatsApp Message** melalui Android `RemoteInput`.
- Menu percakapan bernomor: trigger induk membuat menu, trigger anak memilih opsi dari dropdown.
- Aksi menu `RETURN`, `STAY`, `EXIT`, dan `GOTO`.
- Tombol reset state menu aktif.
- Action **Gemini Reply** dengan prompt, API key, model, parameter generasi, dan placeholder riwayat percakapan.

## Perbaikan penting

- Trigger induk bisa membuka ulang menu saat menerima pesan yang bukan opsi menu.
- State menu lama tanpa timeout dibersihkan otomatis.
- Trigger anak hanya berjalan untuk menu dan opsi yang dipilih.
- `RETURN` mengaktifkan kembali menu induk dan mengirim ulang teksnya.

## Pasang

1. Backup flow Automagic.
2. Jika masih memakai Automagic resmi, ekspor flow lalu uninstall karena sertifikat build ini berbeda.
3. Install `Automagic_1.38.0-wa.1.apk`.
4. Aktifkan notification access untuk Automagic.
5. Nonaktifkan AutoResponder WhatsApp lain saat pengujian.

## Checksum

```text
205190df4f78376688b21cae0ecfe8c0d860ee97694dd12b671f93679040f57f  Automagic_1.38.0-wa.1.apk
```

Sertifikat: `CN=Automagic Patched, O=Local, C=ID` (bukan sertifikat resmi Gridvision).

## Penting

- Ini bukan build resmi. Tidak ada lisensi tambahan yang diberikan.
- API key Gemini disimpan di flow XML sebagai teks biasa; jangan bagikan flow yang berisi key.
- Direct reply bergantung pada action reply yang disediakan notifikasi WhatsApp.

Changelog lengkap: [`CHANGELOG.md`](https://github.com/gilanx04/automagic-mod/blob/main/CHANGELOG.md)
