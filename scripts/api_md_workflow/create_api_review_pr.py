#!/usr/bin/env python3

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_OWNER = "Azure"
REPO_NAME = "azure-sdk-for-python"
REPO_SLUG = f"{REPO_OWNER}/{REPO_NAME}"
REMOTE = "origin"
MAIN_REF = f"{REMOTE}/main"
SYNC_METADATA_MARKER = "api-md-review-sync"
SYNC_METADATA_WARNING = "DO NOT MODIFY THESE CONTENTS!"
GITHUB_API_TIMEOUT_SECONDS = 30
AZSDK_INSTALL_SCRIPT = REPO_ROOT / "eng" / "common" / "mcp" / "azure-sdk-mcp.ps1"
ARCHITECTS_PATH = REPO_ROOT / ".github" / "ARCHITECTS"


class GitHubApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


@dataclass
class CommandResult:
    status: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class ApiResult:
    api_md: bytes
    metadata: bytes | None
    version: str


@dataclass
class BranchState:
    has_api_md: bool
    has_metadata: bool
    api_md_sha256: str | None


@dataclass
class BranchSelection:
    branch_name: str
    reused: bool
    remote_ref: str | None


@dataclass
class ArchitectReviewers:
    users: list[str]
    teams: list[str]


GitRunner = Callable[[list[str], bool], CommandResult]
_git_runner: GitRunner | None = None
_github_api: "GitHubApi | None" = None


def set_command_runner_for_test(git_runner: GitRunner | None) -> None:
    global _git_runner
    _git_runner = git_runner


def set_github_api_for_test(api: "GitHubApi | None") -> None:
    global _github_api
    _github_api = api


def log_info(message: str) -> None:
    print(message)


def log_warning(message: str) -> None:
    print(message, file=sys.stderr)


def log_error(message: str) -> None:
    print(message, file=sys.stderr)


def run(
    args: list[str],
    *,
    cwd: Path = REPO_ROOT,
    check: bool = True,
    capture: bool = False,
    shell: bool = False,
) -> CommandResult:
    printable = " ".join(args)
    log_info(f"$ {printable}")
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=capture,
        text=True,
        shell=shell,
    )
    result = CommandResult(
        completed.returncode, completed.stdout or "", completed.stderr or ""
    )
    if check and result.status != 0:
        details = "\n".join(
            part for part in [result.stderr.strip(), result.stdout.strip()] if part
        )
        raise RuntimeError(
            f"Command failed ({result.status}): {printable}"
            + (f"\n{details}" if details else "")
        )
    return result


def git(args: list[str], *, check: bool = True) -> CommandResult:
    if _git_runner:
        result = _git_runner(args, check)
        if check and result.status != 0:
            raise RuntimeError(
                f"Command failed ({result.status}): {' '.join(['git', *args])}"
            )
        return result
    return run(["git", *args], check=check, capture=True)


def git_out(args: list[str]) -> str:
    return git(args).stdout.strip()


def resolve_github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token

    gh = shutil.which("gh")
    if not gh:
        return None

    try:
        return subprocess.run(
            [gh, "auth", "token"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.SubprocessError:
        return None


def normalize_pull_request(pr: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(pr, dict):
        return None

    owner_login = None
    author_login = None
    if isinstance(pr.get("headRepositoryOwner"), dict):
        owner_login = pr["headRepositoryOwner"].get("login")
    elif isinstance(pr.get("head"), dict):
        repo = (
            pr["head"].get("repo") if isinstance(pr["head"].get("repo"), dict) else {}
        )
        owner = repo.get("owner") if isinstance(repo.get("owner"), dict) else {}
        owner_login = owner.get("login")
    if isinstance(pr.get("author"), dict):
        author_login = pr["author"].get("login")
    elif isinstance(pr.get("user"), dict):
        author_login = pr["user"].get("login")

    return {
        "number": pr.get("number"),
        "url": pr.get("url") or pr.get("html_url"),
        "state": pr.get("state"),
        "updatedAt": pr.get("updatedAt") or pr.get("updated_at"),
        "body": pr.get("body"),
        "headRefName": pr.get("headRefName") or (pr.get("head") or {}).get("ref"),
        "headRepositoryOwner": {"login": owner_login},
        "authorLogin": author_login,
    }


class GitHubApi:
    def __init__(self, token: str | None):
        self.token = token

    def _request(
        self, method: str, url: str, payload: dict[str, Any] | None = None
    ) -> Any:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "azure-sdk-python-api-md-workflow",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if data is not None:
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=GITHUB_API_TIMEOUT_SECONDS) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else None
        except HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            raise GitHubApiError(error.code, details or str(error)) from error
        except TimeoutError as error:
            raise GitHubApiError(1, f"GitHub API request timed out: {error}") from error
        except URLError as error:
            raise GitHubApiError(1, str(error)) from error

    def _rest_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        url = f"https://api.github.com{path}"
        if query:
            url = f"{url}?{urlencode(query)}"
        return url

    def list_pull_requests_by_head(self, head: str, limit: int) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            self._rest_url(
                f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
                {"head": head, "state": "open", "per_page": limit},
            ),
        )
        return [
            pr for pr in (normalize_pull_request(item) for item in data or []) if pr
        ]

    def search_pull_requests(self, query: str, limit: int) -> list[dict[str, Any]]:
        graphql_query = """
query($query: String!, $first: Int!) {
  search(query: $query, type: ISSUE, first: $first) {
    nodes {
      ... on PullRequest {
        number
        url
        state
        updatedAt
        body
        headRefName
        headRepositoryOwner { login }
                author { login }
      }
    }
  }
}
"""
        data = self._request(
            "POST",
            "https://api.github.com/graphql",
            {"query": graphql_query, "variables": {"query": query, "first": limit}},
        )
        nodes = ((data or {}).get("data") or {}).get("search", {}).get("nodes", [])
        return [pr for pr in (normalize_pull_request(item) for item in nodes) if pr]

    def list_pull_requests_by_branches(
        self, base: str, head: str, limit: int
    ) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            self._rest_url(
                f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls",
                {
                    "base": base,
                    "head": f"{REPO_OWNER}:{head}",
                    "state": "open",
                    "per_page": limit,
                },
            ),
        )
        return [
            pr for pr in (normalize_pull_request(item) for item in data or []) if pr
        ]

    def update_pull_request_body(self, number: int, body: str) -> None:
        self._request(
            "PATCH",
            self._rest_url(f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{number}"),
            {"body": body},
        )

    def create_draft_pull_request(
        self, base: str, head: str, title: str, body: str
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            self._rest_url(f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls"),
            {"base": base, "head": head, "title": title, "body": body, "draft": True},
        )

    def request_reviewers(
        self,
        pr_number: int,
        reviewers: list[str],
        team_reviewers: list[str] | None = None,
    ) -> None:
        url = self._rest_url(
            f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/requested_reviewers"
        )
        payload: dict[str, Any] = {"reviewers": reviewers}
        if team_reviewers:
            payload["team_reviewers"] = team_reviewers
        log_info(
            "API review architect diagnostics: requesting PR reviewers at "
            f"{url}: reviewers={reviewers}, team_reviewers={team_reviewers or []}"
        )
        response = self._request(
            "POST",
            url,
            payload,
        )
        requested_reviewers = []
        requested_teams = []
        if isinstance(response, dict):
            requested_reviewers = [
                reviewer.get("login")
                for reviewer in response.get("requested_reviewers", [])
                if isinstance(reviewer, dict) and reviewer.get("login")
            ]
            requested_teams = [
                team.get("slug")
                for team in response.get("requested_teams", [])
                if isinstance(team, dict) and team.get("slug")
            ]
        log_info(
            "API review architect diagnostics: GitHub response "
            f"requested_reviewers={requested_reviewers}, requested_teams={requested_teams}"
        )


def get_github_api() -> GitHubApi:
    global _github_api
    if _github_api is None:
        _github_api = GitHubApi(resolve_github_token())
    return _github_api


def ensure_clean_worktree() -> None:
    status = git_out(["status", "--porcelain"])
    if status:
        raise RuntimeError(
            f"ERROR: working tree is not clean. Commit or stash changes before running.\n{status}"
        )


def current_branch() -> str:
    return git_out(["rev-parse", "--abbrev-ref", "HEAD"])


def tag_exists(tag: str) -> bool:
    return (
        git(
            ["rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"], check=False
        ).status
        == 0
    )


def validate_base_tag(package_name: str, base_tag: str) -> str:
    prefix = f"{package_name}_"
    if not base_tag.startswith(prefix):
        raise RuntimeError(
            f"ERROR: --base tag '{base_tag}' must start with '{prefix}'."
        )

    version = base_tag[len(prefix) :]
    if not version:
        raise RuntimeError(
            f"ERROR: --base tag '{base_tag}' is missing the version suffix."
        )

    if not tag_exists(base_tag):
        raise RuntimeError(
            f"ERROR: tag '{base_tag}' does not exist in this repository."
        )

    return version


def is_explicit_package_tag(target: str, package_name: str | None = None) -> bool:
    if ":" in target:
        return False
    if package_name:
        return target.startswith(f"{package_name}_")
    return "_" in target


def resolve_target_tag(target: str, package_name: str | None = None) -> str | None:
    if not is_explicit_package_tag(target, package_name):
        return None
    if tag_exists(target):
        return target
    git(["fetch", REMOTE, "tag", target], check=False)
    return target if tag_exists(target) else None


def try_remote_branch_ref(branch: str) -> str | None:
    remote_ref = f"refs/remotes/{REMOTE}/{branch}"
    result = git(["fetch", REMOTE, f"{branch}:{remote_ref}"], check=False)
    return f"{REMOTE}/{branch}" if result.status == 0 else None


def fork_url(owner: str) -> str:
    return f"https://github.com/{owner}/{REPO_NAME}.git"


def try_fork_branch_ref(owner: str, branch: str) -> str | None:
    result = git(["fetch", fork_url(owner), branch], check=False)
    return "FETCH_HEAD" if result.status == 0 else None


def resolve_target_ref(target: str, package_name: str | None = None) -> str:
    if ":" not in target:
        target_tag = resolve_target_tag(target, package_name)
        if target_tag:
            return target_tag

        branch_ref = try_remote_branch_ref(target)
        if branch_ref:
            return branch_ref

        raise RuntimeError(
            f"ERROR: --target '{target}' is neither a branch on {REMOTE} nor a tag in this repository."
        )

    owner, branch = target.split(":", 1)
    if not owner or not branch:
        raise RuntimeError(
            f"ERROR: invalid --target '{target}'. Expected 'tag', 'branch', or 'owner:branch'."
        )

    branch_ref = try_fork_branch_ref(owner, branch)
    if not branch_ref:
        raise RuntimeError(
            f"ERROR: branch '{branch}' does not exist in fork '{owner}'."
        )
    return branch_ref


def walk_files(start_dir: Path):
    for root, _, files in os.walk(start_dir):
        for file_name in files:
            yield Path(root) / file_name


def find_package_dir(package_name: str) -> Path:
    sdk_dir = REPO_ROOT / "sdk"
    matches: list[Path] = []
    for service_dir in sdk_dir.iterdir():
        if not service_dir.is_dir():
            continue
        candidate = service_dir / package_name
        if not candidate.is_dir():
            continue
        if (candidate / "pyproject.toml").exists() or (candidate / "setup.py").exists():
            matches.append(candidate)

    if not matches:
        raise RuntimeError(f"ERROR: package '{package_name}' not found under sdk/*/")
    if len(matches) > 1:
        raise RuntimeError(
            f"ERROR: multiple matches for '{package_name}': {', '.join(str(match) for match in matches)}"
        )
    return matches[0]


def read_version(package_dir: Path) -> str:
    version_regex = re.compile(
        r"^\s*VERSION\s*[:=]\s*[\"']([^\"']+)[\"']", re.MULTILINE
    )
    candidates: list[Path] = []
    for file_path in walk_files(package_dir):
        if file_path.name not in {"_version.py", "version.py"}:
            continue
        relative = file_path.relative_to(package_dir).as_posix()
        if "_generated" in relative or "generated_" in relative:
            continue
        candidates.append(file_path)

    for candidate in candidates:
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        match = version_regex.search(text)
        if match:
            return match.group(1)

    raise RuntimeError(f"ERROR: could not find a version string in {package_dir}")


def generate_api_for_package(
    package_name: str, runtime_executable: str | None, ref_label: str | None = None
) -> None:
    if ref_label:
        log_info(f"--- Generating api.md on {ref_label} ---")

    package_dir = find_package_dir(package_name)
    if runtime_executable or os.environ.get("RUNTIME_EXECUTABLE"):
        python_executable = runtime_executable or os.environ["RUNTIME_EXECUTABLE"]
        run(
            [
                python_executable,
                "-m",
                "azpysdk.main",
                "apistub",
                "--dest-dir",
                str(package_dir),
                package_name,
            ],
            check=True,
        )
        return

    run(
        [
            "azpysdk",
            "apistub",
            "--dest-dir",
            str(package_dir),
            package_name,
        ],
        check=True,
        shell=sys.platform == "win32",
    )


def package_rel_dir(package_dir: Path) -> str:
    return package_dir.relative_to(REPO_ROOT).as_posix()


def normalize_package_dir(package_dir: Path | str) -> str:
    path_value = Path(package_dir)
    if path_value.is_absolute():
        return path_value.relative_to(REPO_ROOT).as_posix()
    return str(package_dir).replace("\\", "/")


def api_md_path(package_dir: Path) -> Path:
    return package_dir / "api.md"


def api_md_rel(package_dir: Path) -> str:
    return f"{package_rel_dir(package_dir)}/api.md"


def metadata_path(package_dir: Path) -> Path:
    return package_dir / "api.metadata.yml"


def metadata_rel(package_dir: Path) -> str:
    return f"{package_rel_dir(package_dir)}/api.metadata.yml"


def api_review_branch_name(kind: str, package_name: str, version: str) -> str:
    return f"apireview/{kind}_{package_name}_{version}"


def parse_simple_yaml(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^(\w+)\s*:\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def package_version_major_minor(package_version: str) -> str:
    match = re.match(r"^(\d+)(?:\.(\d+))?", package_version.strip())
    if not match:
        raise RuntimeError(
            f"ERROR: could not derive major/minor version from package version '{package_version}'."
        )
    major = match.group(1)
    minor = match.group(2) or "0"
    return f"{major}.{minor}"


def parse_package_work_item_id(output: str) -> int | None:
    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict):
            value = parsed.get("work_item_id") or parsed.get("workItemId")
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
    except json.JSONDecodeError:
        pass

    match = re.search(r"Work Item ID:\s*(\d+)", output)
    return int(match.group(1)) if match else None


def find_azsdk_executable() -> str | None:
    azsdk_from_path = shutil.which("azsdk")
    if azsdk_from_path:
        return azsdk_from_path

    for install_dir in [Path.home() / "bin", Path.home() / ".azure-sdk-mcp"]:
        for executable_name in ["azsdk.exe", "azsdk"]:
            candidate = install_dir / executable_name
            if candidate.is_file():
                return str(candidate)

    return None


def combined_command_output(result: CommandResult) -> str:
    return "\n".join(
        part.strip() for part in [result.stdout, result.stderr] if part.strip()
    )


def resolve_azsdk_executable() -> str:
    azsdk_executable = find_azsdk_executable()
    if azsdk_executable:
        return azsdk_executable

    raise RuntimeError(
        "ERROR: azsdk CLI not found. Install it by running "
        f"'pwsh {AZSDK_INSTALL_SCRIPT}', or run with '-UpdatePathInProfile' to add it to PATH."
    )


def ensure_azsdk_find_work_item_available() -> None:
    azsdk_executable = resolve_azsdk_executable()
    result = run(
        [azsdk_executable, "package", "find-work-item", "--help"],
        check=False,
        capture=True,
    )
    if result.status == 0:
        return

    details = combined_command_output(result)
    raise RuntimeError(
        "ERROR: azsdk CLI is installed, but the 'package find-work-item' command is unavailable. "
        f"Update it by running 'pwsh {AZSDK_INSTALL_SCRIPT}'."
        + (f"\n{details}" if details else "")
    )


def package_work_item_id(package_name: str, package_version: str) -> int | str:
    package_version_major_minor_value = package_version_major_minor(package_version)
    result = run(
        [
            resolve_azsdk_executable(),
            "package",
            "find-work-item",
            "--package-name",
            package_name,
            "--package-version",
            package_version_major_minor_value,
            "--language",
            "Python",
        ],
        check=False,
        capture=True,
    )
    output = combined_command_output(result)

    if result.status != 0:
        log_warning(
            f"WARNING: failed to resolve package work item ID for {package_name} {package_version_major_minor_value}. "
            "PR body sync metadata will set packageWorkItemId to ERROR."
            + (f"\n{output}" if output else "")
        )
        return "ERROR"

    work_item_id = parse_package_work_item_id(result.stdout)
    if work_item_id is None:
        log_warning(
            f"WARNING: azsdk package find-work-item completed for {package_name} {package_version_major_minor_value} "
            "but did not return a work item ID. PR body sync metadata will set packageWorkItemId to NONE."
            + (f"\n{output}" if output else "")
        )
        return "NONE"
    return work_item_id


def metadata_sha_or_none(metadata_bytes: bytes | None) -> str | None:
    if not metadata_bytes:
        return None
    metadata = parse_simple_yaml(metadata_bytes.decode("utf-8"))
    return metadata.get("apiMdSha256")


def _codeowners_segment_match(
    path_segments: list[str], pattern_segments: list[str]
) -> bool:
    memo: dict[tuple[int, int], bool] = {}

    def match(path_index: int, pattern_index: int) -> bool:
        key = (path_index, pattern_index)
        if key in memo:
            return memo[key]

        # Base case: pattern exhausted
        if pattern_index >= len(pattern_segments):
            result = path_index >= len(path_segments)
        # Pattern segment is **
        elif pattern_segments[pattern_index] == "**":
            next_pattern_index = pattern_index
            while (
                next_pattern_index + 1 < len(pattern_segments)
                and pattern_segments[next_pattern_index + 1] == "**"
            ):
                next_pattern_index += 1
            if next_pattern_index + 1 >= len(pattern_segments):
                result = True
            else:
                result = any(
                    match(next_path_index, next_pattern_index + 1)
                    for next_path_index in range(path_index, len(path_segments) + 1)
                )
        # Path exhausted but pattern remains
        elif path_index >= len(path_segments):
            result = False
        # Segment doesn't match
        elif not fnmatch.fnmatchcase(
            path_segments[path_index], pattern_segments[pattern_index]
        ):
            result = False
        # Recurse to next segments
        else:
            result = match(path_index + 1, pattern_index + 1)

        memo[key] = result
        return result

    return match(0, 0)


def codeowners_style_pattern_matches(pattern: str, path: str) -> bool:
    normalized_path = path.replace("\\", "/").strip("/")
    normalized_pattern = pattern.replace("\\", "/").strip()
    if not normalized_pattern or normalized_pattern.startswith("!"):
        return False

    is_anchored = normalized_pattern.startswith("/")
    if is_anchored:
        normalized_pattern = normalized_pattern[1:]

    if normalized_pattern.endswith("/"):
        normalized_pattern = normalized_pattern.rstrip("/")
        normalized_pattern = f"{normalized_pattern}/**" if normalized_pattern else "**"

    if not normalized_pattern:
        return False

    path_segments = [segment for segment in normalized_path.split("/") if segment]

    if "/" not in normalized_pattern:
        return any(
            fnmatch.fnmatchcase(segment, normalized_pattern)
            for segment in path_segments
        )

    pattern_segments = [segment for segment in normalized_pattern.split("/") if segment]

    if is_anchored:
        return _codeowners_segment_match(path_segments, pattern_segments)

    for start_index in range(0, len(path_segments) + 1):
        if _codeowners_segment_match(path_segments[start_index:], pattern_segments):
            return True
    return False


def github_owner_from_owner(owner: str) -> str | None:
    if not owner.startswith("@"):
        return None
    github_owner = owner[1:].strip()
    return github_owner or None


def architect_reviewers_from_owners(owners: list[str]) -> ArchitectReviewers:
    users: list[str] = []
    teams: list[str] = []
    for owner in owners:
        if "/" in owner:
            _, team_slug = owner.split("/", 1)
            if team_slug:
                teams.append(team_slug)
            continue
        users.append(owner)
    return ArchitectReviewers(users=users, teams=teams)


def architects_for_package(
    package_dir: Path | str, architects_path: Path | None = None
) -> list[str]:
    architects_path = architects_path or ARCHITECTS_PATH
    package_relative = normalize_package_dir(package_dir)
    log_info(
        "API review architect diagnostics: "
        f"package_dir={package_dir}, normalized={package_relative}, architects_path={architects_path}"
    )
    if not architects_path.exists():
        log_warning(
            f"API review architect diagnostics: ARCHITECTS file does not exist: {architects_path}"
        )
        return []

    matching_architects: list[str] = []
    for line in architects_path.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        parts = stripped_line.split()
        if len(parts) < 2:
            continue
        pattern = parts[0]
        if codeowners_style_pattern_matches(pattern, package_relative):
            matching_architects = [
                owner
                for candidate in parts[1:]
                if (owner := github_owner_from_owner(candidate))
            ]
            log_info(
                "API review architect diagnostics: "
                f"matched ARCHITECTS pattern={pattern!r}, owners={parts[1:]}, resolved={matching_architects}"
            )
    log_info(
        f"API review architect diagnostics: resolved architects={matching_architects}"
    )
    return matching_architects


def branch_remote_ref(branch: str) -> str:
    return f"{REMOTE}/{branch}"


def list_remote_branches_with_prefix(prefix: str) -> list[str]:
    result = git(["ls-remote", "--heads", REMOTE, f"refs/heads/{prefix}*"], check=False)
    if result.status != 0 or not result.stdout.strip():
        return []

    branches = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) < 2 or not parts[1].startswith("refs/heads/"):
            continue
        branch = parts[1][len("refs/heads/") :]
        if branch == prefix or branch.startswith(f"{prefix}_"):
            branches.append(branch)
    return branches


def fetch_remote_branch(branch: str) -> str:
    git(["fetch", REMOTE, branch])
    return branch_remote_ref(branch)


def read_ref_file_bytes(ref: str, relative_path: str) -> bytes | None:
    result = git(["show", f"{ref}:{relative_path}"], check=False)
    if result.status != 0:
        return None
    return result.stdout.encode("utf-8")


def desired_branch_state(result: ApiResult | None) -> BranchState:
    if result is None:
        return BranchState(False, False, None)
    return BranchState(
        True, bool(result.metadata), metadata_sha_or_none(result.metadata)
    )


def api_results_have_api_diff(base_result: ApiResult, target_result: ApiResult) -> bool:
    return base_result.api_md != target_result.api_md


def branch_state_matches_desired(actual: BranchState, desired: BranchState) -> bool:
    return actual == desired


def read_branch_state(ref: str, api_relative: str, meta_relative: str) -> BranchState:
    metadata_bytes = read_ref_file_bytes(ref, meta_relative)
    api_md_bytes = read_ref_file_bytes(ref, api_relative)
    return BranchState(
        bool(api_md_bytes), bool(metadata_bytes), metadata_sha_or_none(metadata_bytes)
    )


def branch_suffix_from_index(index: int) -> str:
    value = index
    suffix = ""
    while True:
        suffix = chr(97 + (value % 26)) + suffix
        value = value // 26 - 1
        if value < 0:
            return suffix


def next_available_branch_name(
    preferred_branch: str, existing_branches: set[str]
) -> str:
    if preferred_branch not in existing_branches:
        return preferred_branch

    index = 0
    while f"{preferred_branch}_{branch_suffix_from_index(index)}" in existing_branches:
        index += 1
    return f"{preferred_branch}_{branch_suffix_from_index(index)}"


def is_ancestor_ref(ancestor_ref: str, branch_ref: str) -> bool:
    return (
        git(
            ["merge-base", "--is-ancestor", ancestor_ref, branch_ref], check=False
        ).status
        == 0
    )


def resolve_branch_selection(
    *,
    preferred_branch: str,
    desired_state: BranchState,
    api_relative: str,
    meta_relative: str,
    required_ancestor_ref: str | None = None,
) -> BranchSelection:
    existing_branches = set(list_remote_branches_with_prefix(preferred_branch))
    ordered_candidates = sorted(
        existing_branches, key=lambda branch: (branch != preferred_branch, branch)
    )

    for candidate_branch in ordered_candidates:
        remote_ref = fetch_remote_branch(candidate_branch)
        actual_state = read_branch_state(remote_ref, api_relative, meta_relative)
        if not branch_state_matches_desired(actual_state, desired_state):
            continue
        if required_ancestor_ref and not is_ancestor_ref(
            required_ancestor_ref, remote_ref
        ):
            continue
        return BranchSelection(candidate_branch, True, remote_ref)

    return BranchSelection(
        next_available_branch_name(preferred_branch, existing_branches), False, None
    )


def ensure_branch_state_has_metadata_sha(branch_label: str, state: BranchState) -> None:
    if state.has_api_md and not state.api_md_sha256:
        raise RuntimeError(
            f"ERROR: {branch_label} is missing apiMdSha256 in api.metadata.yml."
        )


def select_best_pr(prs: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        pr
        for pr in prs
        if pr.get("number") is not None
        and pr.get("url")
        and pr.get("state")
        and pr.get("updatedAt")
    ]
    if not candidates:
        return None
    open_prs = [pr for pr in candidates if str(pr.get("state", "")).lower() == "open"]
    pool = open_prs or candidates
    return sorted(pool, key=lambda pr: str(pr.get("updatedAt") or ""), reverse=True)[0]


def branch_reference_parts(head_selector: str) -> dict[str, str]:
    if head_selector == MAIN_REF:
        return {"owner": REPO_OWNER, "branch": "main", "display": head_selector}
    if ":" in head_selector:
        owner, branch = head_selector.split(":", 1)
        return {"owner": owner, "branch": branch, "display": head_selector}
    return {"owner": REPO_OWNER, "branch": head_selector, "display": head_selector}


def target_branch_exists(head_selector: str) -> bool:
    parts = branch_reference_parts(head_selector)
    if parts["owner"] == REPO_OWNER:
        return bool(try_remote_branch_ref(parts["branch"]))
    return bool(try_fork_branch_ref(parts["owner"], parts["branch"]))


def sync_working_branch_info(
    head_selector: str | None, package_name: str | None = None
) -> dict[str, str] | None:
    if not head_selector:
        return None
    if resolve_target_tag(head_selector, package_name):
        return None
    if target_branch_exists(head_selector):
        parts = branch_reference_parts(head_selector)
        return {"owner": parts["owner"], "branch": parts["branch"]}
    return None


def build_sync_metadata_object(
    *,
    package_name: str,
    package_dir: Path | str,
    base_branch: str,
    review_branch: str,
    head_selector: str,
    package_work_item_id_value: int | str | None = None,
) -> dict[str, Any] | None:
    working_branch = sync_working_branch_info(head_selector, package_name)
    if not working_branch:
        return None

    metadata: dict[str, Any] = {
        "schemaVersion": 1,
        "repository": REPO_SLUG,
        "packageName": package_name,
        "packageDir": normalize_package_dir(package_dir),
        "baseBranch": base_branch,
        "reviewBranch": review_branch,
        "workingOwner": working_branch["owner"],
        "workingBranch": working_branch["branch"],
    }
    working_pr = find_open_pr_for_head(head_selector)
    metadata["workingPrNumber"] = (
        working_pr.get("number")
        if working_pr and isinstance(working_pr.get("number"), int)
        else None
    )
    if package_work_item_id_value is not None:
        metadata["packageWorkItemId"] = package_work_item_id_value
    return metadata


def build_sync_metadata_block(metadata: dict[str, Any] | None) -> str | None:
    if not metadata:
        return None
    return "\n".join(
        [
            f"<!-- {SYNC_METADATA_MARKER}",
            SYNC_METADATA_WARNING,
            json.dumps(metadata, indent=2),
            "-->",
        ]
    )


def replace_sync_metadata_block(body: str | None, metadata_block: str | None) -> str:
    cleaned_body = re.sub(
        rf"<!--\s*{SYNC_METADATA_MARKER}[\s\S]*?-->\s*", "", str(body or "")
    ).rstrip()
    if not metadata_block:
        return cleaned_body
    return f"{cleaned_body}\n\n{metadata_block}"


def build_review_pr_body(
    *,
    package_name: str,
    target_version: str,
    base_version: str,
    working_reference: dict[str, str],
    baseline_ref: str,
    sync_metadata_block: str | None,
) -> str:
    lines = [
        f"Automated API review PR for {package_name}.",
        "",
        f"- **{working_reference['label']}:** {working_reference['markdown']} (version {target_version})",
        f"- **Baseline:** {baseline_ref} (version {base_version})",
    ]
    if working_reference["label"] == "Target tag":
        lines.extend(
            [
                "",
                "> [!WARNING]",
                "> Static tag-to-tag review; this PR cannot be automatically updated from a working branch.",
            ]
        )
    lines.extend(["", "Generated by scripts/api_md_workflow/create_api_review_pr.py."])
    return replace_sync_metadata_block("\n".join(lines), sync_metadata_block)


def update_pr_body(pr_number: int, body: str) -> None:
    get_github_api().update_pull_request_body(pr_number, body)


def ensure_pr_body_sync_metadata(
    pr: dict[str, Any] | None, metadata_block: str | None
) -> None:
    if not metadata_block or not pr or not isinstance(pr.get("number"), int):
        return
    desired_body = replace_sync_metadata_block(pr.get("body") or "", metadata_block)
    if desired_body == (pr.get("body") or ""):
        return
    try:
        update_pr_body(pr["number"], desired_body)
        log_info(f"Updated API review sync metadata on PR #{pr['number']}.")
    except Exception as error:  # pylint: disable=broad-except
        details = str(error)
        log_warning(
            f"WARNING: failed to update API review sync metadata on PR #{pr['number']}."
            + (f"\n  {details}" if details else "")
        )


def find_open_pr_for_head(head_selector: str) -> dict[str, Any] | None:
    parts = branch_reference_parts(head_selector)
    selector = f"{parts['owner']}:{parts['branch']}"
    all_prs: list[dict[str, Any]] = []
    github = get_github_api()

    try:
        all_prs.extend(github.list_pull_requests_by_head(selector, 50))
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        all_prs.extend(
            github.search_pull_requests(
                f"repo:{REPO_SLUG} is:pr is:open head:{parts['branch']}", 50
            )
        )
    except Exception:  # pylint: disable=broad-except
        pass

    deduped: dict[int, dict[str, Any]] = {}
    for pr in all_prs:
        if (
            pr.get("number") is not None
            and pr.get("headRefName") == parts["branch"]
            and (pr.get("headRepositoryOwner") or {}).get("login") == parts["owner"]
        ):
            deduped[int(pr["number"])] = pr
    return select_best_pr(list(deduped.values()))


def find_open_pr_for_branches(
    base_branch: str, head_branch: str
) -> dict[str, Any] | None:
    github = get_github_api()
    try:
        prs = github.list_pull_requests_by_branches(base_branch, head_branch, 20)
        if prs:
            return select_best_pr(prs)
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        prs = github.search_pull_requests(
            f"repo:{REPO_SLUG} is:pr is:open head:{head_branch} base:{base_branch}", 20
        )
        return select_best_pr(prs)
    except Exception:  # pylint: disable=broad-except
        return None


def create_draft_pr(
    base_branch: str, head_branch: str, title: str, body: str
) -> dict[str, Any]:
    try:
        created_pr = get_github_api().create_draft_pull_request(
            base_branch, head_branch, title, body
        )
        return {
            "ok": True,
            "number": created_pr.get("number"),
            "url": created_pr.get("html_url") or created_pr.get("url") or "",
            "authorLogin": (
                (created_pr.get("user") or {}).get("login")
                if isinstance(created_pr.get("user"), dict)
                else None
            ),
            "stderr": "",
            "stdout": "",
        }
    except GitHubApiError as error:
        return {"ok": False, "status": error.status, "stdout": "", "stderr": str(error)}


def single_line_output(value: Any) -> str:
    return str(value or "").replace(chr(10), " ").replace(chr(13), " ").strip()


def assign_architects_to_pr(
    pr_number: int | None,
    package_dir: Path | str,
    pr_author_login: str | None = None,
    architects: list[str] | None = None,
) -> None:
    if not pr_number:
        log_warning(
            "API review architect diagnostics: no PR number available; skipping reviewer request"
        )
        return
    architects = (
        architects_for_package(package_dir) if architects is None else architects
    )
    if not architects:
        log_warning(
            "API review architect diagnostics: "
            f"no architects resolved for package_dir={package_dir}; skipping reviewer request"
        )
        return
    resolved_reviewers = architect_reviewers_from_owners(architects)
    log_info(f"API review architect diagnostics: PR author login={pr_author_login}")
    reviewers = resolved_reviewers.users
    team_reviewers = resolved_reviewers.teams
    if pr_author_login:
        author_login = pr_author_login.lower()
        self_reviewers = [
            architect for architect in reviewers if architect.lower() == author_login
        ]
        reviewers = [
            architect for architect in reviewers if architect.lower() != author_login
        ]
        if self_reviewers:
            log_warning(
                "WARNING: GitHub does not allow requesting the PR author as a reviewer; "
                f"skipping architect reviewer(s) on PR #{pr_number}: "
                f"{', '.join('@' + user for user in self_reviewers)}"
            )
        if not reviewers and not team_reviewers:
            log_warning(
                "API review architect diagnostics: "
                f"all resolved architects are the PR author; no reviewer request will be sent for PR #{pr_number}"
            )
            return
    try:
        get_github_api().request_reviewers(pr_number, reviewers, team_reviewers)
        requested_owners = [
            *["@" + user for user in reviewers],
            *["@" + REPO_OWNER + "/" + team for team in team_reviewers],
        ]
        log_info(
            f"Requested API review from architect(s) on PR #{pr_number}: {', '.join(requested_owners)}"
        )
    except GitHubApiError as error:
        log_warning(
            f"WARNING: failed to request API review from architect(s) on PR #{pr_number}: {error}"
        )


def branch_reference_markdown(head_selector: str) -> str:
    parts = branch_reference_parts(head_selector)
    branch_url = f"https://github.com/{parts['owner']}/{REPO_NAME}/tree/{quote(parts['branch'], safe='')}"
    return f"[branch `{parts['display']}`]({branch_url})"


def baseline_reference_markdown(base_tag: str | None) -> str:
    if not base_tag:
        return "empty"
    commit_sha = git_out(["rev-list", "-n", "1", base_tag])
    commit_url = f"https://github.com/{REPO_SLUG}/commit/{commit_sha}"
    return f"[tag `{base_tag}`]({commit_url})"


def target_reference_info(
    head_selector: str, package_name: str | None = None
) -> dict[str, str]:
    target_tag = resolve_target_tag(head_selector, package_name)
    if target_tag:
        return {
            "label": "Target tag",
            "markdown": baseline_reference_markdown(target_tag),
        }

    if target_branch_exists(head_selector):
        pr = find_open_pr_for_head(head_selector)
        if pr:
            return {
                "label": "Working PR",
                "markdown": f"[PR #{pr['number']}]({pr['url']})",
            }
        return {
            "label": "Working branch",
            "markdown": branch_reference_markdown(head_selector),
        }

    return {
        "label": "Working branch",
        "markdown": branch_reference_markdown(head_selector),
    }


def write_bytes(file_path: Path, contents: bytes) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(contents)


def generate_api_bytes_for_ref(
    *,
    package_name: str,
    package_dir: Path,
    runtime_executable: str | None,
    ref: str,
    ref_label: str,
) -> ApiResult:
    package_relative = package_rel_dir(package_dir)
    log_info(f"Overlaying package source from {ref_label} ({ref})")

    git(["checkout", ref, "--", package_relative])
    try:
        version = read_version(package_dir)
        generate_api_for_package(package_name, runtime_executable, ref_label)

        output_path = api_md_path(package_dir)
        if not output_path.exists():
            raise RuntimeError(f"ERROR: did not produce {output_path}")

        metadata = (
            metadata_path(package_dir).read_bytes()
            if metadata_path(package_dir).exists()
            else None
        )
        return ApiResult(output_path.read_bytes(), metadata, version)
    finally:
        git(["reset", "--", package_relative], check=False)
        git(["checkout", "HEAD", "--", package_relative])
        git(["clean", "-fd", "--", package_relative], check=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an API review PR for a Python package api.md diff."
    )
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--target")
    parser.add_argument(
        "--python",
        "--runtime",
        dest="runtime_executable",
        default=os.environ.get("RUNTIME_EXECUTABLE"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if sync_working_branch_info(args.target or "main", args.package_name):
        ensure_azsdk_find_work_item_available()

    package_dir = find_package_dir(args.package_name)
    log_info(f"Found package at: {package_dir}")
    architect_reviewers = architects_for_package(package_dir)

    ensure_clean_worktree()
    original_branch = current_branch()
    if original_branch == "HEAD":
        raise RuntimeError("ERROR: refusing to run from a detached HEAD.")

    git(["fetch", REMOTE, "main"])
    base_version = validate_base_tag(args.package_name, args.base)
    target_ref = (
        resolve_target_ref(args.target, args.package_name) if args.target else MAIN_REF
    )

    try:
        log_info(f"\n=== Capturing baseline api.md from tag {args.base} ===")
        base_result = generate_api_bytes_for_ref(
            package_name=args.package_name,
            package_dir=package_dir,
            runtime_executable=args.runtime_executable,
            ref=args.base,
            ref_label=args.base,
        )

        log_info(f"\n=== Capturing target api.md from {target_ref} ===")
        target_result = generate_api_bytes_for_ref(
            package_name=args.package_name,
            package_dir=package_dir,
            runtime_executable=args.runtime_executable,
            ref=target_ref,
            ref_label=target_ref,
        )
        target_version = target_result.version

        if not api_results_have_api_diff(base_result, target_result):
            log_info(
                f"\nNo API differences found for {args.package_name} between {args.base} "
                f"(version {base_version}) and {target_ref} (version {target_version}). "
                "No API review branches or PR were created."
            )
            return 0

        api_path = api_md_path(package_dir)
        api_relative = api_md_rel(package_dir)
        meta_file_path = metadata_path(package_dir)
        meta_relative = metadata_rel(package_dir)
        desired_base_state = desired_branch_state(base_result)
        desired_review_state = desired_branch_state(target_result)

        ensure_branch_state_has_metadata_sha("baseline API result", desired_base_state)
        ensure_branch_state_has_metadata_sha("target API result", desired_review_state)

        base_selection = resolve_branch_selection(
            preferred_branch=api_review_branch_name(
                "base", args.package_name, base_version
            ),
            desired_state=desired_base_state,
            api_relative=api_relative,
            meta_relative=meta_relative,
        )
        base_branch = base_selection.branch_name

        if base_selection.reused:
            log_info(f"\n=== Reusing base branch {base_branch} ===")
            git(["checkout", "-B", base_branch, base_selection.remote_ref or ""])
        else:
            log_info(f"\n=== Creating base branch {base_branch} ===")
            git(["checkout", "-B", base_branch, MAIN_REF])
            write_bytes(api_path, base_result.api_md)
            git(["add", api_relative])
            if base_result.metadata:
                write_bytes(meta_file_path, base_result.metadata)
                git(["add", meta_relative])
            git(
                [
                    "commit",
                    "-m",
                    f"[API Review] Baseline api.md for {args.package_name} {base_version}",
                ]
            )
            git(["push", "--force-with-lease", REMOTE, base_branch])

        review_selection = resolve_branch_selection(
            preferred_branch=api_review_branch_name(
                "review", args.package_name, target_version
            ),
            desired_state=desired_review_state,
            api_relative=api_relative,
            meta_relative=meta_relative,
            required_ancestor_ref=base_branch,
        )
        review_branch = review_selection.branch_name

        if review_selection.reused:
            log_info(f"\n=== Reusing review branch {review_branch} ===")
            git(["checkout", "-B", review_branch, review_selection.remote_ref or ""])
        else:
            log_info(f"\n=== Creating review branch {review_branch} ===")
            git(["checkout", "-B", review_branch, base_branch])
            write_bytes(api_path, target_result.api_md)
            git(["add", api_relative])
            if target_result.metadata:
                write_bytes(meta_file_path, target_result.metadata)
                git(["add", meta_relative])
            git(
                [
                    "commit",
                    "-m",
                    f"[API Review] api.md for {args.package_name} {target_version}",
                ]
            )
            git(["push", "--force-with-lease", REMOTE, review_branch])

        title = (
            f"[API Review] {args.package_name} {target_version} (base {base_version})"
        )
        working_selector = args.target or "main"
        working_reference = target_reference_info(working_selector, args.package_name)
        baseline_ref = baseline_reference_markdown(args.base)
        package_work_item_id_value: int | str | None = None
        if sync_working_branch_info(working_selector, args.package_name):
            try:
                package_work_item_id_value = package_work_item_id(
                    args.package_name, target_version
                )
            except Exception as error:  # pylint: disable=broad-except
                package_work_item_id_value = "ERROR"
                log_warning(
                    "WARNING: failed to resolve package work item ID. "
                    "PR body sync metadata will set packageWorkItemId to ERROR."
                    + (f"\n{error}" if str(error) else "")
                )
        sync_metadata = build_sync_metadata_object(
            package_name=args.package_name,
            package_dir=package_dir,
            base_branch=base_branch,
            review_branch=review_branch,
            head_selector=working_selector,
            package_work_item_id_value=package_work_item_id_value,
        )
        sync_metadata_block = build_sync_metadata_block(sync_metadata)
        body = build_review_pr_body(
            package_name=args.package_name,
            target_version=target_version,
            base_version=base_version,
            working_reference=working_reference,
            baseline_ref=baseline_ref,
            sync_metadata_block=sync_metadata_block,
        )

        if base_selection.reused and review_selection.reused:
            existing_pr = find_open_pr_for_branches(base_branch, review_branch)
            if existing_pr:
                ensure_pr_body_sync_metadata(existing_pr, sync_metadata_block)
                assign_architects_to_pr(
                    existing_pr.get("number"),
                    package_dir,
                    existing_pr.get("authorLogin"),
                    architect_reviewers,
                )
                log_info(f"\n=== Reusing existing PR #{existing_pr['number']} ===")
                log_info(existing_pr["url"])
                return 0

        log_info("\n=== Opening PR ===")
        compare_url = f"https://github.com/{REPO_SLUG}/compare/{base_branch}...{review_branch}?expand=1"
        pr_create = create_draft_pr(base_branch, review_branch, title, body)
        if pr_create["ok"]:
            assign_architects_to_pr(
                pr_create.get("number"),
                package_dir,
                pr_create.get("authorLogin"),
                architect_reviewers,
            )
            if pr_create.get("url"):
                log_info(pr_create["url"])
        else:
            existing_pr = find_open_pr_for_branches(base_branch, review_branch)
            if existing_pr:
                ensure_pr_body_sync_metadata(existing_pr, sync_metadata_block)
                assign_architects_to_pr(
                    existing_pr.get("number"),
                    package_dir,
                    existing_pr.get("authorLogin"),
                    architect_reviewers,
                )
                log_info(f"\n=== Reusing existing PR #{existing_pr['number']} ===")
                log_info(existing_pr["url"])
                return 0

            error_details = "\n  ".join(
                item
                for item in [
                    f"Exit code: {pr_create.get('status')}",
                    (
                        f"stderr: {single_line_output(pr_create.get('stderr'))}"
                        if pr_create.get("stderr")
                        else ""
                    ),
                    (
                        f"stdout: {single_line_output(pr_create.get('stdout'))}"
                        if pr_create.get("stdout")
                        else ""
                    ),
                    "Debug repro: use the GitHub REST API endpoint POST "
                    f"/repos/{REPO_SLUG}/pulls with base/head/title/body/draft=true.",
                ]
                if item
            )
            log_warning(
                "\nWARNING: GitHub PR creation failed. Both branches were pushed successfully -- "
                "open the PR manually here:\n"
                f"  {compare_url}\n"
                f"  Title: {title}" + (f"\n  {error_details}" if error_details else "")
            )
        return 0
    finally:
        git(["checkout", original_branch], check=False)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # pylint: disable=broad-except
        log_error(str(error))
        sys.exit(1)
