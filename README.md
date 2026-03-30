# Freshworks Platform 3.0 benchmarking suite

This repository provides automated validation and scoring for Freshworks marketplace apps: FDK checks, Platform 3.0 compliance, Crayons usage, file structure, optional custom requirements, and tooling to learn from repeated failures.

## Repository layout

```
benchmarking/
├── bin/                 # Recommended CLI (eval, setup, learn, convert)
├── lib/                 # Shared Python helpers (gitignored; see Prerequisites)
├── tests/               # Pytest for bin/ and lib/
├── automate_test.py     # Legacy / interactive driver (generation + evaluate)
├── setup_test.py        # Interactive criteria and app directory setup
├── convert_criteria.py  # Plain-text criteria → JSON (see also bin/convert-criteria.py)
├── error_learner.py     # Error patterns (see also bin/learn-*.py)
├── docs/                # AGENT_BENCHMARK_PLAN.md, architecture, slash-command mapping
├── use-cases/           # Definitions for generate-and-test flows
├── test-criteria/       # Per-app criteria JSON
├── results/             # Output JSON and eval_history.jsonl (gitignored)
├── test-apps/           # Apps under test
└── .dev/                # Error learning artifacts
```

## Prerequisites

- Python 3.7+
- Dependencies: `pip install -r requirements.txt`
- **FDK on PATH** (required for validation):  
  `npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g`
- Run all commands from the **repository root** (the directory that contains `bin/` and `automate_test.py`).
- **`lib/` directory:** This path is listed in `.gitignore` per repository policy. You need a local `lib/` tree (same layout as before: `resolve.py`, `history.py`, `criteria_convert.py`, `__init__.py`) for `bin/*.py` and tests to import successfully. Obtain it from your team or an internal package source if your clone does not include it.

---

## Running evaluations (recommended)

For day-to-day and CI-style runs, use the **`bin`** scripts. They wrap the same engine as `automate_test.py` but give stable entrypoints, predictable result paths, and exit codes.

| Command | Purpose |
|--------|---------|
| `python3 bin/eval.py run <app_id_or_path> [--app-id ID] [--learn]` | Run evaluation; append to history; optional `--learn` to refresh skill-update suggestions. |
| `python3 bin/eval-results.py [APP_ID] [--json]` | Print result file path or list result files. |
| `python3 bin/eval-history.py [--app-id ID] [--last N] [--json]` | Show evaluation history. |
| `python3 bin/eval-status.py [APP_ID] [--json]` | Last run status (grade, pass/fail). |
| `python3 bin/setup.py <app_id> --criteria-file <path> [--app-path PATH]` | Non-interactive criteria / test-apps setup. |
| `python3 bin/convert-criteria.py --file <path> --output <path>` | Convert plain-text criteria to JSON (`-` for stdin). |
| `python3 bin/learn-stats.py` | Error-learner statistics. |
| `python3 bin/learn-suggest.py` | Write suggestions to `.dev/planning/AUTO_SKILL_UPDATES.md`. |

**Examples:**

```bash
# Evaluate by app ID (resolves test-apps/<ID> and optional criteria file)
python3 bin/eval.py run APP001

# Evaluate by path, with explicit result id
python3 bin/eval.py run test-apps/MyApp --app-id MYAPP

# Inspect outputs
python3 bin/eval-results.py APP001
python3 bin/eval-history.py --last 10
python3 bin/eval-status.py
```

**Outputs**

- Result file: `results/<app_id>_result.json`
- Append-only history: `results/eval_history.jsonl`
- Exit codes: `0` success, `1` failure (validation or runtime error), `2` invalid arguments

Full contract, optional Promptfoo usage, and agent workflow: **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)**. Slash-style command mapping: **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)**. Benchmark agent roles: **[docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md)**.

---

## Alternative: `automate_test.py`

Use this when you need **generate-and-test** (wait for human generation, then validate) or you prefer the older single-script interface.

**Generate from a predefined use case**

```bash
python3 automate_test.py --app APP003
```

The script prints the prompt, waits while you generate the app (for example in another editor), then continues on Enter and runs validation.

**Evaluate an existing app tree**

```bash
python3 automate_test.py --evaluate test-apps/APP001 --app-id APP001 \
  --requirements test-criteria/APP001-criteria.json

# Or comma-separated requirements
python3 automate_test.py --evaluate test-apps/my-app --requirements "OAuth,Webhooks"
```

**Error learning (via automate_test)**

```bash
python3 automate_test.py --show-stats
python3 automate_test.py --generate-skill-updates
```

Prefer `bin/learn-stats.py` and `bin/learn-suggest.py` for the same behavior with clearer naming.

**Help**

```bash
python3 automate_test.py --help
```

---

## Interactive setup (`setup_test.py`)

Creates criteria under `test-criteria/` and a directory under `test-apps/`. Accepts pasted plain text or JSON (terminate input with a line `END`).

```bash
python3 setup_test.py APP001
# Optional: copy app in one step
python3 setup_test.py APP001 --app-path /path/to/your/app
```

Then run evaluation with `bin/eval.py run APP001` or the matching `automate_test.py --evaluate` command shown by the script.

---

## Scoring overview

Apps are scored on a **100-point** scale with letter grades **A–F**.

| Area | Points | Notes |
|------|--------|--------|
| FDK validation | 20 | Pass/fail style contribution |
| File structure | 20 | Expected files present |
| Platform 3.0 compliance | 40 | Five checks (8 pts each where applicable) |
| Crayons usage | 20 | `fw-*` / Crayons usage signals |

**Grade bands:** A 90–100, B 80–89, C 70–79, D 60–69, F below 60.

Result JSON includes `score`, `validation`, `platform3_compliance`, `requirements_met` (when criteria apply), and related fields. Inspect `results/<id>_result.json` after each run.

---

## Predefined use cases (generation mode)

| ID | Name | Type | Product |
|----|------|------|---------|
| APP001 | MS Teams Presence Checker | Frontend | Freshservice |
| APP002 | Freshservice-Asana Sync | Serverless | Freshservice |
| APP003 | Freshdesk-GitHub Integration | Frontend | Freshdesk |
| APP004 | Password Generator | Frontend | Freshservice |
| APP005 | Freshdesk-Zapier Contact Sync | Serverless | Freshdesk |
| APP006 | Jira-Freshdesk OAuth Sync | Serverless | Freshdesk |
| APP007 | Ticket Field Validation | Frontend | Freshdesk |

List IDs from `use-cases/use_cases.json` if the table drifts.

---

## Error learning

Failures can be recorded for pattern analysis. Data lives under `.dev/` (for example `.dev/comparison/error_database.json`, `.dev/planning/AUTO_SKILL_UPDATES.md`).

```bash
python3 bin/learn-stats.py
python3 bin/learn-suggest.py
# Legacy equivalents:
python3 error_learner.py stats
python3 error_learner.py suggest
```

---

## Tests

```bash
pytest tests/
```

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| FDK not found | Install FDK globally (see Prerequisites) and ensure `fdk` is on `PATH`. |
| Import errors from `lib` | Ensure a local `lib/` package exists at repo root (ignored by git; see Prerequisites). |
| Use case not found | Confirm `id` in `use-cases/use_cases.json`. |
| Evaluate path errors | Use paths relative to repo root or absolute paths to the app directory. |

For low scores, run `fdk validate` inside the app directory and compare manifest and file layout to criteria and Platform 3.0 expectations.

---

**Last updated:** March 2026. Internal Freshworks tooling for marketplace app quality assurance.
