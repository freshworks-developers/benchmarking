---
name: app-builder-agent
description: Standalone Freshworks Platform 3.0 app-building agent that converts requirements (JSON criteria, CSV workshop rows, or PRD markdown) into production-ready app scaffolds and implementations using app-dev best practices. Designed to pair with a separate validation agent but not blocked by it.
compatibility: Freshworks Platform 3.0, FDK 9.x, Node.js 18.x
argument-hint: "[build|scaffold] [requirements-source-path-or-id]"
allowed-tools: ["shell", "read", "write", "strreplace", "glob", "grep"]
---

# App Builder Agent Skill

Purpose: Build Freshworks Platform 3.0 apps from structured requirements while strictly following the conventions and constraints of `.agents/skills/app-dev/SKILL.md`.

This agent is:
- **Standalone:** can perform end-to-end build independently.
- **Composable:** can hand off artifacts to a validation agent.
- **Input-flexible:** supports JSON criteria, CSV usecase rows, and PRD markdown.

## Invocation Examples

```bash
/build build @benchmarking/test-criteria/TEST001-criteria.json
/build build @benchmarking/Copilot Skills - Workshop - App Usecases.csv --row 1
/build build @benchmarking/generated-artifacts/generated-app-usecases.csv --row 1
/build build @benchmarking/generated-artifacts/01-PRD-app_493.md
```

If only an ID is provided, resolve in this order:
1. `test-criteria/<ID>-criteria.json`
2. `generated-artifacts/*<ID>*`
3. Ask user to confirm source path if multiple matches exist

## Mandatory Dependency

Before app generation, this skill MUST load and follow:
- `.agents/skills/app-dev/SKILL.md`

If any conflict exists, **`app-dev` rules win**.

## Execution Mode

AUTONOMOUS. Do not stop at planning. Build the app in a new app folder and iterate until functionally complete for the provided requirements.

This builder agent does not need to produce a full validation report, but should leave the app in a clean, validator-ready state.

## Supported Requirement Inputs

### A) JSON Criteria (`test-criteria/*.json`)

Expected keys:
- `id`
- `prompt`
- `expected_platform_features` (snake_case slugs: `request_templates`, `oauth`, `scheduled_events`, `crayons_ui`, etc.)
- `expected_instances` (optional)

Mapping rules:
- `prompt` => primary functional statement
- `expected_platform_features` => required platform capabilities for build and for eval scoring
- `expected_instances` => exact identifiers to materialize (request template names, iparams, events/functions)

Legacy: `expected_features` is accepted only when `expected_platform_features` is absent (same slug vocabulary).

### B) CSV Workshop Sheet (`Copilot Skills - Workshop - App Usecases.csv`)

Expected columns:
- `App Name`, `Product`, `App Features`, `Functional Requirements`, `Success Criteria`, `Platform Features`, `Complexity`

Row selection:
- Prefer explicit `--row N` or exact `App Name` match
- If unspecified, ask user for row

Mapping rules:
- `Product` => module family selection
- `Platform Features` => architecture (serverless/hybrid/oauth/frontend)
- `Functional Requirements` => implementation checklist
- `Success Criteria` => **sole** acceptance checklist (testable bullets); there is no separate “Expected” column in the workshop file

### B2) Unified benchmark use cases (`generated-artifacts/generated-app-usecases.csv`)

Same narrative columns as the workshop sheet, plus benchmark metadata:

- `Sl. No`, `App ID`, `Zip File`, `App Name`, `Product`, `App Features`, `Expected Folders`, `Prompt`, `Functional Requirements`, `Success Criteria`, **`Expected Platform Features`**, `Complexity`, `Reference Links`, `Picked By`

Notes:
- **`Expected Platform Features`** replaces the workshop header `Platform Features` (Freshworks taxonomy: serverless events, request templates, iparams, SMI functions, locations, OAuth, Crayons, data methods, etc.).
- **`Success Criteria`** is the only acceptance column (no legacy `Expected` column).
- Regenerate manifest batches / merged rows with `scripts/extract_manifest_batch.py` and `scripts/build_unified_app_usecases.py` when zips change.

### C) PRD Markdown (`generated-artifacts/*.md`)

Parse sections:
- Summary / Problem / Scope / Functional requirements / Acceptance criteria / Test plan / Platform features observed

Mapping rules:
- Product + platform features observed => module/events/functions skeleton
- Functional requirements + benchmark prompt => behavior implementation
- Acceptance criteria => completion checks

## Build Workflow

### Step 1: Normalize Requirements

Produce a normalized object:

```json
{
  "app_name": "...",
  "product": "...",
  "app_type": "frontend|serverless|hybrid|oauth",
  "features": [],
  "events": [],
  "functions": [],
  "request_templates": [],
  "iparams": [],
  "locations": [],
  "acceptance_criteria": []
}
```

Rules:
- Keep only requirements evidenced by source.
- Do not invent unsupported platform features.
- If certainty is low for a core behavior, mark assumption and choose the safest Platform 3.0-compatible implementation.

### Step 2: Choose Template and App Folder

- Create a new kebab-case app folder in repo root.
- Choose base template from `.agents/skills/app-dev/assets/templates/`:
  - `frontend-skeleton`
  - `serverless-skeleton`
  - `hybrid-skeleton`
  - `oauth-skeleton` (only when required)

### Step 3: Implement Required Artifacts

Implement only what normalized requirements demand:
- `manifest.json`
- `config/iparams.json` (and secure flags where applicable)
- `config/requests.json` (if request templates needed)
- `config/oauth_config.json` (if oauth needed)
- `server/server.js` (events/functions/SMI)
- `app/*` (if frontend/hybrid/oauth)
- `README.md` basic setup/usage

Hard requirements inherited from `app-dev`:
- Platform 3.0 manifest structure
- No Platform 2.x patterns
- manifest-to-file consistency
- request template ↔ manifest sync
- no async-without-await
- no unused params
- icon and Crayons requirements where frontend exists

### Step 4: Builder Self-Check (Lightweight)

Builder performs minimal readiness checks (not full validation-report generation):
- required files exist
- normalized required instances are present (exact names)
- obvious lint blockers addressed by code structure
- app is organized for validator handoff

If local validation is available, run `fdk validate` and fix blocking errors opportunistically; otherwise continue and clearly note that validator should run.

### Step 5: Validator Handoff Contract

Write a handoff file: `.build/handoff.json` in app folder:

```json
{
  "agent": "app-builder-agent",
  "requirements_source": "<path>",
  "normalized_requirements": {},
  "implemented_instances": {
    "events": [],
    "functions": [],
    "request_templates": [],
    "iparams": []
  },
  "known_gaps": [],
  "assumptions": []
}
```

This keeps the builder independent while enabling the validation agent to verify fidelity and quality.

## Product/Module Mapping Baseline

- Freshdesk -> `support_*` modules
- Freshservice -> `service_*` modules
- Freshsales / freshworks_crm -> CRM modules (`deal`, `contact`, `sales_account`, etc. as applicable)

Location/module placement must remain Platform 3.0-correct.

## What This Agent Must Not Do

- Do not generate Platform 2.x syntax or deprecated APIs.
- Do not claim "fully validated" unless validation actually passed.
- Do not generate large validation reports unless explicitly requested.
- Do not add unrelated features not present in source requirements.

## Done Criteria For This Builder Agent

An app build is considered complete when:
1. App structure and implementation match normalized requirements.
2. All required named instances from source are present.
3. App follows `app-dev` best practices and safety constraints.
4. Handoff contract file exists for validator agent.

## Minimal Final Output Format

```text
✅ App build completed: <app-folder>
- Source: <requirements file>
- Type: <frontend|serverless|hybrid|oauth>
- Implemented: <key features>
- Handoff: <app-folder>/.build/handoff.json
```
