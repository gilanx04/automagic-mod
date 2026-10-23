# Dokumentasi offline Automagic

Halaman bantuan di dalam Automagic menampilkan **404** karena aplikasi memuat:

- `http://automagic4android.com/automagic/1.38/help/<lang>/<page>.html`
- `http://automagic4android.com/automagic/1.38/catalog/<lang>/catalog.html`

Domain masih hidup, tetapi seluruh isinya sudah dihapus.

## Bagaimana dipulihkan

### Help — memakai fitur bawaan aplikasi

`HelpActivity` sebenarnya sudah mendukung bantuan offline:

```java
File f = new File(new File(getFilesDir(), "help"), lang + "/" + page + ".html");
if (f.exists()) return "file://" + f.getAbsolutePath();   // dipakai
else return "http://automagic4android.com/...";           // fallback (404)
```

Jadi cukup menaruh HTML di `files/help/<lang>/` dan `version.txt` berisi `1.38`.
Tidak perlu patch APK.

### Catalog — perlu patch kecil

`CatalogActivity` hanya memakai URL remote. Patch di `onCreate` memilih
`files/catalog/<lang>/catalog.html` bila ada, melewati cek jaringan, dan
`shouldOverrideUrlLoading` diubah agar navigasi `file://` tetap di dalam WebView.

## Sumber data

`automagic-help/` adalah arsip dokumentasi dari `web.archive.org`
(snapshot 2022–2023). Setiap file markdown menyimpan `source` dan `archive_url`.

Cakupan (dicocokkan dengan ID komponen di APK):

| Kategori | Halaman | Cocok dengan app |
| --- | ---: | ---: |
| Action | 219 | 219 |
| Trigger | 127 | 127 |
| Condition | 88 | 88 |

Ditambah 4 halaman untuk komponen buatan sendiri (`wa_reply`, `wa_status`,
`wa_gemini_reply`, `wa_message_received`).

## Membangun dan memasang

```bash
python3 work/docs/build_help.py     # md -> html (en + de) + katalog
sh work/docs/install_docs.sh        # salin ke data aplikasi (root)
```

Hasil build: `work/docs/help-out/{en,de}/*.html` dan
`work/docs/help-out/catalog/{en,de}/catalog.html`.

## Catatan

- Dokumentasi disimpan di data aplikasi, jadi tetap ada saat APK di-update,
  tetapi hilang bila aplikasi di-uninstall.
- Bahasa mengikuti locale: `de` untuk Jerman, selain itu `en`.
- Halaman komponen baru otomatis memakai nama `action_<id>`, `trigger_<id>`,
  `condition_<id>` — sama seperti yang dicari `ActionActivity`/`TriggerActivity`.
