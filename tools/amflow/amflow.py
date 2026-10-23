#!/usr/bin/env python3
"""
amflow - tool untuk membuat, memvalidasi dan memasang flow Automagic.

Dipakai oleh AI agent (atau manusia) sebagai "tangan" saat merancang flow:
  amflow.py list action
  amflow.py docs "kirim file ke ftp"
  amflow.py component http_request
  amflow.py new "Backup harian"
  amflow.py add "Backup harian.flow.xml" http_request --set url=... --set httpMethod=POST
  amflow.py validate "Backup harian.flow.xml"
  amflow.py install "Backup harian.flow.xml"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA_PATH = HERE / "schema.json"
DOCS = ROOT / "automagic-help"
PKG = "ch.gridvision.ppam.androidautomagic"
# Automagic membaca flow dari penyimpanan internal; /sdcard hanya salinan/mirror.
INTERNAL_FLOWS = Path(f"/data/data/{PKG}/files/flows.xml")
# Automagic menolak flows.xml yang diubah di luar aplikasi kecuali berkas ini cocok:
#   flow_check = SHA1("89389812312" + isi flows.xml)
FLOW_CHECK = Path(f"/data/data/{PKG}/files/flow_check")
FLOW_CHECK_SALT = b"89389812312"
MIRROR_FLOWS = Path("/sdcard/Automagic/flows.xml")
DEVICE_FLOWS = Path(os.environ.get("AMFLOW_TARGET", str(INTERNAL_FLOWS)))
CONTAINER = {"trigger": "triggercontainer", "condition": "conditioncontainer",
             "action": "actioncontainer"}
CATEGORIES = ("trigger", "condition", "action")


def load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        sys.exit("schema.json belum ada, jalankan: python3 extract_schema.py")
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ docs
def doc_files() -> list[Path]:
    return sorted(DOCS.rglob("*.md"))


def cmd_docs(args) -> int:
    terms = [t.lower() for t in args.query.split() if t]
    scored = []
    for path in doc_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        title = ""
        m = re.search(r"^title:\s*\"?([^\"\n]+)", text, re.M)
        if m:
            title = m.group(1)
        score = sum(low.count(t) for t in terms)
        if terms and all(t in low for t in terms):
            score += 10
        if score:
            first = next((ln for ln in text.splitlines()
                          if any(t in ln.lower() for t in terms)), "")
            scored.append((score, path, title, first.strip()[:160]))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("tidak ada dokumen yang cocok")
        return 1
    for score, path, title, snippet in scored[:args.limit]:
        rel = path.relative_to(DOCS)
        print(f"[{score:>3}] {rel}")
        if title:
            print(f"      {title}")
        if snippet:
            print(f"      {snippet}")
    return 0


# ------------------------------------------------------------------ schema
def cmd_list(args) -> int:
    schema = load_schema()
    cats = [args.category] if args.category else list(CATEGORIES)
    for cat in cats:
        items = schema["components"][cat]
        print(f"# {cat} ({len(items)})")
        for ident, entry in sorted(items.items()):
            print(f"  {ident:<40} {entry['name']}")
    return 0


def cmd_component(args) -> int:
    schema = load_schema()
    for cat in CATEGORIES:
        entry = schema["components"][cat].get(args.id)
        if not entry:
            continue
        print(f"{cat}: {args.id}  ({entry['name']})")
        print(f"class: {entry['class']}")
        if entry.get("tags"):
            print("tags:")
            for tag, typ in entry["tags"].items():
                print(f"  {tag:<28} {typ}")
        else:
            print("tags: (tidak terdeteksi, lihat dokumentasi)")
        if entry.get("example"):
            print("contoh:")
            print(entry["example"])
        return 0
    print(f"komponen '{args.id}' tidak ditemukan")
    return 1


# ------------------------------------------------------------------ flow build
def new_flow(name: str, group: str = "Custom", enabled: bool = False) -> ET.Element:
    flow = ET.Element("flow", {"type": "flow"})
    for tag, text in (("name", name), ("group", group),
                      ("enabled", "true" if enabled else "false"),
                      ("lastExecutionStartTime", "0"), ("lastExecutionEndTime", "0"),
                      ("executionPolicy", "PARALLEL")):
        ET.SubElement(flow, tag).text = text
    return flow


def next_container_id(flow: ET.Element) -> str:
    used = {c.get("id") for c in flow if c.tag.endswith("container")}
    i = 1
    while f"t{i}" in used:
        i += 1
    return f"t{i}"


def add_component(flow: ET.Element, defs: ET.Element, category: str, ident: str,
                  values: dict[str, str], display: str | None, schema: dict) -> ET.Element:
    entry = schema["components"][category].get(ident)
    if entry is None:
        raise SystemExit(f"komponen {category} '{ident}' tidak ada di schema")

    display = display or entry["name"]
    names = {d.findtext("name") for d in defs if d.tag == category}
    if display in names:
        display = f"{display} ({ident})"

    definition = ET.SubElement(defs, category, {"type": ident})
    ET.SubElement(definition, "useDefaultName").text = "false"
    ET.SubElement(definition, "name").text = display
    if category == "trigger":
        ET.SubElement(definition, "enabled").text = "true"
    for key, value in values.items():
        if isinstance(value, list):
            for item in value:
                ET.SubElement(definition, key).text = item
        else:
            ET.SubElement(definition, key).text = value

    cid = next_container_id(flow)
    container = ET.SubElement(flow, CONTAINER[category],
                              {"id": cid, "x": "70.0",
                               "y": str(120.0 * (len(flow.findall('.//*')) + 1))})
    if category == "trigger":
        # triggercontainer menyimpan nama sebagai child <trigger>
        ET.SubElement(container, "trigger").text = display
    else:
        # actioncontainer / conditioncontainer menyimpan nama sebagai teks
        container.text = display
    return container


def connect(flow: ET.Element, src: str, dst: str, kind: str = "NORMAL") -> None:
    ET.SubElement(flow, "connection", {
        "from": src, "to": dst, "type": kind,
        "sourcePosition": "SOUTH", "targetPosition": "NORTH"})


def load_doc(path: Path) -> ET.Element:
    root = ET.parse(path).getroot()
    return root


def cmd_new(args) -> int:
    out = Path(args.file)
    root = ET.Element("data", {"version": "1.38.0"})
    root.append(new_flow(args.name, args.group, args.enable))
    write(root, out)
    print(f"dibuat: {out}")
    return 0


def normalize_order(root: ET.Element) -> None:
    """Automagic me-resolve container saat parsing, jadi definisi komponen harus
    berada SEBELUM elemen <flow> (sama seperti berkas yang ditulis aplikasi)."""
    children = list(root)
    defs = [c for c in children if c.tag != "flow"]
    flows = [c for c in children if c.tag == "flow"]
    ordered = defs + flows
    if ordered != children:
        for c in children:
            root.remove(c)
        for c in ordered:
            root.append(c)


def write(root: ET.Element, path: Path) -> None:
    normalize_order(root)
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode")
    path.write_text("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n" + body,
                    encoding="utf-8")


def cmd_add(args) -> int:
    schema = load_schema()
    path = Path(args.file)
    root = load_doc(path)
    flow = root.find("flow")
    if flow is None:
        sys.exit("file tidak berisi <flow>")

    values = {}
    if args.from_example:
        entry = schema["components"][args.category].get(args.id) or {}
        if not entry.get("example"):
            print(f"peringatan: {args.id} tidak punya contoh di schema")
        else:
            ex = ET.fromstring(entry["example"])
            for child in ex:
                if child.tag in ("useDefaultName", "name", "enabled"):
                    continue
                if child.text is not None:
                    values.setdefault(child.tag, [])
                    if isinstance(values[child.tag], list):
                        values[child.tag].append(child.text)
                    else:
                        values[child.tag] = [values[child.tag], child.text]

    for item in args.set or []:
        if "=" not in item:
            sys.exit(f"--set harus key=value, dapat: {item}")
        k, v = item.split("=", 1)
        values[k] = v  # menimpa nilai dari contoh

    before = {c.get("id") for c in flow if c.tag.endswith("container")}
    container = add_component(flow, root, args.category, args.id, values, args.display, schema)
    new_id = container.get("id")

    # sambungkan otomatis ke node terakhir (rantai linear)
    if before:
        prev = list(before)[-1]
        connect(flow, prev, new_id)

    write(root, path)
    label = container.findtext(args.category) or (container.text or "").strip()
    print(f"{args.category} {args.id} -> {new_id} ({label})")
    return 0


# ------------------------------------------------------------------ validate
def validate(root: ET.Element, schema: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    defs: dict[str, list[ET.Element]] = {c: [] for c in CATEGORIES}
    for cat in CATEGORIES:
        defs[cat] = list(root.findall(cat))

    # nama hanya unik per kategori; trigger dan condition boleh bernama sama
    by_name: dict[tuple[str, str], ET.Element] = {}
    for cat in CATEGORIES:
        for d in defs[cat]:
            name = d.findtext("name")
            if not name or not name.strip():
                warnings.append(f"<{cat} type={d.get('type')}> tanpa nama (tidak dipakai)")
                continue
            key = (cat, name.strip())
            if key in by_name:
                errors.append(f"nama {cat} duplikat: '{name.strip()}'")
            by_name[key] = d
            ident = d.get("type")
            entry = schema["components"][cat].get(ident)
            if entry is None:
                errors.append(f"tipe {cat} tidak dikenal: '{ident}'")
                continue
            known = set(entry.get("tags") or {})
            if known:
                for child in d:
                    if child.tag in ("useDefaultName", "name", "enabled"):
                        continue
                    if child.tag not in known:
                        warnings.append(
                            f"{ident}: tag '{child.tag}' tidak ada di skema "
                            f"(mungkin tetap valid)")

    used_names: set[str] = set()
    flows = root.findall("flow")
    if not flows:
        errors.append("tidak ada <flow>")

    for flow in flows:
        fname = flow.findtext("name") or "(tanpa nama)"
        containers = [c for c in flow if c.tag.endswith("container")]
        ids = {c.get("id") for c in containers}
        triggers = [c for c in containers if c.tag == "triggercontainer"]
        if len(triggers) > 1:
            warnings.append(f"flow '{fname}': {len(triggers)} trigger")

        for c in containers:
            cat = c.tag.replace("container", "")
            if cat not in CATEGORIES:
                errors.append(f"flow '{fname}': container tidak dikenal {c.tag}")
                continue
            refs = [el.text.strip() for el in c.findall(cat) if el.text and el.text.strip()]
            if not refs and (c.text or "").strip():
                refs = [c.text.strip()]
            if not refs:
                if c.tag == "triggercontainer":
                    warnings.append(f"flow '{fname}': tanpa trigger (dijalankan manual)")
                else:
                    errors.append(
                        f"flow '{fname}': {c.get('id')} tidak mereferensikan komponen")
            for ref in refs:
                used_names.add((cat, ref))
                d = by_name.get((cat, ref))
                if d is None:
                    errors.append(f"flow '{fname}': {cat} '{ref}' tidak punya definisi")

        edges = []
        for conn in flow.findall("connection"):
            src, dst = conn.get("from"), conn.get("to")
            for node in (src, dst):
                if node not in ids:
                    errors.append(f"flow '{fname}': connection ke id tak dikenal '{node}'")
            if src and dst:
                edges.append((src, dst))
            if conn.get("type") not in ("NORMAL", "TRUE", "FALSE"):
                warnings.append(f"flow '{fname}': tipe connection '{conn.get('type')}'")

        # keterjangkauan dari trigger
        if triggers:
            reachable, queue = set(), [triggers[0].get("id")]
            while queue:
                node = queue.pop()
                if node in reachable:
                    continue
                reachable.add(node)
                queue += [d for s, d in edges if s == node]
            unreachable = ids - reachable
            if unreachable:
                warnings.append(f"flow '{fname}': node tidak terhubung: "
                                f"{', '.join(sorted(unreachable))}")

    orphans = set(by_name) - used_names
    if orphans:
        preview = ", ".join(f"{c}:{n}" for c, n in sorted(orphans)[:8])
        warnings.append(f"{len(orphans)} komponen tidak dipakai flow mana pun ({preview}...)")
    return errors, warnings


def cmd_validate(args) -> int:
    schema = load_schema()
    root = load_doc(Path(args.file))
    errors, warnings = validate(root, schema)
    for w in warnings:
        print(f"peringatan: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\n{len(errors)} error, {len(warnings)} peringatan")
        return 1
    print(f"valid ({len(warnings)} peringatan)")
    return 0


# ------------------------------------------------------------------ install
def su(cmd: str) -> str:
    return subprocess.run(["su", "-c", cmd], capture_output=True, text=True).stdout


def su_ok(cmd: str) -> bool:
    return subprocess.run(["su", "-c", cmd], capture_output=True).returncode == 0


def read_device(path: Path) -> bytes:
    """Baca berkas milik aplikasi lewat root."""
    if path.exists() and os.access(path, os.R_OK):
        return path.read_bytes()
    return subprocess.run(["su", "-c", f"cat {path}"], capture_output=True).stdout


def write_device(src: Path, dst: Path) -> None:
    su(f"cp {src} {dst}")
    owner = su(f"stat -c %u:%g /data/data/{PKG}").strip()
    if owner:
        su(f"chown {owner} {dst}")


def flow_check_hash(data: bytes) -> str:
    digest = hashlib.sha1()
    digest.update(FLOW_CHECK_SALT)
    digest.update(data)
    return digest.hexdigest()


def write_flow_check(flows_path: Path) -> str:
    """Perbarui flow_check agar Automagic menerima flows.xml hasil edit eksternal."""
    data = read_device(flows_path)
    value = flow_check_hash(data)
    tmp = Path("/data/data/com.termux/files/home/.tmp/amflow_flow_check")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(value, encoding="utf-8")
    su(f"cp {tmp} {FLOW_CHECK}")
    owner = su(f"stat -c %u:%g /data/data/{PKG}").strip()
    if owner:
        su(f"chown {owner} {FLOW_CHECK}")
    return value


def cmd_install(args) -> int:
    schema = load_schema()
    src = Path(args.file)
    root = load_doc(src)
    errors, warnings = validate(root, schema)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print("dibatalkan: flow belum valid")
        return 1
    for w in warnings:
        print(f"peringatan: {w}")

    if not su_ok(f"test -f {DEVICE_FLOWS}"):
        sys.exit(f"{DEVICE_FLOWS} tidak ada")

    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = DEVICE_FLOWS.with_name(f"flows.xml_amflow_{stamp}.bak")
    su(f"cp {DEVICE_FLOWS} {backup}")
    print(f"backup: {backup}")

    merged = ET.fromstring(read_device(DEVICE_FLOWS))
    existing = {}
    for f in merged.findall("flow"):
        existing[f.findtext("name")] = f

    new_flows = []
    for flow in root.findall("flow"):
        name = flow.findtext("name")
        if name in existing:
            if not args.replace:
                print(f"dilewati, flow dengan nama sama sudah ada: {name} "
                      f"(pakai --replace untuk menimpa)")
                continue
            merged.remove(existing[name])
            print(f"diganti: {name}")
        new_flows.append(flow)

    # buang definisi lama dengan nama yang sama agar tidak duplikat
    replace_names = set()
    for cat in CATEGORIES:
        for d in root.findall(cat):
            n = d.findtext("name")
            if n:
                replace_names.add((cat, n.strip()))
    for cat in CATEGORIES:
        for d in list(merged.findall(cat)):
            n = d.findtext("name")
            if n and (cat, n.strip()) in replace_names:
                merged.remove(d)

    # definisi dulu (sebelum <flow> pertama), baru flow
    insert_at = 0
    for idx, child in enumerate(list(merged)):
        if child.tag == "flow":
            insert_at = idx
            break
    else:
        insert_at = len(list(merged))

    new_defs = [d for cat in CATEGORIES for d in root.findall(cat)]
    for offset, d in enumerate(new_defs):
        merged.insert(insert_at + offset, d)

    for flow in new_flows:
        merged.append(flow)

    tmp = Path("/data/data/com.termux/files/home/.tmp/amflow_merge.xml")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    write(merged, tmp)

    write_device(tmp, DEVICE_FLOWS)
    check = write_flow_check(DEVICE_FLOWS)
    print(f"flow_check: {check}")
    if DEVICE_FLOWS != MIRROR_FLOWS and su_ok(f"test -d {MIRROR_FLOWS.parent}"):
        su(f"cp {DEVICE_FLOWS} {MIRROR_FLOWS}")
        su(f"chown media_rw:media_rw {MIRROR_FLOWS}")
    print(f"terpasang: {len(new_flows)} flow baru -> {DEVICE_FLOWS}")

    if args.restart:
        # "am force-stop" tidak selalu mematikan proses di beberapa ROM; kill -9 agar
        # Automagic memuat ulang flows.xml dari disk (kalau tidak, daftar lama ditulis balik).
        for _ in range(5):
            pid = su(f"pidof {PKG}").strip()
            if not pid:
                break
            su(f"kill -9 {pid}")
            time.sleep(1)
        print("Automagic dihentikan, buka lagi untuk memuat flow")
    return 0


# ------------------------------------------------------------------ main
def main() -> int:
    parser = argparse.ArgumentParser(prog="amflow", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("docs", help="cari dokumentasi komponen")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_docs)

    p = sub.add_parser("list", help="daftar komponen")
    p.add_argument("category", nargs="?", choices=CATEGORIES)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("component", help="detail satu komponen")
    p.add_argument("id")
    p.set_defaults(func=cmd_component)

    p = sub.add_parser("new", help="buat file flow baru")
    p.add_argument("name")
    p.add_argument("--group", default="Custom")
    p.add_argument("--file", default=None)
    p.add_argument("--enable", action="store_true",
                   help="langsung aktifkan flow (default: nonaktif)")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("add", help="tambah komponen ke flow")
    p.add_argument("file")
    p.add_argument("id")
    p.add_argument("--category", choices=CATEGORIES, default="action")
    p.add_argument("--display", default=None)
    p.add_argument("--set", action="append", metavar="TAG=VALUE")
    p.add_argument("--from-example", action="store_true",
                   help="mulai dari contoh nyata di flows.xml")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("validate", help="validasi file flow")
    p.add_argument("file")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("install", help="pasang flow ke Automagic")
    p.add_argument("file")
    p.add_argument("--restart", action="store_true")
    p.add_argument("--replace", action="store_true",
                   help="timpa flow dengan nama yang sama")
    p.set_defaults(func=cmd_install)

    args = parser.parse_args()
    if args.command == "new" and not args.file:
        args.file = f"{args.name}.flow.xml"
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
