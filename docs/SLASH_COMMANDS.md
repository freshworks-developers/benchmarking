# Slash commands and CLI mapping

Use these mappings to wire slash-style commands (e.g. in Claude Code or Cursor) to the benchmarking CLI. All commands are run from the **benchmarking repo root**.

| Slash-style command | CLI invocation |
|---------------------|----------------|
| `/eval run APP001` | `python3 bin/eval.py run APP001` |
| `/eval run test-apps/MyApp` | `python3 bin/eval.py run test-apps/MyApp` |
| `/eval run APP001 --learn` | `python3 bin/eval.py run APP001 --learn` |
| `/eval results` | `python3 bin/eval-results.py` |
| `/eval results APP001` | `python3 bin/eval-results.py APP001` |
| `/eval history` | `python3 bin/eval-history.py` |
| `/eval history --last 10` | `python3 bin/eval-history.py --last 10` |
| `/eval history --app-id APP001` | `python3 bin/eval-history.py --app-id APP001` |
| `/eval status` | `python3 bin/eval-status.py` |
| `/eval status APP001` | `python3 bin/eval-status.py APP001` |

**Single dispatcher:** You can use `bin/eval.py` with a subcommand for all eval actions:

- `python3 bin/eval.py run <app_id_or_path> [--app-id ID] [--learn]`
- `python3 bin/eval.py results [APP_ID] [--json]`
- `python3 bin/eval.py history [--app-id ID] [--last N] [--json]`
- `python3 bin/eval.py status [APP_ID] [--json]`

**Wiring in Cursor:** Add a rule or custom command that invokes the CLI above when the user types e.g. `/eval results` or `/eval run APP001`. The exact mechanism depends on your Cursor setup (e.g. `.cursor/rules` or Cursor settings).

**Wiring in Claude Code:** Document that when the user says “eval APP001” or “show eval results”, run the corresponding `python3 bin/eval.py ...` command from the benchmarking directory.
