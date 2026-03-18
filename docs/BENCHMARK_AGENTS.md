# Benchmark Agents

This document describes the three sub-agents for the Freshworks Platform 3.0 benchmarking suite: **planning**, **building**, and **evaluating**. They mirror the structure of the agents in the appathon-q3-2025 `.cursor/agents/` folder and are intended to be invoked via the Task tool or used as prompt context for a general-purpose agent.

## Agent roles

| Agent | Role | When to use |
|-------|------|-------------|
| **benchmark-planning** | Scope and plan: requirements or use-case → criteria JSON, expected_files, optional planning doc. | Setting up a new app slot, converting requirements to test-criteria, or defining what to build before building. |
| **benchmark-building** | Implement or adapt the app from plan/criteria; Platform 3.0, Crayons, manifest, structure. | You have criteria or a plan and need to build or fix the app. Does not run evaluation. |
| **benchmark-evaluating** | Run evaluation (`bin/eval.py run`), interpret results, optionally `learn-suggest`; report grade and suggest fixes. | You need to validate and score an app or analyze evaluation history. |

## Pipeline: plan → build → evaluate

1. **Planning** — Requirements or use-case id → criteria file (`test-criteria/<app_id>-criteria.json`) and optionally a planning doc. Uses `use-cases/use_cases.json`, `bin/setup.py`, `bin/convert-criteria.py`.
2. **Building** — Criteria/plan + app path → implement or adapt app; run `fdk validate` until it passes. Uses app-dev skill and `.cursor/rules/benchmark-eval.mdc`. Does not run evaluation.
3. **Evaluating** — App id or path → run `python3 bin/eval.py run <app_id_or_path>`, read result and history, optionally `bin/learn-suggest.py`; report grade and suggest fixes from `.dev/planning/AUTO_SKILL_UPDATES.md`.

You can loop: after evaluation, use the result (and AUTO_SKILL_UPDATES) to hand back to the building agent for fixes, then re-run the evaluating agent.

## How to invoke

- **Task tool (if your environment supports these subagent types):** Use the Task tool with `subagent_type` set to `benchmark-planning`, `benchmark-building`, or `benchmark-evaluating` and a clear task description (e.g. "Plan from use-case APP001" or "Evaluate app test-apps/MyApp").
- **General-purpose agent:** If only a generic agent type is available, invoke it with the **prompt from the agent file** so the agent behaves as that role. Copy the contents of:
  - `.cursor/agents/benchmark-planning.md`
  - `.cursor/agents/benchmark-building.md`
  - `.cursor/agents/benchmark-evaluating.md`
  and use as the task prompt along with your specific request (e.g. "Evaluate APP001" or "Create criteria for the following requirements: ...").

Agent definitions live in [.cursor/agents/](../.cursor/agents/) (one markdown file per agent). The full execution plan for evaluation is in [AGENT_BENCHMARK_PLAN.md](AGENT_BENCHMARK_PLAN.md); architecture and flows are in [ARCHITECTURE_AND_FLOW.md](ARCHITECTURE_AND_FLOW.md).
