# Agent Benchmark Execution Plan

## Purpose

This repo is the **Freshworks Platform 3.0 evaluation framework**. Agents and humans use it to validate and score Freshworks marketplace apps (FDK validation, Platform 3.0 compliance, Crayons UI, file structure) and to improve over time via error learning and evaluation history.

## Prerequisites

- Python 3.7+
- `pip install -r requirements.txt`
- FDK on PATH: `npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g`
- Run commands from the **benchmarking repo root** (directory containing `bin/`, `lib/`, `automate_test.py`).

## Simple input

You can provide only:

- **App ID** (e.g. `APP001`, `TEST002`) – script resolves to `test-apps/<id>` and optional `test-criteria/<id>-criteria.json`.
- **App path** (e.g. `test-apps/MyApp`) – script uses that path and infers or uses `--app-id` for the result name.

No need to pass criteria paths or expected_files unless overriding.

## Commands (bin scripts)

### Evaluation


| Command                                                            | Description                                                                      |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `python3 bin/eval.py run <app_id_or_path> [--app-id ID] [--learn]` | Run evaluation; append to history; optional `--learn` to generate skill updates. |
| `python3 bin/eval-results.py [APP_ID] [--json]`                    | Print result file path or list all result files.                                 |
| `python3 bin/eval-history.py [--app-id ID] [--last N] [--json]`    | Show evaluation history (table or JSON).                                         |
| `python3 bin/eval-status.py [APP_ID] [--json]`                     | Show last run status (grade, pass/fail) for one or all apps.                     |


### Setup and convert


| Command                                                                  | Description                                               |
| ------------------------------------------------------------------------ | --------------------------------------------------------- |
| `python3 bin/setup.py <app_id> --criteria-file <path> [--app-path PATH]` | Create test-criteria and test-apps dir (non-interactive). |
| `python3 bin/convert-criteria.py --file <path> --output <path>`          | Convert plain text criteria to JSON. Use `-` for stdin.   |


### Error learning


| Command                        | Description                                                                       |
| ------------------------------ | --------------------------------------------------------------------------------- |
| `python3 bin/learn-stats.py`   | Print error learner statistics.                                                   |
| `python3 bin/learn-suggest.py` | Generate skill update suggestions (writes `.dev/planning/AUTO_SKILL_UPDATES.md`). |


## Input/output contract

- **Input**: `app_id` or path; optional `--app-id`, `--requirements` (via criteria file).
- **Output**:
  - **Result file**: `results/<app_id>_result.json` (schema: `score`, `validation`, `platform3_compliance`, `file_structure`, `crayons_usage`).
  - **History**: `results/eval_history.jsonl` (one JSON object per line: `app_id`, `timestamp`, `score`, `grade`, `validation_success`, `result_file`).
  - **Skills**: `.dev/planning/AUTO_SKILL_UPDATES.md` (after `learn-suggest`).
- **Exit codes**: 0 = success, 1 = failure (e.g. app not found, validation failed), 2 = invalid arguments.

## Analyzing results over time

- Read `results/eval_history.jsonl` and compare latest vs previous for each `app_id`.
- Or run: `python3 bin/eval-history.py [--app-id ID] [--last N]` for a summary.
- For failures: read `results/<id>_result.json` → `validation.platform_errors`, `validation.lint_errors`, `platform3_compliance`; optionally read `AUTO_SKILL_UPDATES.md` for suggested rule changes.

## Optional: Promptfoo

For CI or matrix evals:

- **Provider script**: `scripts/promptfoo_provider.py` – receives (context, options, prompt) from Promptfoo, runs `bin/eval.py run <app_id>`, and prints the result JSON to stdout.
- **Config**: `promptfooconfig.yaml` in the repo root – defines one provider (`exec: python3 scripts/promptfoo_provider.py`) and tests with assertions (e.g. is-json, javascript for score and validation_success).
- **Run**: From repo root, run `promptfoo eval` (requires Promptfoo installed: `npm install -g promptfoo`). Results appear in Promptfoo’s output and can be compared across runs.

## Verification and validation

- After changing an app, run: `python3 bin/eval.py run <app_id_or_path>` and check the result file or exit code.
- If grade or `validation_success` is below your bar, iterate on the app and re-run.
- When errors recur, run `python3 bin/learn-suggest.py` and consider applying suggestions from `.dev/planning/AUTO_SKILL_UPDATES.md` to your skills/rules.

