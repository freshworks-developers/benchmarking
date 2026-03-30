# Freshworks Platform 3.0 benchmarking suite

Production tooling for **Freshworks developers** to validate and score Platform 3.0 marketplace apps (FDK, compliance, Crayons, structure) using **IDE-integrated evaluation**, slash-style eval intents, and a stable `bin/` interface. The README stays concise; procedural detail lives in `docs/`.

---

## 1. Setup

1. **Clone** this repository and **open the repo root** in Cursor (or your IDE). Workspace rule **`.cursor/rules/benchmark-eval.mdc`** keeps evaluation behavior consistent.
2. **Python:** `pip install -r requirements.txt`
3. **FDK** (required for validation):  
   `npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g`  
   Ensure `fdk` is on your `PATH`.
4. **`lib/`:** Listed in `.gitignore` by policy. The Python package must exist **locally** next to `bin/` for `bin/*.py` and tests. Obtain it from your team’s distribution if your clone does not include it.

---

## 2. Evaluation workflow

This repo documents **running and interpreting the benchmark**, not authoring apps or criteria.

- **Agent prompt:** **`.cursor/agents/benchmark-evaluating.md`** — `@`-mention it in Cursor (or paste its contents) and ask for an evaluation (e.g. app id `APP001`, path `test-apps/MyApp`). Details: **[docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md)**.
- **Inputs:** An app under **`test-apps/`** (or a path you pass to eval) and, when applicable, **`test-criteria/<id>-criteria.json`** — produced outside this README’s scope.
- **Outputs:** `results/<app_id>_result.json`, `results/eval_history.jsonl`; see §4.

**Contract:** prerequisites, commands, exit codes — **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)**.

---

## 3. Slash-style eval intents

Phrases like `/eval run …` are **intent labels**; map them to the repo CLI from **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)**. Configure Cursor custom commands or rely on the agent + `benchmark-eval` rule to run the equivalent `python3 bin/eval.py …` from the **repo root**.

**Full benchmark vs FDK only:** “Validate this app” here means the **evaluation pipeline** described in AGENT_BENCHMARK_PLAN, not a one-off `fdk validate` unless you ask for that explicitly.

---

## 4. Outputs

| Artifact | Location |
|----------|----------|
| Latest run detail | `results/<app_id>_result.json` (generated; typically gitignored) |
| Run history | `results/eval_history.jsonl` |
| Suggested rule/skill updates | `.dev/planning/AUTO_SKILL_UPDATES.md` (after suggest / `--learn` flows) |

**Scoring:** 100-point scale, grades A–F; breakdown in each result file.

**Sample packaged use-case ids:** `APP001`–`APP007` in `use-cases/use_cases.json` (for apps you already placed under `test-apps/`).

---

## 5. Apps and criteria on disk

- App tree: **`test-apps/<id>/`** (or path passed to `bin/eval.py run`).
- Criteria: **`test-criteria/<id>-criteria.json`** when your flow uses them.
- **Setup helpers:** `python3 bin/setup.py` (non-interactive), `setup_test.py` (interactive) — see [AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md).
- **Legacy generate-and-wait driver:** `automate_test.py --app <ID>` if you use predefined use cases.

---

## 6. Documentation index

| Document | Purpose |
|----------|---------|
| [docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md) | Execution plan, `bin/` commands, I/O, history analysis |
| [docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md) | Slash phrase → CLI mapping |
| [docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md) | Evaluation agent only; local-only prompts |
| [docs/ARCHITECTURE_AND_FLOW.md](docs/ARCHITECTURE_AND_FLOW.md) | Architecture (optional) |

---

## 7. Troubleshooting

| Symptom | Check |
|---------|--------|
| FDK errors | Global FDK install; commands from repo root |
| `lib` import errors | Local `lib/` package at repo root |
| Wrong paths | `test-apps/…` and criteria paths relative to repo root |
| Eval not following suite | Workspace = this repo; `@` **benchmark-evaluating.md**; rule `benchmark-eval.mdc` active |

---

## Appendix: Manual CLI and legacy scripts

For CI, debugging, or without an agent session:

- **Dispatcher:** `python3 bin/eval.py` (`run`, `results`, `history`, `status`). See [AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md) and [SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md).
- **Legacy:** `automate_test.py`, `setup_test.py`, `error_learner.py` — as documented in the plan where applicable.

**Tests:** `python3 -m pytest tests/`

---

**Last updated:** March 2026. Internal Freshworks developer tooling for marketplace app quality assurance.
