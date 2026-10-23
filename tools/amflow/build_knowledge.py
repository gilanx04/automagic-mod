#!/usr/bin/env python3
"""
Membangun berkas pengetahuan untuk AI flow agent.

Hasil (dipasang ke files/amagent/ di data aplikasi):
  catalog.txt   - daftar komponen ringkas untuk prompt (kategori|id|nama)
  catalog.json  - id -> {name, tags, example}
  docs_index.json - halaman -> {title, text} untuk pencarian dokumentasi
"""

from __future__ import annotations

import json
import os
import re
import sys
import html as html_mod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = HERE / "schema.json"
DOCS_SRC = ROOT / "automagic-help"
HELP_OUT = Path(os.environ.get("AMFLOW_DOCS", str(ROOT / "work" / "docs" / "help-out")))
OUT = ROOT / "work" / "docs" / "agent-out"


def strip_html(text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_mod.unescape(text)
    return re.sub(r"[ \t]+", " ", text).strip()


def build_catalog(schema: dict) -> tuple[str, dict]:
    lines = ["# format: kategori|id|nama"]
    catalog: dict[str, dict] = {"trigger": {}, "condition": {}, "action": {}}
    for cat in ("trigger", "condition", "action"):
        for ident, entry in sorted(schema["components"][cat].items()):
            lines.append(f"{cat}|{ident}|{entry['name']}")
            catalog[cat][ident] = {
                "name": entry["name"],
                "tags": entry.get("tags") or {},
            }
            if entry.get("example"):
                catalog[cat][ident]["example"] = entry["example"]
    return "\n".join(lines) + "\n", catalog


def build_docs_index() -> dict:
    index: dict[str, dict] = {}
    for lang_dir in (HELP_OUT / "en",):
        if not lang_dir.exists():
            continue
        for path in sorted(lang_dir.glob("*.html")):
            if path.stem in ("index",):
                continue
            raw = path.read_text(encoding="utf-8", errors="replace")
            title = ""
            m = re.search(r"<title>([^<]*)</title>", raw)
            if m:
                title = m.group(1).strip()
            body = raw.split("<body>", 1)[-1]
            text = strip_html(body)
            text = re.sub(r"\n{2,}", "\n", text)
            index[path.stem] = {"title": title, "text": text[:6000]}
    return index


def main() -> int:
    if not SCHEMA.exists():
        print("schema.json belum ada; jalankan extract_schema.py", file=sys.stderr)
        return 1
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    catalog_txt, catalog_json = build_catalog(schema)
    (OUT / "catalog.txt").write_text(catalog_txt, encoding="utf-8")
    (OUT / "catalog.json").write_text(
        json.dumps(catalog_json, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8")

    index = build_docs_index()
    (OUT / "docs_index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    print(f"catalog.txt     : {len(catalog_txt.splitlines()) - 1} komponen, "
          f"{(OUT / 'catalog.txt').stat().st_size // 1024} KB")
    print(f"catalog.json    : {(OUT / 'catalog.json').stat().st_size // 1024} KB")
    print(f"docs_index.json : {len(index)} halaman, "
          f"{(OUT / 'docs_index.json').stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
