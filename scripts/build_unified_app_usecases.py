#!/usr/bin/env python3
"""Merge manifest batches + workshop JSON + PRD rows into generated-app-usecases.csv."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_BATCHES = [
    REPO_ROOT / "generated-artifacts" / "manifest-batches" / f"batch_{i:02d}.json"
    for i in range(1, 6)
]
ZIP_CSV = REPO_ROOT / "generated-artifacts" / "generated-app-usecases.csv"
WORKSHOP_JSON = REPO_ROOT / "generated-artifacts" / "workshop_rows.json"
OUT_CSV = REPO_ROOT / "generated-artifacts" / "generated-app-usecases.csv"

HEADERS = [
    "Sl. No",
    "App ID",
    "Zip File",
    "App Name",
    "Product",
    "App Features",
    "Expected Folders",
    "Prompt",
    "Functional Requirements",
    "Success Criteria",
    "Expected Platform Features",
    "Complexity",
    "Reference Links",
    "Picked By",
]


def load_manifest_by_app_id() -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    for path in SPEC_BATCHES:
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data:
            aid = str(row.get("app_id", "")).strip()
            if aid:
                by_id[aid] = row
    return by_id


def _clean_readme(ex: str, max_len: int = 400) -> str:
    if not ex:
        return ""
    t = re.sub(r"\s+", " ", ex).strip()
    return t[:max_len].rstrip() + ("…" if len(t) > max_len else "")


def format_expected_platform_features(ms: dict) -> str:
    lines: list[str] = []
    if ms.get("error"):
        lines.append(f"(manifest extract: {ms['error']})")
        return "\n".join(lines)

    summ = ms.get("manifest_summary") or {}
    if ms.get("oauth_hint"):
        lines.append("OAuth (see oauth_config in package)")

    wd = summ.get("whitelisted_domains")
    if wd:
        lines.append("Whitelisted domains (external API / product hosts)")

    # Product-scoped (2.x style)
    for p in summ.get("products") or []:
        locs = (summ.get("locations_by_product") or {}).get(p) or []
        if locs:
            lines.append(f"App locations ({p}): {', '.join(locs)}")
        ev = (summ.get("events_by_product") or {}).get(p) or []
        if ev:
            lines.append(f"Serverless events ({p}): {', '.join(ev)}")
        se = (summ.get("scheduled_events_by_product") or {}).get(p) or []
        if se:
            lines.append(f"Scheduled events ({p}): {', '.join(se)}")
        rq = (summ.get("requests_by_product") or {}).get(p) or []
        if rq:
            lines.append(f"Request templates ({p}): {', '.join(rq)}")
        fn = (summ.get("functions_by_product") or {}).get(p) or []
        if fn:
            lines.append(f"SMI functions ({p}): {', '.join(fn)}")

    # Module-scoped (3.0 style)
    for m in summ.get("modules") or []:
        locs = (summ.get("locations_by_module") or {}).get(m) or []
        if locs:
            lines.append(f"App locations (module {m}): {', '.join(locs)}")
        ev = (summ.get("events_by_module") or {}).get(m) or []
        if ev:
            lines.append(f"Serverless events (module {m}): {', '.join(ev)}")
        se = (summ.get("scheduled_events_by_module") or {}).get(m) or []
        if se:
            lines.append(f"Scheduled events (module {m}): {', '.join(se)}")
        rq = (summ.get("requests_by_module") or {}).get(m) or []
        if rq:
            lines.append(f"Request templates (module {m}): {', '.join(rq)}")
        fn = (summ.get("functions_by_module") or {}).get(m) or []
        if fn:
            lines.append(f"SMI functions (module {m}): {', '.join(fn)}")

    hints = ms.get("text_hints") or {}
    if hints.get("has_crayons_mention"):
        lines.append("Crayons UI (components referenced in app assets)")
    if hints.get("has_client_data"):
        lines.append("Data methods (client.data / interface usage in frontend)")
    if hints.get("has_smi"):
        lines.append("SMI (smi.json present)")

    if ms.get("has_iparams_json") or ms.get("has_iparams_html"):
        lines.append("iparams (installation / configuration parameters)")

    if not lines:
        lines.append(
            "Minimal surface (no locations/events/requests in manifest); verify package manually"
        )

    return "\n".join(lines)


def build_app_features(
    app_name: str, product: str, readme_excerpt: str, ms: dict
) -> str:
    desc = _clean_readme(readme_excerpt, 500)
    if not desc or len(desc) < 40:
        desc = (
            f"{app_name} extends {product} with behaviors declared in manifest "
            f"(see Expected Platform Features)."
        )
    goals = (
        f"- Deliver the packaged workflow reliably in {product}.\n"
        f"- Keep configuration and side effects observable and safe.\n"
        f"- Meet the functional requirements without blocking validation issues."
    )
    stories = (
        f"- As an admin, I want to install and configure the app with clear parameters.\n"
        f"- As an agent, I want the app to behave correctly in its declared UI or event surfaces.\n"
        f"- As an operator, I want failures to surface in logs or UI without silent drops."
    )
    return f"{desc}\n\nGoals\n{goals}\n\nUser Stories\n{stories}"


def build_functional_requirements(ms: dict, product: str) -> str:
    bullets: list[str] = []
    summ = ms.get("manifest_summary") or {}

    def add_ev(label: str, d: dict):
        for scope, evs in (d or {}).items():
            if not evs:
                continue
            bullets.append(
                f"- When events {', '.join(evs)} fire ({label} {scope}), run the declared server handlers (Must)"
            )

    def add_rq(label: str, d: dict):
        for scope, names in (d or {}).items():
            if not names:
                continue
            bullets.append(
                f"- Use request templates {', '.join(names[:12])}"
                f"{'…' if len(names) > 12 else ''} for outbound calls ({label} {scope}) (Must)"
            )

    def add_fn(label: str, d: dict):
        for scope, names in (d or {}).items():
            if not names:
                continue
            bullets.append(
                f"- Expose SMI functions {', '.join(names)} where declared ({label} {scope}) (Must)"
            )

    def add_loc(label: str, d: dict):
        for scope, locs in (d or {}).items():
            if not locs:
                continue
            bullets.append(
                f"- Render UI in locations {', '.join(locs)} ({label} {scope}) (Must)"
            )

    add_loc("product", summ.get("locations_by_product") or {})
    add_loc("module", summ.get("locations_by_module") or {})
    add_ev("product", summ.get("events_by_product") or {})
    add_ev("module", summ.get("events_by_module") or {})
    for scope, evs in (summ.get("scheduled_events_by_product") or {}).items():
        if evs:
            bullets.append(
                f"- Handle scheduled events {', '.join(evs)} for product {scope} (Must)"
            )
    for scope, evs in (summ.get("scheduled_events_by_module") or {}).items():
        if evs:
            bullets.append(
                f"- Handle scheduled events {', '.join(evs)} for module {scope} (Must)"
            )
    add_rq("product", summ.get("requests_by_product") or {})
    add_rq("module", summ.get("requests_by_module") or {})
    add_fn("product", summ.get("functions_by_product") or {})
    add_fn("module", summ.get("functions_by_module") or {})

    if ms.get("has_iparams_json") or ms.get("has_iparams_html"):
        bullets.append("- Collect and validate installation parameters via iparams (Must)")
    if summ.get("whitelisted_domains"):
        bullets.append(
            "- Only call domains allowed by whitelisted-domains / request templates (Must)"
        )
    if ms.get("oauth_hint"):
        bullets.append("- Complete OAuth connection flows required by the integration (Must)")

    if not bullets:
        bullets.append(
            f"- Implement the core behavior implied by the package for {product} (Must)"
        )
        bullets.append(
            "- Validate configuration before executing sensitive operations (Must)"
        )

    bullets.append("- Log serverless and request failures with enough context to debug (Should)")
    return "\n".join(bullets)


def build_success_criteria(ms: dict, app_name: str) -> str:
    lines: list[str] = []
    summ = ms.get("manifest_summary") or {}

    def any_locs():
        for d in (
            summ.get("locations_by_product"),
            summ.get("locations_by_module"),
        ):
            if d and any(d.values()):
                return True
        return False

    def any_ev():
        for d in (
            summ.get("events_by_product"),
            summ.get("events_by_module"),
            summ.get("scheduled_events_by_product"),
            summ.get("scheduled_events_by_module"),
        ):
            if d and any(d.values()):
                return True
        return False

    if any_locs():
        lines.append(
            f"- Declared app surfaces load in-product without console errors for {app_name}"
        )
    if any_ev():
        lines.append(
            "- Configured serverless / scheduled handlers run when triggers fire without unhandled exceptions"
        )
    rq_count = sum(
        len(v or [])
        for v in list((summ.get("requests_by_product") or {}).values())
        + list((summ.get("requests_by_module") or {}).values())
    )
    if rq_count:
        lines.append(
            "- Request templates return expected HTTP outcomes; API/auth errors are surfaced clearly"
        )
    fn_count = sum(
        len(v or [])
        for v in list((summ.get("functions_by_product") or {}).values())
        + list((summ.get("functions_by_module") or {}).values())
    )
    if fn_count:
        lines.append(
            "- SMI function invocations complete within platform timeouts and return structured errors on failure"
        )
    if ms.get("has_iparams_json") or ms.get("has_iparams_html"):
        lines.append("- Installation parameters save correctly and are used on subsequent runs")
    lines.append("- App passes fdk validate for the declared platform-version")
    lines.append(
        "- Invalid configuration or upstream failures do not leave the app in a silent broken state"
    )
    return "\n".join(lines)


def build_prompt(
    product: str,
    app_name: str,
    zip_file: str,
    fr: str,
    sc: str,
    epf: str,
    folders: str,
) -> str:
    return (
        f"Build a Freshworks Platform app for {product.strip()} ({app_name.strip()}). "
        f"Package reference: {zip_file}. "
        f"Match folder layout: {folders.strip()}. "
        f"Implement Functional Requirements and Success Criteria verbatim intent; "
        f"materialize Expected Platform Features using manifest-safe patterns."
    )


def prd_rows() -> list[dict[str, str]]:
    return [
        {
            "app_id": "PRD-01",
            "zip_file": "",
            "app_name": "Freshdesk → Slack thread + Google Calendar event (OAuth)",
            "product": "Freshdesk",
            "app_features": (
                "On ticket creation, create a Slack message (thread anchor) and a Google Calendar event, "
                "with OAuth to Slack and Google, secure tokens, and idempotent execution.\n\n"
                "Goals\n"
                "- Automate ticket-to-collaboration handoff.\n"
                "- Give agents links to Slack and Calendar from the ticket context.\n"
                "- Prevent duplicate Slack posts or duplicate calendar events.\n\n"
                "User Stories\n"
                "- As an admin, I want OAuth for Slack and Google configured at install.\n"
                "- As an agent, I want one Slack thread and one calendar event per new ticket.\n"
                "- As an operator, I want token refresh and clear errors when APIs fail."
            ),
            "expected_folders": "app, config, server",
            "functional_requirements": (
                "- Trigger on ticket creation (Must)\n"
                "- Create Slack message with ticket id, subject, requester, priority, ticket URL (Must)\n"
                "- Create Calendar event titled with ticket id + subject; link ticket URL + Slack in description (Must)\n"
                "- Store OAuth tokens securely; refresh when expired (Must)\n"
                "- Idempotency: duplicate ticket-create payloads do not create duplicate Slack/Calendar resources (Must)\n"
                "- Admin/settings surface shows connection health (Should)"
            ),
            "success_criteria": (
                "- One ticket create produces exactly one Slack message and one Calendar event\n"
                "- Duplicate delivery of the same ticket-create event does not duplicate Slack or Calendar resources\n"
                "- Slack and Google OAuth complete independently; token failures are recoverable\n"
                "- Partial failures (e.g. Slack OK, Google fail) are logged and surfaced per policy\n"
                "- App passes fdk validate\n"
                "- No secrets committed in source"
            ),
            "expected_platform_features": (
                "OAuth (Slack, Google Calendar)\n"
                "Serverless events (ticket create)\n"
                "Request templates (Slack Web API, Google Calendar API)\n"
                "iparams / secure storage for tokens and channel defaults"
            ),
            "complexity": "High",
            "reference_links": "Slack API · Google Calendar API · Freshworks serverless",
            "picked_by": "",
        },
        {
            "app_id": "PRD-02",
            "zip_file": "",
            "app_name": "Support Intelligence Hub (Crayons UI)",
            "product": "Freshdesk",
            "app_features": (
                "Full-page dashboard for queue health and trends plus ticket sidebar for contextual insights, "
                "using Crayons and secure data access.\n\n"
                "Goals\n"
                "- In-product visibility for managers and agents.\n"
                "- Consistent, accessible UI aligned to Freshworks patterns.\n\n"
                "User Stories\n"
                "- As a manager, I want KPIs, filters, and tables on a full-page app.\n"
                "- As an agent, I want ticket summary, related tickets, and a playbook in the sidebar.\n"
                "- As a user, I want clear loading and error states."
            ),
            "expected_folders": "app, config, server",
            "functional_requirements": (
                "- Full-page dashboard: filters, KPI cards, at least one trend view and one data table (Must)\n"
                "- Ticket sidebar: ticket summary, related tickets for requester, optional company-level tickets (Must)\n"
                "- Playbook / checklist in sidebar (Must)\n"
                "- Crayons components for primary UI; keyboard-accessible controls (Must)\n"
                "- Server-side data access for privileged operations (Must)\n"
                "- Admin configuration for defaults where required (Should)"
            ),
            "success_criteria": (
                "- Dashboard loads with filters, KPIs, and table within acceptable time\n"
                "- Sidebar renders on ticket detail with summary, related tickets, and playbook\n"
                "- Loading and error states are user-visible and actionable\n"
                "- App passes fdk validate\n"
                "- No secrets in frontend bundles"
            ),
            "expected_platform_features": (
                "App locations (full_page_app, ticket_sidebar)\n"
                "Crayons UI\n"
                "Data methods / secure server routes for Freshdesk data\n"
                "Request templates or platform APIs as needed for metrics"
            ),
            "complexity": "Medium",
            "reference_links": "Crayons · Freshdesk data methods · Full-page app",
            "picked_by": "",
        },
        {
            "app_id": "PRD-03",
            "zip_file": "",
            "app_name": "Shopify multi-shop order sidebar (Freshdesk)",
            "product": "Freshdesk",
            "app_features": (
                "Ticket sidebar federates Shopify orders for the requester across multiple shops with "
                "pagination, per-shop errors, and guarded actions (refund, cancel, follow-up ticket).\n\n"
                "Goals\n"
                "- Single-pane order context for agents.\n"
                "- Safe, auditable actions with private notes.\n\n"
                "User Stories\n"
                "- As an agent, I want orders from all active shops with shop badges.\n"
                "- As a lead, I want confirmation before refund/cancel and an audit note on the ticket.\n"
                "- As an admin, I want per-shop tokens and allowed actions configurable."
            ),
            "expected_folders": "app, config, server",
            "functional_requirements": (
                "- Sidebar loads only when requester email exists (Must)\n"
                "- Parallel queries per shop with isolated loading/error states (Must)\n"
                "- Unified timeline sorted newest first; load-more pagination (Must)\n"
                "- Refund and cancel: confirmation modal, API call, private note with actor/time/shop/outcome (Must)\n"
                "- Follow-up ticket pre-filled with order + shop context (Must)\n"
                "- Hide actions based on allowed_actions; disable while in-flight (Must)\n"
                "- Tokens only in secure storage / iparams — never client localStorage (Must)"
            ),
            "success_criteria": (
                "- Valid requester shows orders from all configured shops; partial shop failures stay isolated\n"
                "- Refund/cancel completes and writes the required private note\n"
                "- Follow-up ticket creation succeeds with pre-filled context\n"
                "- No API tokens in repo or UI\n"
                "- App passes fdk validate"
            ),
            "expected_platform_features": (
                "App locations (ticket_sidebar)\n"
                "Request templates (Shopify Admin API per shop, Freshdesk API)\n"
                "iparams (multi-shop domains, tokens, allowed actions)\n"
                "Crayons UI (modals, lists, badges)"
            ),
            "complexity": "High",
            "reference_links": "Shopify Admin API · Freshdesk API",
            "picked_by": "",
        },
        {
            "app_id": "PRD-04",
            "zip_file": "",
            "app_name": "Bulk ticket creation with rate-limit handling",
            "product": "Freshdesk",
            "app_features": (
                "Sidebar action creates many tickets via Freshdesk API in batches with explicit 429 handling, "
                "backoff, and concurrency limits.\n\n"
                "Goals\n"
                "- Reliable bulk create under real API limits.\n"
                "- Observable progress and failures.\n\n"
                "User Stories\n"
                "- As an agent, I want to trigger bulk create from the ticket view.\n"
                "- As an operator, I want rate limits to backoff and resume safely.\n"
                "- As an admin, I want clear logs when batches fail."
            ),
            "expected_folders": "app, config, server",
            "functional_requirements": (
                "- Primary UI control triggers batched ticket creation (Must)\n"
                "- Respect Freshdesk rate limits: detect 429, backoff, retry with jitter (Must)\n"
                "- Cap concurrency; no unbounded parallel creates (Must)\n"
                "- Summarize successes/failures to the user; structured server logs (Must)\n"
                "- Idempotent client action where possible to avoid duplicate bulk runs (Should)"
            ),
            "success_criteria": (
                "- Under simulated 429s, app retries with backoff and completes or surfaces terminal failure clearly\n"
                "- Batch progress is visible; no silent partial completion\n"
                "- App passes fdk validate\n"
                "- No API keys in frontend"
            ),
            "expected_platform_features": (
                "App locations (ticket_sidebar)\n"
                "Request templates (Freshdesk tickets API)\n"
                "Server-side batching and retry logic\n"
                "iparams for API key / domain if required"
            ),
            "complexity": "High",
            "reference_links": "Freshdesk API rate limits · Bulk operations",
            "picked_by": "",
        },
    ]


def main() -> None:
    manifest_by_id = load_manifest_by_app_id()
    if len(manifest_by_id) < 42:
        print(f"warning: only {len(manifest_by_id)} manifest summaries loaded (expected 42)")

    workshop = []
    if WORKSHOP_JSON.is_file():
        workshop = json.loads(WORKSHOP_JSON.read_text(encoding="utf-8"))

    out_rows: list[dict[str, str]] = []

    with ZIP_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            zf = (raw.get("Zip File") or "").strip()
            # Idempotent: only ingest packaged apps from the CSV (workshop/PRD rows have no zip).
            if not zf.endswith(".zip"):
                continue
            aid = (raw.get("App ID") or "").strip()
            ms = manifest_by_id.get(aid, {})
            readme = (ms.get("text_hints") or {}).get("readme_excerpt") or ""
            app_name = (raw.get("App Name") or "").strip()
            product = (raw.get("Product") or "").strip()
            zip_file = (raw.get("Zip File") or "").strip()
            folders = (raw.get("Expected Folders") or "").strip()
            complexity = (raw.get("Complexity") or "Medium").strip()

            epf = format_expected_platform_features(ms)
            fr = build_functional_requirements(ms, product)
            sc = build_success_criteria(ms, app_name)
            feats = build_app_features(app_name, product, readme, ms)
            prompt = build_prompt(product, app_name, zip_file, fr, sc, epf, folders)

            out_rows.append(
                {
                    "App ID": aid,
                    "Zip File": zip_file,
                    "App Name": app_name,
                    "Product": product,
                    "App Features": feats,
                    "Expected Folders": folders,
                    "Prompt": prompt,
                    "Functional Requirements": fr,
                    "Success Criteria": sc,
                    "Expected Platform Features": epf,
                    "Complexity": complexity,
                    "Reference Links": (raw.get("Reference Links") or "").strip(),
                    "Picked By": (raw.get("Picked By") or "").strip(),
                }
            )

    # Workshop rows
    for wr in workshop:
        epf = wr.get("expected_platform_features") or ""
        out_rows.append(
            {
                "App ID": wr.get("app_id", ""),
                "Zip File": "",
                "App Name": wr.get("app_name", ""),
                "Product": wr.get("product", ""),
                "App Features": wr.get("app_features", ""),
                "Expected Folders": wr.get("expected_folders", ""),
                "Prompt": wr.get("prompt", ""),
                "Functional Requirements": wr.get("functional_requirements", ""),
                "Success Criteria": wr.get("success_criteria", ""),
                "Expected Platform Features": epf,
                "Complexity": wr.get("complexity", ""),
                "Reference Links": wr.get("reference_links", ""),
                "Picked By": wr.get("picked_by", ""),
            }
        )

    for pr in prd_rows():
        out_rows.append(
            {
                "App ID": pr["app_id"],
                "Zip File": pr["zip_file"],
                "App Name": pr["app_name"],
                "Product": pr["product"],
                "App Features": pr["app_features"],
                "Expected Folders": pr["expected_folders"],
                "Prompt": build_prompt(
                    pr["product"],
                    pr["app_name"],
                    pr["zip_file"] or "N/A",
                    pr["functional_requirements"],
                    pr["success_criteria"],
                    pr["expected_platform_features"],
                    pr["expected_folders"],
                ),
                "Functional Requirements": pr["functional_requirements"],
                "Success Criteria": pr["success_criteria"],
                "Expected Platform Features": pr["expected_platform_features"],
                "Complexity": pr["complexity"],
                "Reference Links": pr["reference_links"],
                "Picked By": pr["picked_by"],
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for i, row in enumerate(out_rows, start=1):
            row_out = {"Sl. No": str(i), **row}
            w.writerow(row_out)

    print(f"Wrote {len(out_rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
