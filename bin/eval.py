#!/usr/bin/env python3
"""
Eval dispatcher: run, results, history, status.
Usage:
  python bin/eval.py run APP001
  python bin/eval.py run test-apps/MyApp [--app-id MYAPP]
  python bin/eval.py results [APP_ID]
  python bin/eval.py history [--app-id ID] [--last N] [--json]
  python bin/eval.py status [APP_ID] [--json]
Exit: 0 success, 1 failure, 2 invalid args.
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Add repo root so we can import lib
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lib.resolve import get_repo_root, resolve_app
from lib.history import append_from_result_file, summarize


def cmd_run(args: argparse.Namespace) -> int:
    app_id_or_path = args.app_id_or_path
    app_id_override = getattr(args, "app_id", None)
    learn = getattr(args, "learn", False)
    try:
        app_path, app_id, _criteria_path, requirements_arg = resolve_app(
            app_id_or_path, app_id_override
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    repo = get_repo_root()
    automate = repo / "automate_test.py"
    cmd = [
        sys.executable,
        str(automate),
        "--evaluate", str(app_path),
        "--app-id", app_id,
    ]
    if requirements_arg:
        cmd.extend(["--requirements", requirements_arg])
    result = subprocess.run(cmd, cwd=str(repo))
    if result.returncode != 0:
        return 1
    # Append to history (use latest result file in case automation used different app_id)
    results_dir = repo / "results"
    result_files = list(results_dir.glob("*_result.json"))
    if result_files:
        latest = max(result_files, key=lambda p: p.stat().st_mtime)
        rid = latest.stem.replace("_result", "")
        append_from_result_file(rid, result_file=latest)
    if learn:
        subprocess.run(
            [sys.executable, str(automate), "--generate-skill-updates"],
            cwd=str(repo),
        )
    return 0


def cmd_results(args: argparse.Namespace) -> int:
    repo = get_repo_root()
    results_dir = repo / "results"
    app_id = getattr(args, "app_id", None)
    as_json = getattr(args, "json", False)
    if app_id:
        path = results_dir / f"{app_id}_result.json"
        if not path.exists():
            print(f"No result file for {app_id}", file=sys.stderr)
            return 1
        if as_json:
            import json
            with open(path) as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print(str(path))
        return 0
    if not results_dir.exists():
        if as_json:
            print("[]")
        else:
            print("No results directory.")
        return 0
    files = sorted(p.name for p in results_dir.glob("*_result.json"))
    if as_json:
        import json
        print(json.dumps({"result_files": files}))
    else:
        for f in files:
            print(f)
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    app_id = getattr(args, "app_id", None)
    last_n = getattr(args, "last", None)
    as_json = getattr(args, "json", False)
    out = summarize(app_id=app_id, last_n=last_n, as_json=as_json)
    print(out)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    repo = get_repo_root()
    results_dir = repo / "results"
    app_id = getattr(args, "app_id", None)
    as_json = getattr(args, "json", False)
    if app_id:
        path = results_dir / f"{app_id}_result.json"
        if not path.exists():
            print(f"No result for {app_id}", file=sys.stderr)
            return 1
        import json
        with open(path) as f:
            data = json.load(f)
        score = data.get("score", {})
        validation = data.get("validation", {})
        if as_json:
            print(json.dumps({
                "app_id": app_id,
                "grade": score.get("grade"),
                "score": score.get("total_score"),
                "validation_success": validation.get("success"),
            }))
        else:
            print(f"app_id: {app_id}  grade: {score.get('grade')}  pass: {validation.get('success')}")
        return 0
    # All apps: list latest from history or result files
    from lib.history import read_history
    records = read_history(last_n=20)
    if not records:
        # Fallback: list result files
        if results_dir.exists():
            for p in sorted(results_dir.glob("*_result.json")):
                app_id = p.stem.replace("_result", "")
                import json
                with open(p) as f:
                    d = json.load(f)
                s = d.get("score", {})
                v = d.get("validation", {})
                print(f"{app_id}: grade={s.get('grade')} pass={v.get('success')}")
        return 0
    seen = set()
    for r in reversed(records):
        aid = r.get("app_id")
        if aid and aid not in seen:
            seen.add(aid)
            print(f"{aid}: grade={r.get('grade')} pass={r.get('validation_success')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Eval dispatcher: run, results, history, status",
        prog="eval",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    # run
    p_run = sub.add_parser("run", help="Run evaluation for an app")
    p_run.add_argument("app_id_or_path", help="App ID (e.g. APP001) or path (e.g. test-apps/MyApp)")
    p_run.add_argument("--app-id", help="Override app ID when using path")
    p_run.add_argument("--learn", action="store_true", help="Run --generate-skill-updates after eval")
    p_run.set_defaults(func=cmd_run)
    # results
    p_results = sub.add_parser("results", help="Show result file path or list results")
    p_results.add_argument("app_id", nargs="?", help="App ID")
    p_results.add_argument("--json", action="store_true", help="Machine-readable output")
    p_results.set_defaults(func=cmd_results)
    # history
    p_history = sub.add_parser("history", help="Show evaluation history")
    p_history.add_argument("--app-id", help="Filter by app ID")
    p_history.add_argument("--last", type=int, metavar="N", help="Last N runs")
    p_history.add_argument("--json", action="store_true", help="Machine-readable output")
    p_history.set_defaults(func=cmd_history)
    # status
    p_status = sub.add_parser("status", help="Show last run status for app(s)")
    p_status.add_argument("app_id", nargs="?", help="App ID (optional)")
    p_status.add_argument("--json", action="store_true", help="Machine-readable output")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
