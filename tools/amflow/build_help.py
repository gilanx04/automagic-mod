#!/usr/bin/env python3
"""
Membangun dokumentasi offline Automagic dari arsip markdown.

Sumber : automagic-help/catalog/{actions,triggers,conditions}/*.md,
         automagic-help/help/*.md, automagic-help/reference/*.md
Hasil  : <out>/<lang>/<page>.html + assets/ + version.txt

Struktur ini persis yang dicari HelpActivity:
    files/help/<lang>/<page>.html      -> dimuat sebagai file://
    files/help/<lang>/version.txt      -> harus berisi "1.38"
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "automagic-help"
OUT = ROOT / "work" / "docs" / "help-out"
NO_IMAGES = False
VERSION = "1.38"

CSS = """
:root { color-scheme: dark; }
body { background:#000; color:#ddd; font:16px/1.6 -apple-system,Roboto,sans-serif;
       margin:0; padding:16px 18px 48px; }
h1 { color:#fff; font-size:1.5em; border-bottom:1px solid #333; padding-bottom:.3em; }
h2 { color:#8ec07c; font-size:1.2em; margin-top:1.6em; }
h3 { color:#83a598; font-size:1.05em; margin-top:1.3em; }
a { color:#7aa2f7; text-decoration:none; }
a:hover { text-decoration:underline; }
code { background:#1d2021; color:#fabd2f; padding:1px 5px; border-radius:3px;
       font-family:monospace; font-size:.92em; }
pre { background:#141414; border:1px solid #2a2a2a; border-radius:6px; padding:12px;
      overflow-x:auto; }
pre code { background:none; color:#d5c4a1; padding:0; }
img { max-width:100%; height:auto; border:1px solid #2a2a2a; border-radius:6px;
      margin:8px 0; }
blockquote { border-left:3px solid #444; margin-left:0; padding-left:14px; color:#aaa; }
table { border-collapse:collapse; width:100%; margin:12px 0; }
th, td { border:1px solid #333; padding:6px 9px; text-align:left; vertical-align:top; }
th { background:#1d2021; }
ul, ol { padding-left:1.5em; }
hr { border:0; border-top:1px solid #333; margin:24px 0; }
.nav { font-size:.9em; color:#888; margin-bottom:18px; }
""".strip()


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def inline(text: str) -> str:
    """Inline markdown -> html (code, bold, italic, links, images)."""
    # simpan inline code agar tidak diproses lagi
    slots: list[str] = []

    def keep_code(m: re.Match) -> str:
        slots.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(slots) - 1}\x00"

    text = re.sub(r"`([^`\n]+)`", keep_code, text)

    # gambar ![alt](src)
    def img(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2)
        return f'<img src="{rewrite_href(src)}" alt="{html.escape(alt)}">'

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, text)

    # link [text](target)
    def link(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        return f'<a href="{rewrite_href(target)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", text)
    text = html.escape(text, quote=False)
    # html.escape merusak tag yang sudah kita buat -> kembalikan
    text = (text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
                .replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
                .replace("&lt;a href=&quot;", '<a href="')
                .replace("&quot;&gt;", '">')
                .replace("&lt;/a&gt;", "</a>")
                .replace("&lt;img src=&quot;", '<img src="')
                .replace("&quot; alt=&quot;", '" alt="')
                .replace("&quot;&gt;", '">'))
    text = re.sub(r"&amp;", "&", text)

    for i, code in enumerate(slots):
        text = text.replace(f"\x00{i}\x00", code)
    return text


def rewrite_href(target: str) -> str:
    if re.match(r"^[a-z]+://", target):
        return target
    if target.startswith("#"):
        return target
    target = target.replace("../assets/", "assets/")
    target = re.sub(r"\.md(#|$)", r".html\1", target)
    return target


def convert(md: str) -> tuple[str, str]:
    """Kembalikan (title, body_html)."""
    md = strip_front_matter(md)
    lines = md.split("\n")
    out: list[str] = []
    title = ""
    i = 0
    list_stack: list[str] = []
    in_code = False
    code_buf: list[str] = []
    para: list[str] = []
    table_buf: list[str] = []

    def close_list() -> None:
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    def flush_para() -> None:
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_table() -> None:
        if not table_buf:
            return
        rows = [r for r in table_buf if r.strip()]
        table_buf.clear()
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        if len(cells) >= 2 and all(set(c) <= set("-: ") for c in cells[1]):
            head, body = cells[0], cells[2:]
        else:
            head, body = cells[0], cells[1:]
        out.append("<table><thead><tr>"
                   + "".join(f"<th>{inline(c)}</th>" for c in head)
                   + "</tr></thead><tbody>")
        for row in body:
            out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
        out.append("</tbody></table>")

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            flush_para()
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf.clear()
                in_code = False
            else:
                close_list()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("|") and line.strip().endswith("|"):
            flush_para()
            close_list()
            table_buf.append(line)
            i += 1
            continue
        flush_table()

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush_para()
            close_list()
            level = len(m.group(1))
            text = inline(m.group(2).strip())
            if level == 1 and not title:
                title = re.sub(r"<[^>]+>", "", text)
            out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        if re.match(r"^\s*([-*+])\s+", line):
            flush_para()
            if not list_stack or list_stack[-1] != "ul":
                close_list()
                out.append("<ul>")
                list_stack.append("ul")
            out.append("<li>" + inline(re.sub(r"^\s*[-*+]\s+", "", line)) + "</li>")
            i += 1
            continue

        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_para()
            if not list_stack or list_stack[-1] != "ol":
                close_list()
                out.append("<ol>")
                list_stack.append("ol")
            out.append("<li>" + inline(m.group(1)) + "</li>")
            i += 1
            continue

        if re.match(r"^\s*>\s?", line):
            flush_para()
            close_list()
            out.append("<blockquote>" + inline(re.sub(r"^\s*>\s?", "", line)) + "</blockquote>")
            i += 1
            continue

        if re.match(r"^\s*(---+|\*\*\*+)\s*$", line):
            flush_para()
            close_list()
            out.append("<hr>")
            i += 1
            continue

        if not line.strip():
            flush_para()
            close_list()
            i += 1
            continue

        para.append(line.strip())
        i += 1

    flush_para()
    flush_table()
    close_list()
    if in_code and code_buf:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    return title, "\n".join(out)


def strip_images(body: str) -> str:
    """Buang tag <img> (varian tanpa screenshot agar tidak ada ikon rusak)."""
    import re as _re
    return _re.sub(r"<img[^>]*>", "", body)


def page(title: str, body: str) -> str:
    if NO_IMAGES:
        body = strip_images(body)
    return (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
        f"<body>{body}</body></html>"
    )


CUSTOM_PAGES = {
    "action_wa_reply": ("Action - Reply to WhatsApp Message", """
<p>Balas pesan WhatsApp langsung dari notifikasi memakai <code>RemoteInput</code>,
tanpa membuka aplikasi.</p>
<h2>Pengaturan</h2>
<ul>
<li><b>Message</b> — teks balasan, mendukung variabel <code>{...}</code>.</li>
</ul>
<h2>Variabel</h2>
<p><code>{wa_sender}</code>, <code>{wa_message}</code>, <code>{wa_is_group}</code>,
<code>{wa_group}</code>, <code>{wa_conversation}</code>, <code>{wa_package}</code>.</p>
<h2>Catatan</h2>
<p>Action harus dijalankan tepat setelah trigger <b>WhatsApp Message Received</b>,
karena memakai notifikasi sebagai sumber action balasan.</p>
"""),
    "action_wa_gemini_reply": ("Action - Reply with Google Gemini", """
<p>Mengirim prompt ke Google Gemini lalu membalas pesan WhatsApp dengan hasilnya.</p>
<h2>Endpoint</h2>
<pre><code>POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
x-goog-api-key: &lt;API key&gt;</code></pre>
<h2>Placeholder pesan</h2>
<p><code>%message%</code>, <code>%message_512%</code>, <code>%prev_message_0_1_512%</code>
(offset 1 = paling baru), <code>%prev_reply_0_1_512%</code>.</p>
<p>Format: <code>%prev_message_&lt;diabaikan&gt;_&lt;offset&gt;_&lt;limit&gt;%</code>. Gunakan
bentuk tiga angka; <code>%prev_message_2_100%</code> berarti offset 100, bukan offset 2 limit 100.</p>
<h2>Placeholder memori &amp; waktu</h2>
<table>
<tr><th>Placeholder</th><th>Isi</th></tr>
<tr><td><code>%now%</code></td><td>waktu sekarang, mis. "Jum, 23 Okt 2026 22:55"</td></tr>
<tr><td><code>%last_seen%</code></td><td>kapan terakhir bicara, mis. "3 hari lalu"</td></tr>
<tr><td><code>%memory%</code></td><td>fakta jangka panjang (persona + catatan)</td></tr>
<tr><td><code>%summary%</code></td><td>ringkasan pesan lama yang sudah dipadatkan</td></tr>
</table>
<p>Setiap giliran riwayat diberi label waktu, mis. <code>[2 jam lalu] kamu udah makan?</code>,
sehingga model tahu jeda antar pesan. Bisa dimatikan dengan opsi
<b>Include message timestamps</b>.</p>
<h2>Ringkasan otomatis</h2>
<p><b>Summarize every N messages</b> memadatkan pesan lama menjadi ringkasan
(maksimal 4 kalimat) setiap N pesan. Memakai satu panggilan API tambahan per N pesan.
Isi 0 untuk mematikan. Ringkasan dikirim lewat <code>%summary%</code>.</p>
<h2>Penanda prompt</h2>
<p><code>1::</code> = giliran user, <code>2::</code> = giliran model. Teks sebelum penanda
pertama menjadi system instruction.</p>
<h2>Keamanan</h2>
<p>API key disimpan sebagai teks biasa di flow XML. Jangan bagikan flow yang berisi key.</p>
"""),
    "action_wa_status": ("Action - Post WhatsApp Status", """
<p>Memposting status WhatsApp berisi teks tanpa interaksi pengguna, juga saat layar mati.</p>
<h2>Pengaturan</h2>
<ul><li><b>Status text</b> — teks status, mendukung variabel <code>{...}</code>.</li></ul>
<h2>Kebutuhan</h2>
<p>Memerlukan modul LSPosed <b>Automagic WA Bridge</b> yang aktif untuk WhatsApp.</p>
<h2>Cara kerja</h2>
<p>Action mengirim ordered broadcast ke WhatsApp, modul bridge memanggil composer status
internal, lalu mengembalikan hasil (1 = sukses, 2 = gagal).</p>
<h2>Batasan</h2>
<ul>
<li>Hanya status teks; foto dan video belum didukung.</li>
<li>Audiens mengikuti privasi status terakhir di WhatsApp.</li>
</ul>
"""),
    "action_wa_reset_history": ("Action - Reset Conversation History", """
<p>Menghapus riwayat percakapan yang dipakai placeholder Gemini
(<code>%prev_message_*</code>, <code>%prev_reply_*</code>).</p>
<h2>Pengaturan</h2>
<ul>
<li><b>What to reset</b> — Current conversation (dari trigger), Specific contact, atau All conversations.</li>
<li><b>Contact / conversation</b> — dipakai untuk mode Specific. Mendukung variabel.</li>
<li><b>Package</b> — default <code>com.whatsapp</code>.</li>
</ul>
<h2>Kapan dipakai</h2>
<p>Setelah flow dimatikan lama lalu diaktifkan lagi. Selama flow mati tidak ada pesan yang
tercatat, sehingga konteks yang dikirim ke Gemini menjadi basi dan model cenderung
mengulang pertanyaan lama.</p>
<h2>Hasil</h2>
<p>Jumlah yang dihapus disimpan di <code>{wa_history_status}</code>.</p>
<h2>Catatan</h2>
<p>Riwayat disimpan di SharedPreferences <code>wa_conversation_state</code>, maksimal 30
entri per percakapan. Menghapus riwayat tidak menghapus chat WhatsApp asli.</p>
"""),
    "action_wa_memory": ("Action - Gemini Memory", """
<p>Mengelola memori jangka panjang yang dikirim ke Gemini lewat placeholder
<code>%memory%</code> dan <code>%summary%</code>.</p>
<h2>Aksi</h2>
<table>
<tr><th>Pilihan</th><th>Fungsi</th></tr>
<tr><td>Set a fact</td><td>simpan/ganti satu fakta (key + value)</td></tr>
<tr><td>Remove a fact</td><td>hapus satu fakta berdasarkan key</td></tr>
<tr><td>Clear all facts</td><td>hapus semua fakta</td></tr>
<tr><td>Reset facts + summary</td><td>hapus fakta dan ringkasan</td></tr>
<tr><td>Install built-in persona</td><td>pasang persona bawaan (Gilang) sebagai fakta</td></tr>
<tr><td>Show memory</td><td>tampilkan fakta dan ringkasan</td></tr>
</table>
<h2>Pengaturan lain</h2>
<ul>
<li><b>Fact key</b> / <b>Fact value</b> — untuk aksi set dan remove.</li>
<li><b>Contact / conversation</b> — mendukung <code>{wa_conversation}</code>.</li>
<li><b>Package</b> — default <code>com.whatsapp</code>.</li>
</ul>
<h2>Hasil</h2>
<p>Ringkasan hasil disimpan di <code>{wa_memory_status}</code>.</p>
<h2>Catatan</h2>
<p>Memori disimpan per percakapan di SharedPreferences <code>wa_memory_state</code>.
Fakta bawaan ditandai <code>builtin</code> agar bisa dibedakan dari catatan buatan sendiri.</p>
"""),
    "trigger_wa_message_received": ("Trigger - WhatsApp Message Received", """
<p>Trigger yang berjalan saat notifikasi pesan WhatsApp masuk.</p>
<h2>Pengaturan</h2>
<ul>
<li><b>Message match</b> — Any, Exact, Contains, Pattern/wildcard, Regex, Similarity, Welcome.</li>
<li><b>Chat type filter</b> — semua, direct only, group only.</li>
<li><b>Specific contacts</b> / <b>Ignored contacts</b> — nama, nomor, nama grup, wildcard.</li>
<li><b>Ignore case</b> dan deduplikasi notifikasi.</li>
</ul>
<h2>Variabel</h2>
<p><code>{wa_sender}</code>, <code>{wa_message}</code>, <code>{wa_is_group}</code>,
<code>{wa_group}</code>, <code>{wa_conversation}</code>, <code>{wa_package}</code>,
<code>{wa_match_mode}</code>.</p>
"""),
}


def collect_sources() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for cat, prefix in (("actions", "action_"), ("triggers", "trigger_"),
                        ("conditions", "condition_")):
        for f in sorted((SRC / "catalog" / cat).glob("*.md")):
            if f.stem.startswith(prefix):
                items.append((f.stem, f))
    for f in sorted((SRC / "help").glob("*.md")):
        items.append((f.stem, f))
    for f in sorted((SRC / "reference").glob("*.md")):
        items.append((f.stem, f))
    return items


def build_lang(lang: str, items: list[tuple[str, Path]]) -> int:
    out_dir = OUT / lang
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "assets").mkdir(parents=True)

    count = 0
    index_rows: dict[str, list[tuple[str, str]]] = {
        "Panduan": [], "Trigger": [], "Condition": [], "Action": [], "Referensi": []}

    for stem, path in items:
        title, body = convert(path.read_text(encoding="utf-8"))
        title = title or stem.replace("_", " ").title()
        (out_dir / f"{stem}.html").write_text(page(title, body), encoding="utf-8")
        count += 1

        if stem.startswith("trigger_"):
            index_rows["Trigger"].append((stem, title))
        elif stem.startswith("condition_"):
            index_rows["Condition"].append((stem, title))
        elif stem.startswith("action_"):
            index_rows["Action"].append((stem, title))
        elif path.parent.name == "reference":
            index_rows["Referensi"].append((stem, title))
        else:
            index_rows["Panduan"].append((stem, title))

    for stem, (title, body) in CUSTOM_PAGES.items():
        (out_dir / f"{stem}.html").write_text(page(title, body), encoding="utf-8")
        count += 1
        index_rows["Action" if stem.startswith("action_") else "Trigger"].append((stem, title))

    # halaman indeks
    parts = ["<h1>Dokumentasi Automagic</h1>",
             "<p class=\"nav\">Bantuan offline, versi " + VERSION + ".</p>"]
    for section in ("Panduan", "Trigger", "Condition", "Action", "Referensi"):
        rows = sorted(index_rows[section])
        if not rows:
            continue
        parts.append(f"<h2>{section} ({len(rows)})</h2><ul>")
        for stem, title in rows:
            parts.append(f'<li><a href="{stem}.html">{html.escape(title)}</a></li>')
        parts.append("</ul>")
    (out_dir / "index.html").write_text(page("Dokumentasi Automagic", "\n".join(parts)),
                                        encoding="utf-8")
    count += 1

    if not NO_IMAGES:
        shutil.copytree(SRC / "assets", out_dir / "assets", dirs_exist_ok=True)
    (out_dir / "version.txt").write_text(VERSION, encoding="utf-8")
    return count


def build_catalog(lang: str, items: list[tuple[str, Path]]) -> Path:
    """Katalog komponen, ditautkan ke halaman help offline."""
    groups = {"Trigger": [], "Condition": [], "Action": [], "Panduan & Referensi": []}
    for stem, path in items:
        title, _ = convert(path.read_text(encoding="utf-8"))
        title = title or stem.replace("_", " ").title()
        if stem.startswith("trigger_"):
            groups["Trigger"].append((stem, title))
        elif stem.startswith("condition_"):
            groups["Condition"].append((stem, title))
        elif stem.startswith("action_"):
            groups["Action"].append((stem, title))
        else:
            groups["Panduan & Referensi"].append((stem, title))
    for stem, (title, _) in CUSTOM_PAGES.items():
        groups["Action" if stem.startswith("action_") else "Trigger"].append((stem, title))

    total = sum(len(v) for v in groups.values())
    parts = ["<h1>Katalog Automagic</h1>",
             f"<p class=\"nav\">{total} komponen terdokumentasi. Klik untuk membuka halaman bantuan.</p>"]
    for name in ("Trigger", "Condition", "Action", "Panduan & Referensi"):
        rows = sorted(groups[name])
        if not rows:
            continue
        parts.append(f"<h2>{name} ({len(rows)})</h2><ul>")
        for stem, title in rows:
            parts.append(f'<li><a href="../../help/{lang}/{stem}.html">{html.escape(title)}</a></li>')
        parts.append("</ul>")

    out_dir = OUT / "catalog" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "catalog.html"
    target.write_text(page("Katalog Automagic", "\n".join(parts)), encoding="utf-8")
    return target


def main() -> int:
    global OUT, NO_IMAGES
    if "--no-images" in sys.argv:
        NO_IMAGES = True
        OUT = ROOT / "work" / "docs" / "help-out-nopix"
    items = collect_sources()
    if not items:
        print("sumber dokumentasi tidak ditemukan", file=sys.stderr)
        return 1
    for lang in ("en", "de"):
        n = build_lang(lang, items)
        cat = build_catalog(lang, items)
        print(f"{lang}: {n} halaman -> {OUT / lang}, katalog -> {cat}")
    print(f"total sumber: {len(items)} halaman komponen/panduan/referensi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
