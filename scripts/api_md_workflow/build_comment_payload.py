#!/usr/bin/env python

from __future__ import annotations

import json
import os

from common import DEFAULT_CONSISTENCY_MARKER, env_path, read_lines, require_env


def main() -> int:
    marker = os.environ.get("API_MD_COMMENT_MARKER", DEFAULT_CONSISTENCY_MARKER)
    pr_number = int(require_env("PR_NUMBER"))
    repository = require_env("REPOSITORY")
    run_id = require_env("RUN_ID")
    run_attempt = int(require_env("RUN_ATTEMPT"))
    mismatch_count = int(require_env("MISMATCH_COUNT"))
    changed_count = int(require_env("CHANGED_COUNT"))
    mismatches_file = env_path("API_MD_MISMATCHES_FILE", ".artifacts/mismatched_api_files.txt")
    out_file = env_path("API_MD_COMMENT_FILE", ".artifacts/comment/comment.json")

    mismatches = read_lines(mismatches_file)
    run_url = f"https://github.com/{repository}/actions/runs/{run_id}/attempts/{run_attempt}"

    if changed_count == 0:
        body = (
            "## API.md consistency\n\n"
            "No SDK package changes were detected in this PR."
        )
    elif mismatch_count == 0:
        body = (
            "## API.md consistency\n\n"
            f"Checked {changed_count} affected package(s). All generated API.md files are up to date."
        )
    elif run_attempt == 1:
        lines = "\n".join(f"- `{path}`" for path in mismatches)
        body = (
            "## API.md consistency\n\n"
            "Generated API.md differs from files in this branch.\n\n"
            "### Files that need update\n"
            f"{lines}\n\n"
            "### Apply updates to this same PR\n"
            f"- Click [this workflow run]({run_url}).\n"
            "- In the Actions UI, click `Re-run all jobs`.\n"
            "- On rerun, this workflow will commit regenerated API.md files directly to this PR branch.\n\n"
            "No PR number input is required."
        )
    else:
        body = (
            "## API.md consistency\n\n"
            "API.md updates are being applied for this PR rerun."
        )

    payload = {
        "marker": marker,
        "pr_number": pr_number,
        "body": body,
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
