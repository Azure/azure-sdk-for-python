#!/usr/bin/env python

from __future__ import annotations

import json
import os

from common import DEFAULT_APPLY_MARKER, env_path, require_env


def main() -> int:
    created = require_env("COMMIT_CREATED").lower() == "true"
    pr_number = int(require_env("PR_NUMBER"))
    head_ref = require_env("HEAD_REF")
    run_url = require_env("RUN_URL")
    commit_sha = os.environ.get("COMMIT_SHA", "")
    marker = os.environ.get("API_MD_APPLY_MARKER", DEFAULT_APPLY_MARKER)
    out_file = env_path("API_MD_APPLY_RESULT_FILE", ".artifacts/comment/apply-result.json")

    if created:
        body = "\n".join(
            [
                "API.md updates have been committed to this PR branch.",
                "",
                f"- Branch: `{head_ref}`",
                f"- Commit: `{commit_sha}`",
                f"- Run: {run_url}",
            ]
        )
    else:
        body = "\n".join(
            [
                "No API.md changes were required after regeneration.",
                "",
                f"- Branch: `{head_ref}`",
                f"- Run: {run_url}",
            ]
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
