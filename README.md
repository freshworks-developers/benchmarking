# Freshworks Platform 3.0 benchmarking suite

This repository is set up for **AI agent learners** and **Cursor (or similar) workflows**: you clone the project, open it in your editor, and drive **planning, building, and evaluation through agents**—not by memorizing shell commands first. Human reviewers can still run the same checks manually; those steps are in the appendix at the bottom.

---

## 1. Install and open the repo (everyone)

Do this once so the agent can run validation and scoring.

1. **Clone** this repository and **open the repo root** in Cursor (or your IDE). The bundled **`.cursor/rules/benchmark-eval.mdc`** applies in this workspace and steers the AI toward the correct evaluation flow.
2. **Python:** `pip install -r requirements.txt`
3. **FDK** (required for real validation):  
   `npm install https://cdn.freshdev.io/fdk/latest-v24.tgz -g`  
   Confirm `fdk` is on your `PATH`.
4. **`lib/`:** The `lib/` directory is **gitignored**. Your environment still needs those Python modules at the repo root for tools to run. If your clone has no `lib/`, get the folder from your instructor or internal instructions and place it next to `bin/`.

Tell the agent: *“We’re in the benchmarking repo root; follow AGENT_BENCHMARK_PLAN and use the evaluation agents.”*

---

## 2. Primary workflow: benchmark agents (plan → build → evaluate)

Three roles mirror how you should work through an exercise. Full detail: **[docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md)**. Agent prompts live under **`.cursor/agents/`**.

| Agent | File to @-mention or paste | Role |
|-------|-----------------------------|------|
| **Planning** | `.cursor/agents/benchmark-planning.md` | Turn requirements or a use-case id into criteria (`test-criteria/…`), expected files, optional planning notes. |
| **Building** | `.cursor/agents/benchmark-building.md` | Implement or fix the app (Platform 3.0, Crayons, manifest). Does not substitute for the evaluation step. |
| **Evaluating** | `.cursor/agents/benchmark-evaluating.md` | Run the benchmark, interpret scores, suggest fixes; may use learning outputs. |

**Typical chat pattern in Cursor**

1. Start a thread and **attach the agent file** you need (e.g. type `@` and choose `benchmark-evaluating.md`), *or* paste that file’s contents into your first message so the model stays in role.
2. Say what you want in plain language, for example:
   - *“Using the evaluating agent: run a full benchmark for app id `APP001` and summarize grade and failures.”*
   - *“Plan criteria for use-case `APP006` from `use-cases/use_cases.json`.”*
   - *“After this eval result, suggest concrete manifest and file fixes.”*
3. If your course uses a **Task** or **subagent** feature, request the matching type when documented (e.g. `benchmark-evaluating`) as described in [BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md).

**Pipeline:** plan (criteria) → build (app under `test-apps/`) → evaluate → iterate from the result JSON and suggestions.

Execution contract (inputs, outputs, history files, exit codes): **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)**.

---

## 3. Slash-style commands and validation requests

Courses and rules often phrase work as **slash commands** or **“run validation”**. Those are *names for intents*; your agent should map them to the repo tooling. Official mapping table: **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)**.

| You say (examples) | What the agent should do (repo root) |
|--------------------|--------------------------------------|
| `/eval run APP001` | Run evaluation for that app id. |
| `/eval run test-apps/MyApp` | Run evaluation for that path (optionally set `--app-id`). |
| `/eval run APP001 --learn` | Run evaluation, then refresh skill-update suggestions. |
| `/eval results` / `/eval results APP001` | Show where results live or list them. |
| `/eval history` / `/eval history --last 10` | Show evaluation history. |
| `/eval status` / `/eval status APP001` | Show last run status (grade, pass/fail). |

**In Cursor:** You can define **custom slash commands** or rules that expand `/eval …` into the matching command from [SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md). If you have not wired slashes yet, ask the agent in natural language: *“Run the same thing as `/eval run APP001`”*—it should still execute the mapped tooling from the plan.

**@ validation / “validate this app”:** Point the agent at the app path or id and ask for a **full benchmark** (not only `fdk validate`). The evaluating agent should follow **AGENT_BENCHMARK_PLAN** and the workspace rule **benchmark-eval**.

---

## 4. What gets produced

- **Scores and detail:** `results/<app_id>_result.json` (gitignored locally when generated).
- **History:** `results/eval_history.jsonl`.
- **Learning suggestions:** `.dev/planning/AUTO_SKILL_UPDATES.md` (when you run suggest / `--learn` flows).

**Scoring (summary):** 100-point scale, letter grades A–F; categories include FDK validation, file structure, Platform 3.0 compliance, Crayons usage. Details remain in result JSON.

**Predefined use-case ids** (for generation-style exercises): `APP001`–`APP007` in `use-cases/use_cases.json` (Freshdesk / Freshservice mix; see table in earlier course materials or that file).

---

## 5. Documentation map

| Doc | Use |
|-----|-----|
| [docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md) | Single source for prerequisites, commands the agent may run, I/O contract, history analysis. |
| [docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md) | Slash phrase → exact command mapping. |
| [docs/BENCHMARK_AGENTS.md](docs/BENCHMARK_AGENTS.md) | Agent roles, pipeline, how to invoke. |
| [docs/ARCHITECTURE_AND_FLOW.md](docs/ARCHITECTURE_AND_FLOW.md) | Deeper architecture (optional). |

---

## 6. Troubleshooting (for you or the agent)

| Symptom | Check |
|---------|--------|
| FDK errors | Install FDK globally; run from repo root. |
| Import / `lib` errors | `lib/` present at repo root (ignored by git). |
| Wrong app path | Paths relative to repo root: `test-apps/<id>` or as given in criteria. |
| Agent ignores benchmark flow | Ensure workspace is **this** repo so `.cursor/rules/benchmark-eval.mdc` applies; @-mention **benchmark-evaluating.md**. |

---

## Appendix A: Manual CLI (optional)

Use this if you are **not** going through an agent or you are debugging.

The **dispatcher** is `python3 bin/eval.py` with subcommands `run`, `results`, `history`, `status`. Other `bin/*.py` scripts cover setup, criteria conversion, and learning. Copy-paste examples and flags: **[docs/AGENT_BENCHMARK_PLAN.md](docs/AGENT_BENCHMARK_PLAN.md)** and **[docs/SLASH_COMMANDS.md](docs/SLASH_COMMANDS.md)**.

**Legacy interactive driver:** `automate_test.py` (generate-and-wait flows, `--evaluate`, `--show-stats`). **Interactive criteria:** `setup_test.py`.

**Tests:** `python3 -m pytest tests/`

---

**Last updated:** March 2026. Internal Freshworks tooling for marketplace app quality assurance.
