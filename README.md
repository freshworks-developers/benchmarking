# Freshworks Platform 3.0 benchmarking suite

Production tooling for **Freshworks developers** to validate and score Platform 3.0 marketplace apps (FDK, compliance, Crayons, structure) using **IDE-integrated evaluation**, slash-style eval intents, and a stable `bin/` interface. The README stays concise; procedural detail lives in `docs/`.

### Using this repo in Cursor

**Opening this repository as the workspace root is enough** for Cursor-specific behavior: the project rule **`.cursor/rules/benchmark-eval.mdc`** is set to **always apply** in this folder, so the assistant is steered toward the benchmark CLI and **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)** without any extra “enable benchmark” step. You still need the prerequisites below (Python, FDK, local `lib/`).

Phrases like `/eval run …` in **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)** are **intent labels** that map to `python3 bin/eval.py …`; the rule helps the model run those commands from the **repo root** when you ask in natural language or slash-style wording.

---

## 1. Setup

1. **Clone** this repository and **open the repo root** in Cursor (or your IDE)—the folder that contains `bin/`, `docs/`, and `.cursor/`.
2. **Python:** `pip install -r requirements.txt`
3. **FDK** (required for validation):  
   `npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g`  
   Ensure `fdk` is on your `PATH`.
4. **`lib/`:** Listed in `.gitignore` by policy. The Python package must exist **locally** next to `bin/` for `bin/*.py` and tests. Obtain it from your team’s distribution if your clone does not include it.

---

## 2. Evaluation workflow

This repo documents **running and interpreting the benchmark**.

- **Agent prompt:** **`.cursor/agents/benchmark-evaluating.md`** — `@`-mention it in Cursor (or paste its contents) and ask for an evaluation. Details: **[docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md)**.
- **App input:** See **§5** — you can use a **bare app id** or **any path** to app source; not limited to `test-apps/`.
- **Outputs:** Scores and history are written under **`results/` inside this repo** (see §4), regardless of where the app lives on disk.

**Contract:** prerequisites, commands, exit codes — **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)**.

---

## 3. Slash-style eval intents

Phrases like `/eval run …` are **intent labels**; map them to the repo CLI from **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)**. Configure Cursor custom commands or rely on the agent + `benchmark-eval` rule to run the equivalent `python3 bin/eval.py …` from the **repo root**.

**Full benchmark vs FDK only:** “Validate this app” here means the **evaluation pipeline** described in AGENT_BENCHMARK_PLAN, not a one-off `fdk validate` unless you ask for that explicitly.

---

## 4. Outputs

All benchmark artifacts below are created **under this repository’s root** (not next to the app folder):

| Artifact | Location |
|----------|----------|
| Latest run detail | `results/<app_id>_result.json` (generated; typically gitignored) |
| Run history | `results/eval_history.jsonl` |
| Suggested rule/skill updates | `.dev/planning/AUTO_SKILL_UPDATES.md` (after suggest / `--learn` flows) |

`<app_id>` is the resolved id for the run (from your argument or inferred from the app directory name; use **`--app-id`** on `bin/eval.py run` when you want a stable name).

**Scoring:** 100-point scale, grades A–F; breakdown in each result file.

**Sample packaged use-case ids:** `APP001`–`APP007` in `use-cases/use_cases.json` — typically used with apps under `test-apps/<id>/`, but evaluation itself accepts any valid app path (§5).

---

## 5. Apps and criteria on disk

**How you point at app code**

| What you pass to `bin/eval.py run` | Resolved app directory |
|-----------------------------------|-------------------------|
| **Bare id** (e.g. `APP001`) | `test-apps/APP001/` relative to this repo |
| **Path with `/` or `\\`** | That path: **relative paths are from the repo root**; **absolute paths** are allowed (e.g. another checkout or a customer app tree elsewhere) |

So the app **does not** have to live under `test-apps/` unless you use the short id form.

**Criteria (optional):** If `test-criteria/<resolved_app_id>-criteria.json` exists, it is picked up automatically. Otherwise requirements can come from flags / `automate_test` / use cases as described in [AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md).

**Stable result filenames:** If the folder name is awkward, pass **`--app-id MYAPP`** so `results/MYAPP_result.json` and history use that id.

**Setup helpers:** `python3 bin/setup.py` (non-interactive), `setup_test.py` (interactive) — see [AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md).

**Legacy generate-and-wait driver:** `automate_test.py --app <ID>` for predefined use cases; **`--benchmark-dir`** changes where that mode looks for app folders, but **result files still go to `results/`** in this repo.

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
| Wrong paths | Bare id → `test-apps/<id>`; paths → relative to **repo root** or use an **absolute** path to the app |
| Eval not following suite | Workspace = this repo root; `@` **benchmark-evaluating.md**; rule `benchmark-eval.mdc` active |

---

## Appendix: Manual CLI and legacy scripts

For CI, debugging, or without an agent session:

- **Dispatcher:** `python3 bin/eval.py` (`run`, `results`, `history`, `status`). See [AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md) and [SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md).
- **Legacy:** `automate_test.py`, `setup_test.py`, `error_learner.py` — as documented in the plan where applicable.

**Tests:** `python3 -m pytest tests/`

---

**Last updated:** March 2026. Internal Freshworks developer tooling for marketplace app quality assurance.
