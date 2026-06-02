#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib import request


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATE_API_SCRIPT = REPO_ROOT / "scripts" / "generate_api_text.py"
DEFAULT_CONSISTENCY_MARKER = "<!-- api-md-consistency-comment -->"
DEFAULT_APPLY_MARKER = "<!-- api-md-apply-result-comment -->"


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not lines:
        path.write_text("", encoding="utf-8")
        return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_github_output(key: str, value: str | int) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")


def env_path(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default))


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required")
    return value


def github_request(method: str, url: str, token: str, data: dict[str, Any] | None = None) -> Any:
    payload = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, method=method, data=payload, headers=headers)
    with request.urlopen(req) as response:
        text = response.read().decode("utf-8")
        if not text:
            return None
        return json.loads(text)


def list_comments(owner: str, repo: str, pr_number: int, token: str) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
            f"?per_page=100&page={page}"
        )
        batch = github_request("GET", url, token)
        if not isinstance(batch, list) or not batch:
            break
        comments.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return comments
