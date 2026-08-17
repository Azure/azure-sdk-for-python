# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

from azure.core.exceptions import ResourceNotFoundError

from azure.ai.projects import AIProjectClient


def create_github_issue(owner: str, repository: str, token: str, *, title: str, assignee: str) -> None:
    """Create and assign a GitHub issue using the REST API."""
    request = urllib.request.Request(
        url=f"https://api.github.com/repos/{owner}/{repository}/issues",
        data=json.dumps({"title": title, "assignees": [assignee]}).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "azure-ai-projects-sample",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        issue = json.load(response)

    print(f"Created GitHub issue #{issue['number']}: {issue['html_url']}")


def start_issue_creation_thread(
    owner: str, repository: str, token: str | None, assignee: str, *, title: str = "Testing routine"
) -> threading.Thread | None:
    """Create the trigger issue in parallel so polling can begin immediately."""
    if not token:
        print("GITHUB_PAT_TOKEN is not set; skipping automatic issue creation.")
        return None

    def worker() -> None:
        try:
            create_github_issue(owner, repository, token, title=title, assignee=assignee)
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            print(f"Failed to create GitHub issue: {exc.code} {exc.reason} {details}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Failed to create GitHub issue: {exc}")

    thread = threading.Thread(target=worker, name="github-issue-trigger", daemon=True)
    thread.start()
    return thread
