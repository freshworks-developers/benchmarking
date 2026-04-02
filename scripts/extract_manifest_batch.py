#!/usr/bin/env python3
"""Extract manifest (and light file hints) summaries for a batch of benchmark zips.

Writes one JSON file per batch for later merge into unified use-cases CSV.

Usage:
  python3 scripts/extract_manifest_batch.py --batch-spec path/to/batch_N.json
  # batch JSON: {"items": [{"app_id": "493", "zip_file": "app_493_v711945.zip"}, ...]}
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path


def _find_manifest_member(names: list[str]) -> str | None:
    for n in names:
        if n.endswith("manifest.json") and n.count("/") <= 1:
            return n
    for n in names:
        if n.rstrip("/").endswith("manifest.json"):
            return n
    return None


def _zip_read(zf: zipfile.ZipFile, *candidates: str) -> bytes | None:
    for c in candidates:
        try:
            return zf.read(c)
        except KeyError:
            continue
    # fuzzy: endswith
    for name in zf.namelist():
        if name.endswith(candidates[-1].split("/")[-1]) and name.count("/") <= 2:
            try:
                return zf.read(name)
            except KeyError:
                continue
    return None


def _walk_product(manifest: dict) -> dict:
    out: dict = {
        "products": [],
        "locations_by_product": {},
        "events_by_product": {},
        "requests_by_product": {},
        "functions_by_product": {},
        "scheduled_events_by_product": {},
        "whitelisted_domains": manifest.get("whitelisted-domains"),
        "modules": [],
        "locations_by_module": {},
        "events_by_module": {},
        "requests_by_module": {},
        "functions_by_module": {},
        "scheduled_events_by_module": {},
    }
    prod = manifest.get("product") or {}
    if isinstance(prod, dict):
        for pname, pconf in prod.items():
            if not isinstance(pconf, dict):
                continue
            out["products"].append(pname)
            loc = pconf.get("location") or {}
            if isinstance(loc, dict):
                out["locations_by_product"][pname] = sorted(loc.keys())
            ev = pconf.get("events") or {}
            if isinstance(ev, dict):
                nkeys, skeys = [], []
                for k, v in ev.items():
                    if k == "onScheduledEvent":
                        skeys.append(k)
                    else:
                        nkeys.append(k)
                out["events_by_product"][pname] = sorted(nkeys)
                if skeys:
                    out["scheduled_events_by_product"][pname] = sorted(skeys)
            req = pconf.get("requests") or {}
            if isinstance(req, dict):
                out["requests_by_product"][pname] = sorted(req.keys())
            fn = pconf.get("functions") or {}
            if isinstance(fn, dict):
                out["functions_by_product"][pname] = sorted(fn.keys())

    mods = manifest.get("modules") or {}
    if isinstance(mods, dict):
        for mname, mconf in mods.items():
            if not isinstance(mconf, dict):
                continue
            out["modules"].append(mname)
            loc = mconf.get("location") or {}
            if isinstance(loc, dict):
                out["locations_by_module"][mname] = sorted(loc.keys())
            ev = mconf.get("events") or {}
            if isinstance(ev, dict):
                nkeys, skeys = [], []
                for k in ev.keys():
                    if k == "onScheduledEvent":
                        skeys.append(k)
                    else:
                        nkeys.append(k)
                out["events_by_module"][mname] = sorted(nkeys)
                if skeys:
                    out["scheduled_events_by_module"][mname] = sorted(skeys)
            req = mconf.get("requests") or {}
            if isinstance(req, dict):
                out["requests_by_module"][mname] = sorted(req.keys())
            fn = mconf.get("functions") or {}
            if isinstance(fn, dict):
                out["functions_by_module"][mname] = sorted(fn.keys())
    return out


def _scan_text_hints(zf: zipfile.ZipFile) -> dict:
    hints = {
        "has_crayons_mention": False,
        "has_client_data": False,
        "has_smi": False,
        "readme_excerpt": "",
    }
    smi = _zip_read(zf, "smi.json", "./smi.json")
    hints["has_smi"] = smi is not None
    readme_raw = _zip_read(zf, "README.md", "./README.md", "readme.md")
    if readme_raw:
        try:
            text = readme_raw.decode("utf-8", errors="replace")[:1200]
            text = re.sub(r"\s+", " ", text).strip()
            hints["readme_excerpt"] = text
        except Exception:
            pass
    # sample a few app files (bounded)
    checked = 0
    for name in zf.namelist():
        if checked > 25:
            break
        if not name.endswith((".html", ".js", ".hbs")):
            continue
        if "/app/" not in name and not name.startswith("app/"):
            continue
        try:
            raw = zf.read(name).decode("utf-8", errors="replace")[:8000]
        except Exception:
            continue
        checked += 1
        low = raw.lower()
        if "crayons" in low or "fw-" in low or "fwx-" in low:
            hints["has_crayons_mention"] = True
        if "client.data" in raw or "client.interface" in raw:
            hints["has_client_data"] = True
    return hints


def summarize_zip(zip_dir: Path, zip_file: str, app_id: str) -> dict:
    path = zip_dir / zip_file
    row: dict = {"app_id": app_id, "zip_file": zip_file, "error": None}
    if not path.is_file():
        row["error"] = f"missing_zip:{path}"
        return row
    try:
        with zipfile.ZipFile(path, "r") as zf:
            mname = _find_manifest_member(zf.namelist())
            if not mname:
                row["error"] = "no_manifest"
                return row
            raw = zf.read(mname)
            manifest = json.loads(raw.decode("utf-8"))
            row["platform_version"] = manifest.get("platform-version")
            row["engines"] = manifest.get("engines")
            row["manifest_summary"] = _walk_product(manifest)
            if manifest.get("oauth_config") or manifest.get("oauth"):
                row["oauth_hint"] = True
            ip = _zip_read(zf, "config/iparams.json", "./config/iparams.json")
            row["has_iparams_json"] = ip is not None
            iph = _zip_read(zf, "config/iparams.html", "./config/iparams.html")
            row["has_iparams_html"] = iph is not None
            rq = _zip_read(zf, "config/requests.json", "./config/requests.json")
            row["has_config_requests_json"] = rq is not None
            row["text_hints"] = _scan_text_hints(zf)
    except Exception as e:
        row["error"] = str(e)
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    ap.add_argument("--zip-dir", type=Path, default=None)
    ap.add_argument("--batch-spec", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root
    zip_dir = args.zip_dir or (root / "downloaded-zips")
    spec = json.loads(args.batch_spec.read_text(encoding="utf-8"))
    items = spec.get("items") or []
    summaries = []
    for it in items:
        summaries.append(
            summarize_zip(zip_dir, it["zip_file"], str(it.get("app_id", "")))
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summaries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(summaries)} summaries -> {args.output}")


if __name__ == "__main__":
    main()
