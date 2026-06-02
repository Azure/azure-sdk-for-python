#!/usr/bin/env python

from __future__ import annotations

import json
import os

from common import DEFAULT_CONSISTENCY_MARKER, env_path, github_request, list_comments


def main() -> int:
    comment_file = env_path("COMMENT_FILE", ".artifacts/comment/comment.json")
    payload = json.loads(comment_file.read_text(encoding="utf-8"))

    marker = payload.get("marker") or os.environ.get("DEFAULT_MARKER") or DEFAULT_CONSISTENCY_MARKER
    default_pr = int(os.environ.get("DEFAULT_PR_NUMBER", "0") or "0")
    pr_number = int(payload.get("pr_number") or default_pr)
    if pr_number <= 0:
        raise ValueError("No PR number available for comment publishing.")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required to post comments.")

    repo_full_name = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full_name:
        raise ValueError("GITHUB_REPOSITORY is missing or invalid.")
    owner, repo = repo_full_name.split("/", 1)

    body = f"{marker}\n{payload.get('body') or 'API.md consistency finished.'}"

    comments = list_comments(owner, repo, pr_number, token)
    existing = None
    for comment in comments:
        user = comment.get("user") or {}
        comment_body = comment.get("body") or ""
        if user.get("type") == "Bot" and marker in comment_body:
            existing = comment
            break

    if existing:
        update_url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{existing['id']}"
        github_request("PATCH", update_url, token, {"body": body})
        print(f"Updated comment on PR #{pr_number}")
    else:
        create_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        github_request("POST", create_url, token, {"body": body})
        print(f"Created comment on PR #{pr_number}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
