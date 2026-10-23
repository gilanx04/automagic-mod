#!/usr/bin/env python3
"""
Mengekstrak skema komponen Automagic dari source hasil decompile (jadx) + contoh
nyata dari flows.xml.

Hasil: schema.json
  components.<category>.<id> = {
      name, class, tags: {tag: type}, example: "<action ...>...</action>" (opsional)
  }
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APKTOOL = ROOT / "work" / "am_apktool"
SOURCES = ROOT / "work" / "am" / "sources"
REGISTRY = APKTOOL / "smali/ch/gridvision/ppam/androidautomagic/service/b.smali"
FLOWS = Path("/sdcard/Automagic/flows.xml")
OUT = Path(__file__).resolve().parent / "schema.json"

CATEGORY = {"a": "trigger", "b": "action", "c": "condition"}


# ---------------------------------------------------------------- registry
def parse_registry() -> list[dict]:
    text = REGISTRY.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(
        r"const-class v1, (L[^;]+;)\s*.*?const-string v2, \"([^\"]*)\"\s*.*?"
        r"const-string v3, \"([^\"]*)\"\s*.*?const-string v4, \"([^\"]*)\"\s*.*?"
        r"service/b;->([abc])\(Ljava/lang/Class;",
        text, re.S)
    return [{
        "category": CATEGORY[fn],
        "class": cls[1:-1].replace("/", "."),
        "id": ident,
        "name": en,
    } for cls, ident, en, de, fn in blocks]


# ---------------------------------------------------------------- sources
def load_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for base in (SOURCES, ROOT / "work" / "patch" / "src"):
        if not base.exists():
            continue
        for path in base.rglob("*.java"):
            rel = path.relative_to(base).with_suffix("")
            sources[".".join(rel.parts)] = path.read_text(encoding="utf-8", errors="replace")
    return sources


def build_constants(sources: dict[str, str]) -> dict[str, str]:
    constants: dict[str, str] = {}
    for cls, text in sources.items():
        for m in re.finditer(
                r'static\s+final\s+String\s+(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', text):
            constants[f"{cls}.{m.group(1)}"] = m.group(2)
            constants.setdefault(m.group(1), m.group(2))
    return constants


def parent_of(cls: str, sources: dict[str, str]) -> str | None:
    text = sources.get(cls, "")
    m = re.search(r"class\s+\w+\s+extends\s+([\w.]+)", text)
    if not m:
        return None
    name = m.group(1)
    if "." in name:
        return name
    package = cls.rsplit(".", 1)[0]
    candidate = f"{package}.{name}"
    if candidate in sources:
        return candidate
    for key in sources:
        if key.endswith("." + name):
            return key
    return None


def class_chain(cls: str, sources: dict[str, str]) -> list[str]:
    chain, seen = [], set()
    while cls and cls not in seen:
        seen.add(cls)
        chain.append(cls)
        cls = parent_of(cls, sources)
    return list(reversed(chain))  # induk dulu


def field_types(cls: str, sources: dict[str, str]) -> dict[str, str]:
    types: dict[str, str] = {}
    for c in class_chain(cls, sources):
        for m in re.finditer(
                r"(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?"
                r"(boolean|int|long|float|double|String)\s+(\w+)\s*[=;]", sources.get(c, "")):
            types[m.group(2)] = m.group(1)
    return types


# ---------------------------------------------------------------- serializer
SER_START = re.compile(
    r'startTag\(""\s*,\s*([^)]+?)\)\s*\.text\(([^;]*?)\)\s*\.endTag')


def resolve_tag(expr: str, constants: dict[str, str]) -> str | None:
    expr = expr.strip()
    m = re.fullmatch(r'"((?:[^"\\]|\\.)*)"', expr)
    if m:
        return m.group(1)
    return constants.get(expr)


def resolve_type(value_expr: str, fields: dict[str, str]) -> str:
    value_expr = value_expr.strip()
    if "Integer.toString" in value_expr or "Integer.valueOf" in value_expr:
        return "int"
    if "Long.toString" in value_expr:
        return "long"
    m = re.search(r"this\.(\w+)", value_expr)
    if m:
        return fields.get(m.group(1), "string").lower()
    if value_expr.startswith('"'):
        return "string"
    return "string"


def serializer_tags(cls: str, sources: dict[str, str], constants: dict[str, str]) -> dict[str, str]:
    tags: dict[str, str] = {}
    for c in class_chain(cls, sources):
        text = sources.get(c, "")
        fields = field_types(c, sources)
        for m in re.finditer(
                r"public\s+void\s+a\([^)]*XmlSerializer[^)]*\)\s*(?:throws [\w., ]+)?\{(.*?)\n    \}",
                text, re.S):
            body = m.group(1)
            for sm in SER_START.finditer(body):
                tag = resolve_tag(sm.group(1), constants)
                if not tag:
                    continue
                tags[tag] = resolve_type(sm.group(2), fields)
    return tags


# ---------------------------------------------------------------- examples
def examples_from_flows() -> dict[tuple[str, str], str]:
    if not FLOWS.exists():
        return {}
    try:
        root = ET.parse(FLOWS).getroot()
    except ET.ParseError as exc:
        print(f"flows.xml tidak bisa dibaca: {exc}", file=sys.stderr)
        return {}
    out = {}
    for category in ("trigger", "condition", "action"):
        for el in root.findall(category):
            t = el.get("type")
            if t and (category, t) not in out:
                out[(category, t)] = ET.tostring(el, encoding="unicode").strip()
    return out


def main() -> int:
    registry = parse_registry()
    if not registry:
        print("registry kosong - cek b.smali", file=sys.stderr)
        return 1
    sources = load_sources()
    constants = build_constants(sources)
    examples = examples_from_flows()

    components: dict[str, dict] = {"trigger": {}, "condition": {}, "action": {}}
    no_source = 0
    for item in registry:
        cls = item["class"]
        if cls not in sources:
            no_source += 1
            tags = {}
        else:
            tags = serializer_tags(cls, sources, constants)
        entry = {"name": item["name"], "class": cls, "tags": tags}
        example = examples.get((item["category"], item["id"]))
        if example:
            entry["example"] = example
        components[item["category"]][item["id"]] = entry

    schema = {
        "version": "1.38.0",
        "generated_from": "Automagic 1.38.0 (jadx sources) + flows.xml",
        "counts": {k: len(v) for k, v in components.items()},
        "components": components,
    }
    OUT.write_text(json.dumps(schema, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"schema: {OUT}")
    for k, v in schema["counts"].items():
        with_tags = sum(1 for c in components[k].values() if c["tags"])
        with_example = sum(1 for c in components[k].values() if c.get("example"))
        print(f"  {k}: {v} komponen, {with_tags} punya tag, {with_example} punya contoh")
    if no_source:
        print(f"  peringatan: {no_source} kelas tidak punya source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
