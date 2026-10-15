"""Invoke Bug Scouter for a validated PR artifact and publish the result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

EXPECTED_REPOSITORY = "Azure/azure-sdk-for-python"
MAX_SUMMARY_CHARACTERS = 60_000
MAX_BUG_COUNT = 10_000
MAX_BUG_BASH_DOCUMENT_CHARACTERS = 190_000


class HttpResponseError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _request_json(
    method: str,
    url: str,
    *,
    token: str,
    payload: dict | None = None,
) -> tuple[object, dict[str, str]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "bug-scouter-github-action",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
            headers = {key.lower(): value for key, value in response.headers.items()}
            return body, headers
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HttpResponseError(
            exc.code, f"HTTP {exc.code} from {url}: {detail}"
        ) from exc


def _with_query(url: str, **values: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    query.update({key: value for key, value in values.items() if value})
    return urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))


def _azure_token(resource: str) -> str:
    process = subprocess.run(
        [
            "az",
            "account",
            "get-access-token",
            "--resource",
            resource,
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    token = process.stdout.strip()
    if not token:
        raise RuntimeError(f"Azure CLI returned no token for {resource}")
    return token


def _request_values(request: dict, *, require_document: bool = False) -> dict:
    if request.get("repository") != EXPECTED_REPOSITORY:
        raise ValueError("request repository is invalid")
    head_sha = str(request.get("head_sha") or "").lower()
    if len(head_sha) != 40 or any(
        character not in "0123456789abcdef" for character in head_sha
    ):
        raise ValueError("request head SHA is invalid")
    bug_bash_document = request.get("bug_bash_document")
    if require_document:
        if not isinstance(bug_bash_document, str) or not bug_bash_document.strip():
            raise ValueError("request bug-bash document is missing")
        if len(bug_bash_document) > MAX_BUG_BASH_DOCUMENT_CHARACTERS:
            raise ValueError(
                "request bug-bash document exceeds the maximum allowed size"
            )
    values = {
        "repository": EXPECTED_REPOSITORY,
        "run_id": int(request["run_id"]),
        "pr_number": int(request["pr_number"]),
        "head_sha": head_sha,
        "head_repository": str(request.get("head_repository") or ""),
        "pr_title": str(request.get("pr_title") or ""),
        "html_url": str(request.get("html_url") or ""),
    }
    if require_document:
        values["bug_bash_document"] = bug_bash_document
    return values


def _upload_blob(args, blob_name: str, wheel_path: Path) -> None:
    subprocess.run(
        [
            "az",
            "storage",
            "blob",
            "upload",
            "--auth-mode",
            "login",
            "--account-name",
            args.storage_account,
            "--container-name",
            args.container,
            "--name",
            blob_name,
            "--file",
            str(wheel_path),
            "--overwrite",
            "true",
            "--only-show-errors",
            "-o",
            "none",
        ],
        check=True,
    )


def _delete_blob(args, blob_name: str) -> None:
    subprocess.run(
        [
            "az",
            "storage",
            "blob",
            "delete",
            "--auth-mode",
            "login",
            "--account-name",
            args.storage_account,
            "--container-name",
            args.container,
            "--name",
            blob_name,
            "--only-show-errors",
            "-o",
            "none",
        ],
        check=True,
    )


def invoke(args, request: dict) -> dict:
    values = _request_values(request, require_document=True)
    wheel_path = Path(request["wheel"]).resolve()
    if not wheel_path.is_file():
        raise RuntimeError("validated wheel no longer exists")
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        raise RuntimeError("GITHUB_TOKEN is required to authorize invocation")
    _validate_live_authorization(values, github_token)

    wheel_hash = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
    owner, repository_name = values["repository"].split("/", 1)
    blob_name = (
        f"{owner.lower()}/{repository_name.lower()}/{values['pr_number']}/"
        f"{values['head_sha']}/{values['run_id']}/{wheel_path.name}"
    )
    upload_attempted = False
    primary_error = None
    try:
        upload_attempted = True
        _upload_blob(args, blob_name, wheel_path)
        payload = {
            "schema_version": 1,
            **values,
            "wheel_filename": wheel_path.name,
            "wheel_blob_name": blob_name,
            "wheel_sha256": wheel_hash,
            "bug_bash_document": values["bug_bash_document"],
        }
        token = _azure_token("https://ai.azure.com")
        started, headers = _request_json(
            "POST",
            _with_query(args.endpoint, **{"api-version": "v1"}),
            token=token,
            payload=payload,
        )
        if not isinstance(started, dict):
            raise RuntimeError(f"Bug Scouter returned an invalid response: {started}")
        invocation_id = started.get("invocation_id")
        if not isinstance(invocation_id, str) or not invocation_id:
            raise RuntimeError(
                f"Bug Scouter did not return an invocation ID: {started}"
            )

        poll_url = _with_query(
            f"{args.endpoint.rstrip('/')}/{urllib.parse.quote(invocation_id)}",
            **{
                "api-version": "v1",
                "agent_session_id": headers.get("x-agent-session-id", ""),
            },
        )
        deadline = time.monotonic() + args.timeout_minutes * 60
        while time.monotonic() < deadline:
            try:
                status, _ = _request_json("GET", poll_url, token=token)
            except HttpResponseError as exc:
                if exc.status != 401:
                    raise
                token = _azure_token("https://ai.azure.com")
                status, _ = _request_json("GET", poll_url, token=token)
            if not isinstance(status, dict):
                raise RuntimeError(f"Bug Scouter returned an invalid status: {status}")
            if status.get("state") != "running":
                return status
            print(f"Bug Scouter: {status.get('stage') or 'running'}", flush=True)
            time.sleep(args.poll_seconds)
        raise TimeoutError(
            f"Bug Scouter did not finish within {args.timeout_minutes} minutes"
        )
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        if upload_attempted:
            try:
                _delete_blob(args, blob_name)
            except Exception as cleanup_error:
                if primary_error is None:
                    raise
                print(f"Bug Scouter blob cleanup failed: {cleanup_error}", flush=True)


def _github_request(method: str, path: str, token: str, payload: dict | None = None):
    result, _ = _request_json(
        method,
        f"https://api.github.com/{path.lstrip('/')}",
        token=token,
        payload=payload,
    )
    return result


def _validate_live_authorization(request: dict, token: str) -> None:
    repository = request["repository"]
    pr_number = request["pr_number"]
    pull_request = _github_request(
        "GET", f"repos/{repository}/pulls/{pr_number}", token
    )
    if not isinstance(pull_request, dict) or pull_request.get("state") != "open":
        raise ValueError("pull request is not open")
    live_sha = str((pull_request.get("head") or {}).get("sha") or "").lower()
    if live_sha != request["head_sha"]:
        raise ValueError("pull request head SHA changed before invocation")
    labels = pull_request.get("labels")
    if not isinstance(labels, list) or "bug-scouter" not in {
        str(label.get("name") or "") for label in labels if isinstance(label, dict)
    }:
        raise ValueError("pull request does not have the bug-scouter label")


def _safe_summary(value: object, fallback: str) -> str:
    summary = str(value or fallback)[:MAX_SUMMARY_CHARACTERS]
    return summary.replace("@", "&#64;")


def _bug_count(result: dict) -> int:
    value = result.get("real_bug_count")
    if isinstance(value, bool):
        raise ValueError("real_bug_count must be an integer")
    try:
        bug_count = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("real_bug_count must be an integer") from exc
    if bug_count < 0 or bug_count > MAX_BUG_COUNT:
        raise ValueError("real_bug_count is outside the allowed range")
    return bug_count


def publish(
    request: dict, response: dict, *, github_token: str, target_url: str
) -> str:
    values = _request_values(request)
    result = response.get("result") if isinstance(response, dict) else None
    if response.get("state") != "completed" or not isinstance(result, dict):
        state, description = "error", "Bug Scouter infrastructure failure"
        summary = "## Bug Scouter - infrastructure failure"
    elif result.get("status") != "ok":
        state, description = "error", "Bug Scouter pipeline failed"
        summary = "## Bug Scouter - pipeline failed"
    else:
        try:
            bug_count = _bug_count(result)
        except ValueError:
            state, description = "error", "Bug Scouter returned an invalid result"
            summary = "## Bug Scouter - invalid result"
        else:
            state = "success" if bug_count == 0 else "failure"
            description = (
                "No real bugs found"
                if bug_count == 0
                else f"{bug_count} real bug(s) found"
            )
            summary = _safe_summary(result.get("summary_markdown"), description)

    repository = values["repository"]
    _github_request(
        "POST",
        f"repos/{repository}/statuses/{values['head_sha']}",
        github_token,
        {
            "state": state,
            "context": "Bug Scouter",
            "description": description[:140],
            "target_url": target_url,
        },
    )
    marker = f"<!-- bug-scouter:{values['head_sha']} -->"
    body = f"{marker}\n{summary}\n\n[Workflow run]({target_url})"
    comments = []
    for page in range(1, 11):
        batch = _github_request(
            "GET",
            f"repos/{repository}/issues/{values['pr_number']}/comments?per_page=100&page={page}",
            github_token,
        )
        if not isinstance(batch, list):
            raise RuntimeError("GitHub returned an invalid pull request comment list")
        comments.extend(batch)
        if len(batch) < 100:
            break
    existing = next(
        (comment for comment in comments if marker in str(comment.get("body") or "")),
        None,
    )
    if existing:
        comment = _github_request(
            "PATCH",
            f"repos/{repository}/issues/comments/{existing['id']}",
            github_token,
            {"body": body},
        )
    else:
        comment = _github_request(
            "POST",
            f"repos/{repository}/issues/{values['pr_number']}/comments",
            github_token,
            {"body": body},
        )
    return str(comment.get("html_url") or "") if isinstance(comment, dict) else ""


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--storage-account", required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--output", default="bugscouter-result.json")
    parser.add_argument("--timeout-minutes", type=int, default=90)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--target-url", default="")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    try:
        build_outcome = os.environ.get("BUILD_OUTCOME", "")
        if build_outcome and build_outcome != "success":
            raise RuntimeError(f"Bug Scouter build {build_outcome}")
        preparation_outcome = os.environ.get("PREPARATION_OUTCOME", "")
        if preparation_outcome and preparation_outcome != "success":
            raise RuntimeError(f"Bug Scouter context preparation {preparation_outcome}")
        login_outcome = os.environ.get("AZURE_LOGIN_OUTCOME", "")
        if login_outcome and login_outcome != "success":
            raise RuntimeError(f"Azure OIDC login {login_outcome}")
        response = invoke(args, request)
    except Exception as exc:
        response = {"state": "failed", "error": f"{type(exc).__name__}: {exc}"}
    Path(args.output).write_text(json.dumps(response, indent=2), encoding="utf-8")
    if args.publish:
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            raise RuntimeError("GITHUB_TOKEN is required to publish results")
        print(
            publish(request, response, github_token=token, target_url=args.target_url)
        )
    result = response.get("result") if isinstance(response, dict) else None
    if (
        response.get("state") != "completed"
        or not isinstance(result, dict)
        or result.get("status") != "ok"
    ):
        return 2
    try:
        bug_count = _bug_count(result)
    except ValueError:
        return 2
    return 1 if bug_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
