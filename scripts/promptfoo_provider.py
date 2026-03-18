#!/usr/bin/env python3
"""
Promptfoo custom script provider: runs benchmarking eval and prints result JSON to stdout.
Receives (context, options, prompt) as arguments; context and options are JSON strings.
Use app_id or path from context.vars or from the prompt text.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: promptfoo_provider.py <context_json> <options_json> <prompt>"}), file=sys.stderr)
        sys.exit(1)
    context_str, options_str, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        context = json.loads(context_str)
    except json.JSONDecodeError:
        context = {}
    vars_ = context.get("vars", {})
    app_id = vars_.get("app_id") or vars_.get("app_path")
    if not app_id and prompt:
        prompt_stripped = prompt.strip()
        if prompt_stripped:
            app_id = prompt_stripped.split()[0] if prompt_stripped else None
    if not app_id:
        out = json.dumps({"error": "No app_id or app_path in context.vars or prompt"})
        print(out)
        return
    cmd = [
        sys.executable,
        str(REPO_ROOT / "bin" / "eval.py"),
        "run",
        str(app_id),
    ]
    if vars_.get("app_id") and app_id != vars_.get("app_id"):
        cmd.extend(["--app-id", str(vars_.get("app_id"))])
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    results_dir = REPO_ROOT / "results"
    result_file = results_dir / f"{app_id}_result.json"
    if not result_file.exists():
        # Use most recently modified result file (from this run)
        result_files = list(results_dir.glob("*_result.json"))
        result_file = max(result_files, key=lambda p: p.stat().st_mtime) if result_files else None
    if result_file and result_file.exists():
        with open(result_file) as f:
            data = json.load(f)
        print(json.dumps(data))
    else:
        print(json.dumps({
            "error": "Eval did not produce a result file",
            "stderr": result.stderr or "",
            "returncode": result.returncode,
        }))


if __name__ == "__main__":
    main()
