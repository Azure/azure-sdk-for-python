"""Validate an untrusted Bug Scouter build artifact for trusted invocation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

EXPECTED_REPOSITORY = "Azure/azure-sdk-for-python"
EXPECTED_WORKFLOW = "Bug Scouter Build"
OPT_IN_LABEL = "bug-scouter"
MAX_BUG_BASH_DOCUMENT_CHARS = 190_000
MAX_DIFF_BYTES = 160_000
MAX_GITHUB_JSON_BYTES = 2 * 1024 * 1024
MAX_GITHUB_PAGES = 10
MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
MAX_MANIFEST_BYTES = 16 * 1024
MAX_WHEEL_BYTES = 200 * 1024 * 1024
MAX_ARCHIVE_BYTES = MAX_WHEEL_BYTES + MAX_DOCUMENT_BYTES + MAX_MANIFEST_BYTES
WHEEL_PATTERN = re.compile(r"azure_ai_ml-[A-Za-z0-9_.+-]+-py3-none-any\.whl")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _github_json(path: str, token: str):
    request = urllib.request.Request(
        f"https://api.github.com/{path.lstrip('/')}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "bug-scouter-github-action",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read(MAX_GITHUB_JSON_BYTES + 1)
            if len(payload) > MAX_GITHUB_JSON_BYTES:
                raise ValueError(
                    "GitHub JSON response exceeds the maximum allowed size"
                )
            return json.loads(payload.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed with HTTP {exc.code}: {detail}"
        ) from exc


def _github_text(path: str, token: str, *, accept: str, max_bytes: int) -> str:
    request = urllib.request.Request(
        f"https://api.github.com/{path.lstrip('/')}",
        headers={
            "Accept": accept,
            "Authorization": f"Bearer {token}",
            "User-Agent": "bug-scouter-github-action",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                raise ValueError("pull request diff exceeds the maximum allowed size")
            return payload.decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed with HTTP {exc.code}: {detail}"
        ) from exc


def _github_pages(path: str, token: str) -> list[dict]:
    separator = "&" if "?" in path else "?"
    items = []
    for page in range(1, MAX_GITHUB_PAGES + 1):
        result = _github_json(f"{path}{separator}per_page=100&page={page}", token)
        if not isinstance(result, list) or not all(
            isinstance(item, dict) for item in result
        ):
            raise RuntimeError("GitHub returned an invalid paginated response")
        items.extend(result)
        if len(result) < 100:
            return items
    raise ValueError("pull request discussion exceeds the maximum allowed pages")


def _github_pull(repository: str, number: int, token: str) -> dict:
    result = _github_json(f"repos/{repository}/pulls/{number}", token)
    if not isinstance(result, dict):
        raise RuntimeError("GitHub returned an invalid pull request")
    return result


def _workflow_values(event: dict) -> dict:
    run = event.get("workflow_run")
    repository = event.get("repository")
    if not isinstance(run, dict) or not isinstance(repository, dict):
        raise ValueError("event must contain workflow_run and repository objects")
    if repository.get("full_name") != EXPECTED_REPOSITORY:
        raise ValueError(
            "workflow run repository is not the expected upstream repository"
        )
    if run.get("name") != EXPECTED_WORKFLOW or run.get("event") != "pull_request":
        raise ValueError("workflow run provenance is invalid")
    if run.get("status") != "completed":
        raise ValueError("build workflow is not complete")
    pull_requests = run.get("pull_requests")
    if not isinstance(pull_requests, list) or len(pull_requests) > 1:
        raise ValueError("workflow run has invalid pull request associations")
    head_sha = str(run.get("head_sha") or "").lower()
    if len(head_sha) != 40 or any(
        character not in "0123456789abcdef" for character in head_sha
    ):
        raise ValueError("workflow run head SHA is invalid")
    return {
        "repository": EXPECTED_REPOSITORY,
        "run_id": int(run["id"]),
        "conclusion": str(run.get("conclusion") or ""),
        "pr_number": int(pull_requests[0]["number"]) if pull_requests else None,
        "head_sha": head_sha,
        "head_repository": str(
            (run.get("head_repository") or {}).get("full_name") or ""
        ),
        "head_branch": str(run.get("head_branch") or ""),
    }


def _validate_live_pull(values: dict, pull_request: dict) -> dict:
    head = pull_request.get("head") or {}
    head_repository = head.get("repo") or {}
    if pull_request.get("state") != "open":
        raise ValueError("pull request is not open")
    if str(head.get("sha") or "").lower() != values["head_sha"]:
        raise ValueError("workflow run SHA is stale")
    if head_repository.get("full_name") != values["head_repository"]:
        raise ValueError("workflow run head repository does not match the pull request")
    base_repository = ((pull_request.get("base") or {}).get("repo") or {}).get(
        "full_name"
    )
    if base_repository != values["repository"]:
        raise ValueError("pull request base repository is invalid")
    labels = pull_request.get("labels")
    if not isinstance(labels, list) or OPT_IN_LABEL not in {
        str(label.get("name") or "") for label in labels if isinstance(label, dict)
    }:
        raise ValueError(f"pull request does not have the {OPT_IN_LABEL} label")
    base_sha = str((pull_request.get("base") or {}).get("sha") or "").lower()
    if len(base_sha) != 40 or any(
        character not in "0123456789abcdef" for character in base_sha
    ):
        raise ValueError("pull request base SHA is invalid")
    return {
        **values,
        "pr_number": int(pull_request["number"]),
        "pr_title": str(pull_request.get("title") or ""),
        "pr_body": str(pull_request.get("body") or ""),
        "base_sha": base_sha,
        "html_url": str(pull_request.get("html_url") or ""),
    }


def _discussion_entry(item: dict, *, kind: str) -> str | None:
    body = str(item.get("body") or "").strip()
    if "<!-- bug-scouter:" in body:
        return None
    author = str((item.get("user") or {}).get("login") or "unknown")
    timestamp = str(item.get("submitted_at") or item.get("created_at") or "unknown")
    details = [f"author={author}", f"time={timestamp}"]
    if kind == "review":
        details.append(f"state={str(item.get('state') or 'unknown')}")
    if kind == "inline review comment":
        details.append(f"path={str(item.get('path') or 'unknown')}")
        details.append(f"line={str(item.get('line') or 'unknown')}")
    return f"### {kind.title()} ({', '.join(details)})\n{body or '(no written body)'}"


def _discussion_section(title: str, items: list[dict], *, kind: str) -> str:
    entries = [
        entry
        for item in items
        if (entry := _discussion_entry(item, kind=kind)) is not None
    ]
    return f"## {title}\n" + ("\n\n".join(entries) if entries else "(none)")


def _build_bug_bash_document(request: dict, readme: str, token: str) -> str:
    repository = request["repository"]
    pr_number = request["pr_number"]
    issue_comments = _github_pages(
        f"repos/{repository}/issues/{pr_number}/comments", token
    )
    reviews = _github_pages(f"repos/{repository}/pulls/{pr_number}/reviews", token)
    review_comments = _github_pages(
        f"repos/{repository}/pulls/{pr_number}/comments", token
    )
    diff = _github_text(
        f"repos/{repository}/compare/{request['base_sha']}...{request['head_sha']}",
        token,
        accept="application/vnd.github.diff",
        max_bytes=MAX_DIFF_BYTES,
    )
    sections = [
        "# Bug Bash Instructions from Pull Request",
        (
            "Use the PR title, description, discussion, reviews, inline review "
            "comments, and exact code diff below as the bug-bash instructions. "
            "Use the package README only as supporting API documentation."
        ),
        f"## PR Title\n{request['pr_title'] or '(none)'}",
        f"## PR Description\n{request['pr_body'] or '(none)'}",
        _discussion_section("PR Conversation", issue_comments, kind="comment"),
        _discussion_section("Reviews", reviews, kind="review"),
        _discussion_section(
            "Inline Review Comments", review_comments, kind="inline review comment"
        ),
        (
            f"## Exact Code Diff ({request['base_sha']}...{request['head_sha']})\n"
            f"```diff\n{diff}\n```"
        ),
        f"## Package README (Supporting Context)\n{readme}",
    ]
    document = "\n\n".join(sections)
    if len(document) > MAX_BUG_BASH_DOCUMENT_CHARS:
        raise ValueError("pull request context exceeds the maximum allowed size")
    return document


def _resolve_pull(values: dict, token: str) -> dict:
    if values["pr_number"] is not None:
        return _github_pull(values["repository"], values["pr_number"], token)
    head_owner = values["head_repository"].split("/", 1)[0]
    if not head_owner or not values["head_branch"]:
        raise ValueError("workflow run cannot identify its pull request head")
    query = urllib.parse.urlencode(
        {
            "state": "open",
            "head": f"{head_owner}:{values['head_branch']}",
            "per_page": "10",
        }
    )
    candidates = _github_json(f"repos/{values['repository']}/pulls?{query}", token)
    if not isinstance(candidates, list):
        raise RuntimeError("GitHub returned an invalid pull request list")
    matches = [
        pull_request
        for pull_request in candidates
        if str((pull_request.get("head") or {}).get("sha") or "").lower()
        == values["head_sha"]
    ]
    if len(matches) != 1:
        raise ValueError(
            "workflow run does not resolve to exactly one open pull request"
        )
    return matches[0]


def _regular_files(artifact_directory: Path) -> list[Path]:
    files = []
    for path in artifact_directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"artifact contains a symbolic link: {path.name}")
        if path.is_file():
            files.append(path)
    return files


def _download_artifact(artifact_directory: Path, values: dict, token: str) -> None:
    artifacts = _github_json(
        f"repos/{values['repository']}/actions/runs/{values['run_id']}/artifacts?per_page=100",
        token,
    )
    if not isinstance(artifacts, dict) or not isinstance(
        artifacts.get("artifacts"), list
    ):
        raise RuntimeError("GitHub returned an invalid artifact list")
    expected_name = f"bug-scouter-input-{values['head_sha']}"
    matches = [
        artifact
        for artifact in artifacts["artifacts"]
        if artifact.get("name") == expected_name
    ]
    if len(matches) != 1 or matches[0].get("expired"):
        raise ValueError("workflow run must contain one unexpired exact-SHA artifact")
    if int(matches[0].get("size_in_bytes") or 0) > MAX_ARCHIVE_BYTES:
        raise ValueError("artifact archive exceeds the maximum allowed size")

    request = urllib.request.Request(
        str(matches[0]["archive_download_url"]),
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "bug-scouter-github-action",
        },
    )
    artifact_directory.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryFile() as archive_file:
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            response = opener.open(request, timeout=120)
        except urllib.error.HTTPError as exc:
            if exc.code not in {301, 302, 303, 307, 308} or not exc.headers.get(
                "Location"
            ):
                raise
            redirected_request = urllib.request.Request(
                exc.headers["Location"],
                headers={"User-Agent": "bug-scouter-github-action"},
            )
            response = urllib.request.urlopen(redirected_request, timeout=120)
        with response:
            downloaded = 0
            while chunk := response.read(1024 * 1024):
                downloaded += len(chunk)
                if downloaded > MAX_ARCHIVE_BYTES:
                    raise ValueError(
                        "downloaded artifact exceeds the maximum allowed size"
                    )
                archive_file.write(chunk)
        archive_file.seek(0)
        with zipfile.ZipFile(archive_file) as archive:
            members = [member for member in archive.infolist() if not member.is_dir()]
            names = {member.filename for member in members}
            wheel_names = [name for name in names if WHEEL_PATTERN.fullmatch(name)]
            if len(wheel_names) != 1 or names != {
                "manifest.json",
                "README.md",
                wheel_names[0],
            }:
                raise ValueError(
                    "artifact archive contains missing, nested, or unexpected files"
                )
            size_limits = {
                "manifest.json": MAX_MANIFEST_BYTES,
                "README.md": MAX_DOCUMENT_BYTES,
                wheel_names[0]: MAX_WHEEL_BYTES,
            }
            for member in members:
                if member.file_size > size_limits[member.filename]:
                    raise ValueError(
                        f"{member.filename} exceeds the maximum allowed size"
                    )
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("artifact archive contains a symbolic link")
                destination = artifact_directory / member.filename
                with archive.open(member) as source, destination.open("wb") as output:
                    copied = 0
                    while chunk := source.read(1024 * 1024):
                        copied += len(chunk)
                        if copied > size_limits[member.filename]:
                            raise ValueError(
                                f"{member.filename} exceeds the maximum allowed size"
                            )
                        output.write(chunk)


def _validate_artifact(artifact_directory: Path, values: dict) -> tuple[Path, Path]:
    artifact_directory = artifact_directory.resolve()
    files = _regular_files(artifact_directory)
    relative_names = {path.relative_to(artifact_directory).as_posix() for path in files}
    wheel_names = [name for name in relative_names if WHEEL_PATTERN.fullmatch(name)]
    if len(wheel_names) != 1:
        raise ValueError("artifact must contain exactly one azure-ai-ml wheel")
    expected_names = {"manifest.json", "README.md", wheel_names[0]}
    if relative_names != expected_names:
        raise ValueError("artifact contains missing, nested, or unexpected files")

    manifest_path = artifact_directory / "manifest.json"
    document_path = artifact_directory / "README.md"
    wheel_path = artifact_directory / wheel_names[0]
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("manifest exceeds the maximum allowed size")
    if wheel_path.stat().st_size > MAX_WHEEL_BYTES:
        raise ValueError("wheel exceeds the maximum allowed size")
    if document_path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("document exceeds the maximum allowed size")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_manifest = {
        "schema_version": 1,
        "repository": values["repository"],
        "run_id": values["run_id"],
        "pr_number": values["pr_number"],
        "head_sha": values["head_sha"],
        "wheel_filename": wheel_path.name,
        "wheel_sha256": _sha256(wheel_path),
        "document_sha256": _sha256(document_path),
    }
    if manifest != expected_manifest:
        raise ValueError("artifact manifest does not match the trusted workflow run")
    return wheel_path, document_path


def resolve(event: dict, token: str) -> dict:
    values = _workflow_values(event)
    pull_request = _resolve_pull(values, token)
    return _validate_live_pull(values, pull_request)


def prepare(event: dict, artifact_directory: Path, token: str) -> dict:
    request = resolve(event, token)
    if request["conclusion"] != "success":
        raise ValueError("build workflow did not complete successfully")
    _download_artifact(artifact_directory, request, token)
    wheel_path, document_path = _validate_artifact(artifact_directory, request)
    bug_bash_document = _build_bug_bash_document(
        request, document_path.read_text(encoding="utf-8"), token
    )
    final_request = _validate_live_pull(
        request, _github_pull(request["repository"], request["pr_number"], token)
    )
    if final_request["base_sha"] != request["base_sha"]:
        raise ValueError("pull request base SHA changed while collecting context")
    return {
        **final_request,
        "wheel": str(wheel_path),
        "document": str(document_path),
        "bug_bash_document": bug_bash_document,
    }


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--artifact")
    parser.add_argument("--output", required=True)
    parser.add_argument("--resolve-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required to validate the pull request")
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    if args.resolve_only:
        request = resolve(event, token)
    elif args.artifact:
        request = prepare(event, Path(args.artifact), token)
    else:
        raise ValueError("--artifact is required unless --resolve-only is used")
    Path(args.output).write_text(json.dumps(request, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
