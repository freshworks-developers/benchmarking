#!/usr/bin/env python3
"""Parse workshop CSV into generated-artifacts/workshop_rows.json."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "Copilot Skills - Workshop - App Usecases.csv"
OUT_PATH = REPO_ROOT / "generated-artifacts" / "workshop_rows.json"

EXPECTED_HEADERS = {
    "Sl. No",
    "App Name",
    "Product",
    "App Features",
    "Functional Requirements",
    "Success Criteria",
    "Platform Features",
    "Complexity",
    "Reference Links",
    "Picked By",
}

FOLDER_ORDER = ("app", "config", "server")


def _norm(s: str) -> str:
    return (s or "").lower()


def derive_expected_folders(platform_features: str) -> str:
    """Comma-separated plausible folders from Platform Features text."""
    t = _norm(platform_features)
    t_compact = re.sub(r"\s+", "", t)

    has_serverless = any(
        k in t
        for k in (
            "serverless",
            "serverless events",
            "onappinstall",
            "app setup",
            "app setupevent",
        )
    ) or "events" in t and "serverless" in t
    if not has_serverless:
        has_serverless = "serverless" in t_compact or bool(
            re.search(r"\bevents?\b", t) and "serverless" in t
        )
    if not has_serverless:
        has_serverless = "requesttemplate" in t_compact or "request templates" in t

    has_ui = any(
        x in t
        for x in (
            "crayons",
            "sidebar",
            "hybrid app",
            "full page",
            "fullpage",
            "client.data",
            "ticket sidebar",
            "ui ",
            "locations",
            "location)",
        )
    )

    has_oauth = "oauth" in t

    folders: set[str] = set()
    if has_serverless:
        folders.update(("config", "server"))
    if has_ui:
        folders.update(("app", "config"))
    if has_oauth:
        folders.update(("app", "config", "server"))

    if not folders:
        folders.update(("app", "config", "server"))

    ordered = [f for f in FOLDER_ORDER if f in folders]
    return ",".join(ordered)


def build_prompt(
    product: str,
    app_name: str,
    functional_requirements: str,
    success_criteria: str,
) -> str:
    return (
        f'Build a Freshworks Platform 3.0 app for {product.strip()} named {app_name.strip()}. '
        f"Implement per Functional Requirements and Success Criteria. "
        f"Match Expected Platform Features."
    )


def main() -> None:
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing CSV: {CSV_PATH}")

    rows: list[dict[str, str]] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, dialect="excel")
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header row")
        missing = EXPECTED_HEADERS - set(reader.fieldnames)
        if missing:
            raise SystemExit(f"CSV missing expected headers: {sorted(missing)}")

        for raw in reader:
            if not any((raw.get(h) or "").strip() for h in reader.fieldnames if h):
                continue
            rows.append(raw)

    if len(rows) != 12:
        raise SystemExit(f"Expected 12 data rows, got {len(rows)}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    out: list[dict[str, str]] = []
    for i, row in enumerate(rows, start=1):
        sl = (row.get("Sl. No") or "").strip()
        app_name = (row.get("App Name") or "").strip()
        product = (row.get("Product") or "").strip()
        app_features = (row.get("App Features") or "").strip()
        functional_requirements = (row.get("Functional Requirements") or "").strip()
        success_criteria = (row.get("Success Criteria") or "").strip()
        platform_features = (row.get("Platform Features") or "").strip()
        complexity = (row.get("Complexity") or "").strip()
        reference_links = (row.get("Reference Links") or "").strip()
        picked_by = (row.get("Picked By") or "").strip()

        app_id = f"WSHOP-{i:02d}"
        expected_folders = derive_expected_folders(platform_features)
        prompt = build_prompt(product, app_name, functional_requirements, success_criteria)

        out.append(
            {
                "app_id": app_id,
                "workshop_sl_no": sl,
                "app_name": app_name,
                "product": product,
                "app_features": app_features,
                "functional_requirements": functional_requirements,
                "success_criteria": success_criteria,
                "expected_platform_features": platform_features,
                "complexity": complexity,
                "reference_links": reference_links,
                "picked_by": picked_by,
                "expected_folders": expected_folders,
                "prompt": prompt,
            }
        )

    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(out)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
