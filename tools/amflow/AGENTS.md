# AGENTS.md — merancang flow Automagic dengan AI agent

Panduan ini untuk agent (LLM) yang bertugas membuat atau mengubah flow Automagic
atas permintaan user. Semua alat ada di `work/amflow/`.

## Alur kerja wajib

1. **Pahami permintaan** — tentukan trigger, kondisi, aksi, dan variabel yang dipakai.
2. **Cari dokumentasi** (jangan menebak nama tag):
   ```
   python3 work/amflow/amflow.py docs "kirim file ke ftp"
   ```
   Buka file markdown yang relevan di `automagic-help/` untuk membaca bagian *Settings*.
3. **Cek skema komponen**:
   ```
   python3 work/amflow/amflow.py component http_request
   ```
   Output berisi daftar tag + tipe + contoh nyata dari flows.xml.
4. **Bangun flow**:
   ```
   python3 work/amflow/amflow.py new "Backup harian" --group "Custom"
   python3 work/amflow/amflow.py add "Backup harian.flow.xml" periodic_timer \
       --category trigger --from-example --set interval=86400
   python3 work/amflow/amflow.py add "Backup harian.flow.xml" http_request \
       --from-example --set url=https://example.com/upload --set httpMethod=POST
   ```
   `--from-example` menyalin tag dari flow nyata (termasuk tag berulang seperti
   `<weekday>`), lalu `--set` menimpa nilainya.
5. **Validasi** (wajib, jangan dilewati):
   ```
   python3 work/amflow/amflow.py validate "Backup harian.flow.xml"
   ```
   Perbaiki semua `ERROR`. `peringatan` boleh dibiarkan bila disengaja.
6. **Pasang** hanya setelah user menyetujui:
   ```
   python3 work/amflow/amflow.py install "Backup harian.flow.xml" --restart
   ```
   Perintah ini membuat backup `flows.xml_amflow_<timestamp>.bak` lebih dulu.

## Aturan keamanan

- **Jangan pernah** menimpa `flows.xml` secara manual; selalu lewat `install`.
- Jangan mengubah atau menghapus flow milik user. Hanya menambah flow baru.
- Flow baru selalu `<enabled>false</enabled>`. Biarkan user mengaktifkannya sendiri.
- Jangan memasang flow yang memakai kredensial (API key, password) tanpa izin eksplisit;
  nilai itu tersimpan sebagai teks biasa di `flows.xml`.
- Jika validasi gagal, jangan pasang. Tunjukkan error ke user.
- Jika komponen tidak punya `tags` di skema, baca dokumentasinya sebelum memakai tag apa pun.

## Struktur flow Automagic (ringkas)

```xml
<data version="1.38.0">
  <flow type="flow">
    <name>Nama flow</name>
    <group>Custom</group>
    <enabled>false</enabled>
    <executionPolicy>PARALLEL</executionPolicy>

    <triggercontainer id="t1" x="70.0" y="120.0">
      <trigger>Nama tampilan trigger</trigger>   <!-- child element -->
    </triggercontainer>
    <conditioncontainer id="t2" x="70.0" y="240.0">Nama tampilan kondisi</conditioncontainer>
    <actioncontainer id="t3" x="70.0" y="360.0">Nama tampilan aksi</actioncontainer>

    <connection from="t1" to="t2" type="NORMAL" sourcePosition="SOUTH" targetPosition="NORTH"/>
    <connection from="t2" to="t3" type="TRUE"   sourcePosition="SOUTH" targetPosition="NORTH"/>
  </flow>

  <!-- definisi setting, dihubungkan lewat <name> -->
  <trigger type="time"><name>Nama tampilan trigger</name> ...</trigger>
  <condition type="expression"><name>Nama tampilan kondisi</name> ...</condition>
  <action type="http_request"><name>Nama tampilan aksi</name> ...</action>
</data>
```

Poin penting:

- **Definisi komponen WAJIB ditulis sebelum `<flow>`.** Automagic me-resolve nama
  container saat parsing; kalau definisi ada di belakang, container jadi kosong dan
  tidak bisa diedit. `amflow` sudah menata ulang otomatis, jangan diubah manual.
- `actioncontainer` / `conditioncontainer` menyimpan nama sebagai **teks elemen**.
- `triggercontainer` menyimpan nama sebagai **child `<trigger>`** (boleh lebih dari satu).
- Nama komponen harus unik **per kategori**; trigger dan condition boleh bernama sama.
- `connection` tipe: `NORMAL`, `TRUE` (dari condition), `FALSE`.
- `triggercontainer` kosong = flow dijalankan manual.

## Perintah yang tersedia

| Perintah | Fungsi |
| --- | --- |
| `docs <kata>` | cari dokumentasi komponen |
| `list [trigger\|condition\|action]` | daftar ID komponen |
| `component <id>` | tag, tipe, dan contoh komponen |
| `new <nama>` | buat file flow kosong |
| `add <file> <id>` | tambah komponen + container + koneksi |
| `validate <file>` | cek struktur, tag, koneksi, keterjangkauan |
| `install <file> [--replace] [--restart]` | backup + gabung ke flows.xml |
| `agent.py "<permintaan>" [--install]` | rancang flow dengan Gemini (multi API key) |

## Batasan yang perlu disampaikan ke user

- Skema diekstrak otomatis; sebagian komponen (khususnya condition) belum punya daftar tag.
- Validator tidak tahu tag mana yang **wajib** secara fungsional; memakai `--from-example`
  lebih aman untuk komponen yang punya contoh.
- Automagic tidak memuat ulang flow saat berjalan; perlu `--restart` atau buka ulang app.
- Beberapa aksi butuh izin runtime (SMS, lokasi, aksesibilitas) yang tidak bisa diberikan agent.

## Integritas flows.xml

Automagic menolak `flows.xml` yang diubah di luar aplikasi ("The flow definitions
have been modified outside of Automagic"). Berkas penjaganya:

```
flow_check = SHA1("89389812312" + isi flows.xml)   # hex, tanpa newline
```

`amflow install` menulis ulang `flow_check` otomatis. Kalau mengedit manual, hitung
ulang nilai ini, jika tidak Automagic akan menonaktifkan semua flow.

**Penting:** Automagic memakai `/sdcard/Automagic/flows.xml` sebagai berkas aktif
(`files/flows.xml` hanya salinan). Keduanya harus berisi isi yang sama. Selain itu
`am force-stop` tidak selalu mematikan proses di sebagian ROM: matikan dengan
`kill -9 $(pidof ch.gridvision.ppam.androidautomagic)` sebelum menulis, kalau tidak
aplikasi akan menulis daftar flow dari memori dan menimpa perubahan.

## Agent (Gemini, BYOK, multi-key)

```bash
python3 work/amflow/agent.py "setiap jam 7 pagi kirim status WA: selamat pagi" \
    --keys keys.txt --install
```

- `keys.txt`: satu API key per baris (boleh juga `GEMINI_API_KEYS=k1,k2`).
- Key yang kena limit (HTTP 429) otomatis dilewati dan istirahat 30 menit;
  key tidak valid 24 jam. State di `.keys_state.json`.
- Alur: pilih komponen → susun XML → validasi → minta model memperbaiki → tulis file.
- `--endpoint` bisa diarahkan ke server tiruan untuk pengujian (`mock_gemini.py`).
