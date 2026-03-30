# Benchmark evaluation agent

This repository ships **evaluation only**: run the scoring pipeline, read results and history, and optionally drive error-learning suggestions. **Planning and building** apps (criteria authoring, implementing fixes) are **not** part of this repo’s published surface; keep any such Cursor prompts **locally** if you use them.

The published agent definition is:

| Agent | Role |
|-------|------|
| **benchmark-evaluating** | Run `bin/eval.py run`, interpret `results/<app_id>_result.json` and history, optionally `bin/learn-suggest.py`; report grade and failures. |

## Definition file

- **`.cursor/agents/benchmark-evaluating.md`** — use as `@` context in Cursor or paste into a task prompt so the model follows the evaluation workflow.

## How to invoke

- **Cursor:** `@benchmark-evaluating.md` (or open that file and reference it) and specify app id (e.g. `APP001`) or path (e.g. `test-apps/MyApp`).
- **Task / subagent tools:** If your environment exposes a `benchmark-evaluating` type, use it with a clear request (e.g. “Evaluate `test-apps/MyApp` and summarize grade and lint errors”).
- **Without an agent session:** run the same commands yourself from the repo root; see [AGENT_BENCHMARK_PLAN.md](AGENT_BENCHMARK_PLAN.md).

## Local-only planning/building prompts

If you maintain your own **`benchmark-planning.md`** or **`benchmark-building.md`** under `.cursor/agents/`, those paths are **gitignored** so they are not committed with this repository.

Full execution contract: [AGENT_BENCHMARK_PLAN.md](AGENT_BENCHMARK_PLAN.md). Architecture: [ARCHITECTURE_AND_FLOW.md](ARCHITECTURE_AND_FLOW.md).
