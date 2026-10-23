#!/usr/bin/env python3
"""
amflow agent - merancang flow Automagic dari deskripsi bahasa alami.

Provider: Gemini (BYOK). Beberapa API key didukung; key yang kena limit
dilewati otomatis (rotasi) dan diberi cooldown.

Contoh:
  python3 agent.py "setiap jam 7 pagi kirim status WA: selamat pagi"
  python3 agent.py "..." --keys keys.txt --install
  python3 agent.py "..." --endpoint http://127.0.0.1:8099   # untuk uji lokal
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KNOW = ROOT / "work" / "docs" / "agent-out"
STATE = Path(os.environ.get("AMFLOW_KEY_STATE", str(HERE / ".keys_state.json")))

DEFAULT_MODEL = "gemini-3.5-flash-lite"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
COOLDOWN_LIMIT = 30 * 60
COOLDOWN_INVALID = 24 * 60 * 60

RULES = """Kamu adalah perancang flow Automagic. Balas HANYA dengan format yang diminta.

Struktur file flow:
<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<data version="1.38.0">
  <flow type="flow">
    <name>Nama flow</name>
    <group>Custom</group>
    <enabled>false</enabled>
    <lastExecutionStartTime>0</lastExecutionStartTime>
    <lastExecutionEndTime>0</lastExecutionEndTime>
    <executionPolicy>PARALLEL</executionPolicy>
    <triggercontainer id="t1" x="70.0" y="120.0"><trigger>Nama tampilan</trigger></triggercontainer>
    <actioncontainer id="t2" x="70.0" y="300.0">Nama tampilan aksi</actioncontainer>
    <connection from="t1" to="t2" type="NORMAL" sourcePosition="SOUTH" targetPosition="NORTH"/>
  </flow>
  <trigger type="id_trigger"><useDefaultName>false</useDefaultName><name>Nama tampilan</name><enabled>true</enabled>...</trigger>
  <action type="id_action"><useDefaultName>false</useDefaultName><name>Nama tampilan aksi</name>...</action>
</data>

Aturan wajib:
- actioncontainer dan conditioncontainer menyimpan nama sebagai TEKS elemen.
- triggercontainer menyimpan nama sebagai child <trigger>.
- Nama komponen unik per kategori dan sama persis antara container dan definisi.
- connection type: NORMAL, atau TRUE/FALSE dari condition.
- flow baru selalu <enabled>false</enabled>.
- Hanya pakai komponen dan tag yang diberikan. Jangan mengarang tag.
- id container berurutan: t1, t2, t3, ...
- Jangan menambahkan penjelasan di luar blok kode."""


# ------------------------------------------------------------------ keys
def load_keys(args) -> list[str]:
    keys: list[str] = []
    if args.keys:
        text = Path(args.keys).read_text(encoding="utf-8")
        keys += [ln.strip() for ln in text.splitlines()]
    env = os.environ.get("GEMINI_API_KEYS") or os.environ.get("GEMINI_API_KEY")
    if env:
        keys += re.split(r"[,;\n]", env)
    if args.key:
        keys.append(args.key)
    cleaned = []
    for k in keys:
        k = k.strip().strip('"').strip("'")
        if k and not k.startswith("#") and k not in cleaned:
            cleaned.append(k)
    return cleaned


def key_id(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=1))


def key_ready(state: dict, key: str) -> bool:
    entry = state.get(key_id(key), {})
    return entry.get("until", 0) <= time.time()


def mark_key(state: dict, key: str, seconds: int, reason: str) -> None:
    state[key_id(key)] = {"until": time.time() + seconds, "reason": reason}
    save_state(state)


# ------------------------------------------------------------------ http
class QuotaError(Exception):
    pass


class InvalidKeyError(Exception):
    pass


def call_gemini(endpoint: str, model: str, key: str, prompt: str,
                timeout: int = 120) -> str:
    url = endpoint.format(model=model)
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192},
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-api-key": key,
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        message = raw
        try:
            message = json.loads(raw)["error"]["message"]
        except Exception:
            pass
        low = (message + raw).lower()
        if exc.code == 429 or "quota" in low or "resource_exhausted" in low:
            raise QuotaError(f"HTTP {exc.code}: {message[:200]}") from None
        if "api key not valid" in low or "api_key_invalid" in low or exc.code in (401, 403):
            raise InvalidKeyError(f"HTTP {exc.code}: {message[:200]}") from None
        raise RuntimeError(f"HTTP {exc.code}: {message[:300]}") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"jaringan gagal: {exc.reason}") from None

    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("respons Gemini kosong atau terblokir") from None


def generate_with_rotation(keys: list[str], state: dict, endpoint: str, model: str,
                           prompt: str, verbose: bool = True) -> str:
    if not keys:
        raise SystemExit("tidak ada API key. Isi keys.txt atau set GEMINI_API_KEYS")
    errors = []
    for idx, key in enumerate(keys, 1):
        if not key_ready(state, key):
            if verbose:
                print(f"  key#{idx} cooldown, dilewati")
            continue
        try:
            return call_gemini(endpoint, model, key, prompt)
        except QuotaError as exc:
            mark_key(state, key, COOLDOWN_LIMIT, "limit")
            errors.append(f"key#{idx}: limit")
            if verbose:
                print(f"  key#{idx} kena limit -> rotasi ({exc})")
        except InvalidKeyError as exc:
            mark_key(state, key, COOLDOWN_INVALID, "invalid")
            errors.append(f"key#{idx}: tidak valid")
            if verbose:
                print(f"  key#{idx} tidak valid -> rotasi ({exc})")
    raise SystemExit("semua API key gagal dipakai: " + "; ".join(errors))


# ------------------------------------------------------------------ prompts
def load_knowledge() -> tuple[str, dict, dict]:
    catalog_txt = (KNOW / "catalog.txt").read_text(encoding="utf-8")
    catalog = json.loads((KNOW / "catalog.json").read_text(encoding="utf-8"))
    docs = json.loads((KNOW / "docs_index.json").read_text(encoding="utf-8"))
    return catalog_txt, catalog, docs


def phase_select(request: str, catalog_txt: str, call) -> dict:
    prompt = f"""Pilih komponen Automagic yang diperlukan untuk permintaan user.

{catalog_txt}

Permintaan user:
{request}

Balas HANYA JSON tanpa penjelasan:
{{"trigger": ["id", ...], "condition": ["id", ...], "action": ["id", ...]}}
Gunakan 1 trigger, 0-3 condition, dan 1-6 action. Pilih id persis dari daftar."""
    raw = call(prompt)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise RuntimeError("model tidak mengembalikan JSON komponen")
    data = json.loads(m.group(0))
    return {k: [str(i) for i in data.get(k, [])] for k in ("trigger", "condition", "action")}


def component_details(selected: dict, catalog: dict, docs: dict) -> str:
    parts = []
    for cat in ("trigger", "condition", "action"):
        for ident in selected.get(cat, []):
            entry = catalog.get(cat, {}).get(ident)
            if not entry:
                continue
            block = [f"### {cat} {ident} - {entry['name']}"]
            if entry.get("tags"):
                block.append("tag: " + ", ".join(f"{k}({v})" for k, v in entry["tags"].items()))
            if entry.get("example"):
                block.append("contoh:\n" + entry["example"])
            prefix = {"trigger": "trigger_", "condition": "condition_", "action": "action_"}[cat]
            doc = docs.get(prefix + ident)
            if doc:
                block.append("dokumentasi:\n" + doc["text"][:700])
            parts.append("\n".join(block))
    return "\n\n".join(parts)


def phase_generate(request: str, details: str, call) -> str:
    prompt = f"""{RULES}

Komponen yang tersedia (hanya ini yang boleh dipakai):

{details}

Permintaan user:
{request}

Tulis file flow XML lengkap dalam satu blok kode ```xml."""
    raw = call(prompt)
    m = re.search(r"```(?:xml)?\s*(.*?)```", raw, re.S)
    xml = m.group(1) if m else raw
    if "<data" not in xml:
        raise RuntimeError("model tidak mengembalikan XML flow")
    return xml.strip()


def phase_fix(xml: str, errors: list[str], details: str, call) -> str:
    prompt = f"""{RULES}

Komponen yang boleh dipakai:

{details}

XML berikut tidak valid:
{xml}

Kesalahan:
{chr(10).join('- ' + e for e in errors)}

Perbaiki dan balas XML lengkap dalam satu blok kode ```xml."""
    raw = call(prompt)
    m = re.search(r"```(?:xml)?\s*(.*?)```", raw, re.S)
    return (m.group(1) if m else raw).strip()


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser(prog="agent", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request")
    ap.add_argument("--keys", help="file berisi satu API key per baris")
    ap.add_argument("--key", help="satu API key langsung")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--endpoint", default=ENDPOINT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--fix-attempts", type=int, default=2)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    verbose = not args.quiet

    sys.path.insert(0, str(HERE))
    import amflow  # dipakai untuk validasi + install

    keys = load_keys(args)
    state = load_state()
    catalog_txt, catalog, docs = load_knowledge()

    def call(prompt: str) -> str:
        return generate_with_rotation(keys, state, args.endpoint, args.model, prompt, verbose)

    if verbose:
        print(f"[1/3] memilih komponen ({len(keys)} key tersedia)")
    selected = phase_select(args.request, catalog_txt, call)
    if verbose:
        for cat, ids in selected.items():
            print(f"      {cat}: {', '.join(ids) or '-'}")
    details = component_details(selected, catalog, docs)

    if verbose:
        print("[2/3] menyusun flow")
    xml = phase_generate(args.request, details, call)

    schema = json.loads((HERE / "schema.json").read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else Path(f"agent_{int(time.time())}.flow.xml")
    out.write_text(xml if xml.startswith("<?xml") else
                   "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n" + xml,
                   encoding="utf-8")

    if verbose:
        print("[3/3] validasi")
    import xml.etree.ElementTree as ET
    for attempt in range(args.fix_attempts + 1):
        try:
            root = ET.parse(out).getroot()
        except ET.ParseError as exc:
            errors = [f"XML tidak bisa dibaca: {exc}"]
        else:
            errors, warnings = amflow.validate(root, schema)
        if not errors:
            break
        if attempt == args.fix_attempts:
            print("gagal validasi setelah perbaikan:", file=sys.stderr)
            for e in errors:
                print("  - " + e, file=sys.stderr)
            return 1
        if verbose:
            print(f"      {len(errors)} error -> minta model memperbaiki")
        xml = phase_fix(out.read_text(encoding="utf-8"), errors, details, call)
        out.write_text(xml if xml.startswith("<?xml") else
                       "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n" + xml,
                       encoding="utf-8")

    print(f"flow: {out}")
    for w in warnings[:5]:
        print(f"peringatan: {w}")

    if args.install:
        rc = amflow.cmd_install(argparse.Namespace(file=str(out), restart=True))
        if rc:
            return rc
    else:
        print("(preview saja; tambahkan --install untuk memasang)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
