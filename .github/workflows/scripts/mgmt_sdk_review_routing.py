#!/usr/bin/env python3
"""Authorize review requests using GitHub metadata, never PR artifacts or code."""

import datetime
import json
import os
import re
import subprocess

INTAKE_WORKFLOW = "pr-review-intake.yml"
REVIEW_WORKFLOW = "mgmt-sdk-pr-review.lock.yml"
REVIEW_LABEL = "mgmt-review-needed"
REPOSITORY = "Azure/azure-sdk-for-python"
DEFAULT_REF = "refs/heads/main"


def positive_integer(value):
    if not re.fullmatch(r"[1-9][0-9]{0,15}", str(value)):
        raise ValueError("Review request IDs must be positive integers.")
    return int(value)


def timestamp(value):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def has_review_label(pull):
    return any(label.get("name") == REVIEW_LABEL for label in pull.get("labels", []))


def authorized_request(client, run_id, event_id=None, pr_number=None, head_sha=None):
    """Resolve a unique, current label request, including runs from fork PRs."""
    root = f"/repos/{client.repository}"
    run = client.get(f"{root}/actions/runs/{positive_integer(run_id)}")
    workflow = client.get(f"{root}/actions/workflows/{INTAKE_WORKFLOW}")
    if (
        run.get("id") != positive_integer(run_id)
        or run.get("workflow_id") != workflow["id"]
        or run.get("repository", {}).get("full_name") != REPOSITORY
        or run.get("event") != "pull_request"
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or not re.fullmatch(r"[0-9a-f]{40}", run.get("head_sha", ""))
    ):
        raise ValueError("Expected a successful PR Review Intake run in the upstream repository.")
    job_page = client.get(
        f"{root}/actions/runs/{run['id']}/attempts/{positive_integer(run['run_attempt'])}/jobs?per_page=100"
    )
    jobs = job_page["jobs"]
    requests = [job for job in jobs if job.get("name") == "request"]
    if (
        job_page["total_count"] != len(jobs)
        or len(requests) != 1
        or requests[0].get("status") != "completed"
        or requests[0].get("conclusion") != "success"
    ):
        return None

    # workflow_run.pull_requests can be empty for fork PRs.
    pulls, truncated = client.paged_get(f"{root}/commits/{run['head_sha']}/pulls", max_items=100)
    candidates = [
        pull
        for pull in pulls
        if pull.get("state") == "open"
        and (pull.get("base", {}).get("repo") or {}).get("full_name") == REPOSITORY
        and (pull.get("head", {}).get("repo") or {}).get("id")
        == positive_integer((run.get("head_repository") or {}).get("id"))
        and pull.get("head", {}).get("sha") == run["head_sha"]
        and has_review_label(pull)
    ]
    if truncated or len(candidates) > 1:
        raise ValueError("The intake must identify one unambiguous PR review target.")
    if not candidates:
        return None
    number = positive_integer(candidates[0]["number"])
    pull = client.get(f"{root}/pulls/{number}")
    if (
        pull.get("number") != number
        or pull.get("state") != "open"
        or (pull.get("base", {}).get("repo") or {}).get("full_name") != REPOSITORY
        or (pull.get("head", {}).get("repo") or {}).get("id") != run["head_repository"]["id"]
        or pull.get("head", {}).get("sha") != run["head_sha"]
        or not has_review_label(pull)
    ):
        return None
    if pr_number is not None and (number != positive_integer(pr_number) or head_sha != run["head_sha"]):
        raise ValueError("The dispatched PR or head does not match the intake.")
    events, truncated = client.paged_get(f"{root}/issues/{number}/events", max_items=3000)
    if truncated:
        raise ValueError("The complete label history is required to authorize a review.")
    changes = [
        event
        for event in events
        if event.get("event") in ("labeled", "unlabeled") and event.get("label", {}).get("name") == REVIEW_LABEL
    ]
    if not changes:
        return None
    latest = max(changes, key=lambda event: (timestamp(event["created_at"]), positive_integer(event["id"])))
    age = (timestamp(run["created_at"]) - timestamp(latest["created_at"])).total_seconds()
    if (
        latest["event"] != "labeled"
        or latest.get("actor", {}).get("id") != positive_integer((run.get("actor") or {}).get("id"))
        or not 0 <= age <= 300
        or (event_id is not None and positive_integer(event_id) != latest["id"])
    ):
        return None
    actor = latest["actor"]
    login = actor.get("login", "")
    if not re.fullmatch(r"[A-Za-z0-9-]+", login) or actor.get("type") != "User":
        raise ValueError("Only repository maintainers may request an automated review.")
    permission = client.get(f"{root}/collaborators/{login}/permission")
    if permission.get("permission") not in ("admin", "maintain", "write"):
        raise ValueError("The label requester must have repository write access.")
    return {
        "pr_number": str(number),
        "head_sha": run["head_sha"],
        "request_run_id": str(run["id"]),
        "request_event_id": str(latest["id"]),
    }


def route_review(client, event, ref):
    if client.repository != REPOSITORY or ref != DEFAULT_REF:
        raise ValueError("Review routing must execute on the upstream default branch.")
    request = authorized_request(client, event["workflow_run"]["id"])
    if request is None:
        print("No current, attributable management SDK review request; nothing to dispatch.")
        return
    command = ["gh", "workflow", "run", REVIEW_WORKFLOW, "--repo", REPOSITORY, "--ref", "main"]
    for name, value in request.items():
        command.extend(["-f", f"{name}={value}"])
    subprocess.run(command, check=True, timeout=30)


if __name__ == "__main__":
    from mgmt_sdk_review_context import GitHubClient

    if os.environ["GITHUB_EVENT_NAME"] != "workflow_run":
        raise ValueError("The router requires a workflow_run event.")
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as source:
        payload = json.load(source)
    route_review(
        GitHubClient(os.environ["GH_REPOSITORY"], os.environ["GH_TOKEN"]),
        payload,
        os.environ["GITHUB_REF"],
    )
