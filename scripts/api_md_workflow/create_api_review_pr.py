#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Create an API review PR for an Azure SDK Python package.

Workflow:
  1. Validate that ``--package-name`` exists under ``sdk/*/``.
  2. Build the BASE branch (``base_{package}_{base_version}``):
       - If ``--base`` is a tag (e.g. ``azure-ai-projects_1.0.0b1``): check out
         the tag, generate API.md, then create the base branch off the latest
         ``origin/main`` and commit the captured API.md onto it.
       - If ``--base`` is omitted: create the base branch off ``origin/main``
         and delete any existing API.md for the package (no-op if absent).
  3. Build the REVIEW branch (``review_{package}_{target_version}``):
       - If ``--target`` is omitted: use the latest ``origin/main``.
       - Otherwise: check out the given branch.
       Generate API.md on that ref, then commit it on a branch created off
       the base branch.
  4. Push both branches to ``origin`` and open a PR with title:
       ``[API Review] {package} {target_version} (base {base_version})``

Usage::

    python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-ai-projects
    python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-ai-projects \\
        --base azure-ai-projects_1.0.0b1
    python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-ai-projects \\
        --base azure-ai-projects_1.0.0b1 --target my-feature-branch

Requires ``gh`` (GitHub CLI) authenticated against the repository, plus push
access on the ``origin`` remote.
"""

from __future__ import annotations

import argparse
import json
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Optional
from urllib.parse import quote


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENERATE_SCRIPT = os.path.join(REPO_ROOT, "scripts", "generate_api_text.py")
EXPORT_SCRIPT = os.path.join(REPO_ROOT, "eng", "common", "scripts", "Export-APIViewMarkdown.ps1")
REMOTE = "origin"
MAIN_REF = f"{REMOTE}/main"


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def run(cmd, *, cwd: str = REPO_ROOT, check: bool = True, capture: bool = False, env: Optional[dict] = None) -> subprocess.CompletedProcess:
    """Run a command, echoing it first."""
    printable = " ".join(cmd) if isinstance(cmd, list) else cmd
    print(f"$ {printable}")
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        capture_output=capture,
        env=env,
    )


def git(*args: str, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    return run(["git", *args], capture=capture, check=check)


def git_out(*args: str) -> str:
    return git(*args, capture=True).stdout.strip()


# ---------------------------------------------------------------------------
# Package + ref helpers
# ---------------------------------------------------------------------------

def find_package_dir(package_name: str) -> str:
    """Locate ``sdk/*/{package_name}`` containing a pyproject.toml or setup.py."""
    pattern = os.path.join(REPO_ROOT, "sdk", "*", package_name)
    matches = [
        m for m in glob.glob(pattern)
        if os.path.isdir(m)
        and (
            os.path.exists(os.path.join(m, "pyproject.toml"))
            or os.path.exists(os.path.join(m, "setup.py"))
        )
    ]
    if not matches:
        raise SystemExit(f"ERROR: package '{package_name}' not found under sdk/*/")
    if len(matches) > 1:
        raise SystemExit(f"ERROR: multiple matches for '{package_name}': {matches}")
    return matches[0]


def package_rel_dir(package_dir: str) -> str:
    """Repo-relative POSIX path for the package directory."""
    return os.path.relpath(package_dir, REPO_ROOT).replace(os.sep, "/")


def api_md_path(package_dir: str) -> str:
    return os.path.join(package_dir, "API.md")


def api_md_rel(package_dir: str) -> str:
    return f"{package_rel_dir(package_dir)}/API.md"


_VERSION_RE = re.compile(r"""^\s*VERSION\s*[:=]\s*["']([^"']+)["']""", re.MULTILINE)


def read_version(package_dir: str) -> str:
    """Find and parse a ``_version.py`` (or ``version.py``) inside ``package_dir``."""
    candidates = []
    candidates.extend(glob.glob(os.path.join(package_dir, "**", "_version.py"), recursive=True))
    candidates.extend(glob.glob(os.path.join(package_dir, "**", "version.py"), recursive=True))
    for path in candidates:
        try:
            text = open(path, "r", encoding="utf-8").read()
        except OSError:
            continue
        m = _VERSION_RE.search(text)
        if m:
            return m.group(1)
    raise SystemExit(f"ERROR: could not find a version string in {package_dir}")


def tag_exists(tag: str) -> bool:
    result = git("rev-parse", "--verify", "--quiet", f"refs/tags/{tag}", capture=True, check=False)
    return result.returncode == 0


def ensure_clean_worktree() -> None:
    status = git_out("status", "--porcelain")
    if status:
        raise SystemExit(
            "ERROR: working tree is not clean. Commit or stash changes before running.\n"
            + status
        )


def current_branch() -> str:
    return git_out("rev-parse", "--abbrev-ref", "HEAD")


def remote_branch_ref(branch: str) -> str:
    """Return the ref name for a branch on ``REMOTE``, fetching it first."""
    git("fetch", REMOTE, branch)
    return f"{REMOTE}/{branch}"


def resolve_target_ref(target: str) -> str:
    """Resolve ``--target`` to a checkoutable ref.

    Supports both:
    - ``branch``: fetched from ``origin`` and returned as ``origin/branch``
    - ``owner:branch``: fetched from ``https://github.com/{owner}/azure-sdk-for-python.git``
      and returned as ``FETCH_HEAD``
    """
    if ":" not in target:
        return remote_branch_ref(target)

    owner, branch = target.split(":", 1)
    if not owner or not branch:
        raise SystemExit(
            f"ERROR: invalid --target '{target}'. Expected either 'branch' or 'owner:branch'."
        )

    fork_url = f"https://github.com/{owner}/azure-sdk-for-python.git"
    git("fetch", fork_url, branch)
    return "FETCH_HEAD"


# ---------------------------------------------------------------------------
# API.md generation
# ---------------------------------------------------------------------------

def generate_api_md(package_name: str, package_dir: str) -> bytes:
    """Run ``generate_api_text.py`` for the package and return the bytes of the
    resulting API.md. The file is also left on disk at its canonical location.
    """
    print(f"--- Generating API.md for {package_name} on {current_branch_or_sha()} ---")
    run([sys.executable, GENERATE_SCRIPT, package_name])
    path = api_md_path(package_dir)
    if not os.path.exists(path):
        raise SystemExit(f"ERROR: generate_api_text.py did not produce {path}")
    with open(path, "rb") as f:
        return f.read()


def current_branch_or_sha() -> str:
    name = git_out("rev-parse", "--abbrev-ref", "HEAD")
    if name == "HEAD":
        return git_out("rev-parse", "--short", "HEAD")
    return name


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    doc = __doc__ or "Create an API review PR"
    p = argparse.ArgumentParser(description=doc.splitlines()[0])
    p.add_argument("--package-name", required=True,
                   help="Package directory name under sdk/*/ (e.g. azure-ai-projects)")
    p.add_argument("--base", default=None,
                   help="Tag to use as the API.md baseline, formatted as "
                        "'{package-name}_{version}'. Omit to make the baseline empty.")
    p.add_argument("--target", default=None,
                   help="Branch containing the API to review. Supports 'branch' or 'owner:branch'. Omit to use the latest origin/main.")
    return p.parse_args()


def validate_base_tag(package_name: str, base: str) -> str:
    """Validate the ``--base`` tag format/existence and return the version."""
    if not base.startswith(f"{package_name}_"):
        raise SystemExit(
            f"ERROR: --base tag '{base}' must start with '{package_name}_'."
        )
    version = base[len(package_name) + 1:]
    if not version:
        raise SystemExit(f"ERROR: --base tag '{base}' is missing the version suffix.")
    if not tag_exists(base):
        raise SystemExit(f"ERROR: tag '{base}' does not exist in this repository.")
    return version


def write_bytes(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def main() -> int:
    args = parse_args()
    package_name = args.package_name

    package_dir = find_package_dir(package_name)
    print(f"Found package at: {package_dir}")

    ensure_clean_worktree()
    original_branch = current_branch()
    if original_branch == "HEAD":
        raise SystemExit("ERROR: refusing to run from a detached HEAD.")

    # Always fetch main once up-front.
    git("fetch", REMOTE, "main")

    # ---- Validate inputs --------------------------------------------------
    base_version = "none"
    if args.base is not None:
        base_version = validate_base_tag(package_name, args.base)

    target_ref: str
    if args.target is None:
        target_ref = MAIN_REF
    else:
        target_ref = resolve_target_ref(args.target)

    # Cache the generate + export scripts (they may not exist on older refs we check out).
    tmp_script_dir = tempfile.mkdtemp(prefix="apirev_script_")
    cached_script = os.path.join(tmp_script_dir, "generate_api_text.py")
    cached_export = os.path.join(tmp_script_dir, "Export-APIViewMarkdown.ps1")
    shutil.copy2(GENERATE_SCRIPT, cached_script)
    shutil.copy2(EXPORT_SCRIPT, cached_export)

    try:
        # ---- Step 1: capture base API.md content (if base is a tag) ------
        base_api_bytes: Optional[bytes] = None
        if args.base is not None:
            print(f"\n=== Capturing baseline API.md from tag {args.base} ===")
            git("checkout", "--detach", args.base)
            base_api_bytes = _generate_with_cached_script(
                cached_script, cached_export, package_name, package_dir
            )

        # ---- Step 2: capture target API.md content -----------------------
        print(f"\n=== Capturing target API.md from {target_ref} ===")
        git("checkout", "--detach", target_ref)
        target_version = read_version(package_dir)
        target_api_bytes = _generate_with_cached_script(
            cached_script, cached_export, package_name, package_dir
        )

        # ---- Step 3: build base branch off origin/main -------------------
        base_branch = f"base_{package_name}_{base_version}"
        review_branch = f"review_{package_name}_{target_version}"

        print(f"\n=== Creating base branch {base_branch} ===")
        git("checkout", "-B", base_branch, MAIN_REF)

        api_path = api_md_path(package_dir)
        api_relative = api_md_rel(package_dir)

        if base_api_bytes is not None:
            write_bytes(api_path, base_api_bytes)
            git("add", api_relative)
            git("commit", "-m",
                f"[API Review] Baseline API.md for {package_name} {base_version}")
        else:
            # Is the file tracked in the branch we just created? (Not "is it on disk?" --
            # generate_api_text.py from a previous step may have left an untracked copy.)
            tracked = git("ls-files", "--error-unmatch", api_relative,
                          capture=True, check=False)
            if tracked.returncode == 0:
                git("rm", api_relative)
                git("commit", "-m",
                    f"[API Review] Remove API.md for {package_name} (empty baseline)")
            else:
                # Ensure no stray untracked copy is left in the working tree.
                if os.path.exists(api_path):
                    os.remove(api_path)
                git("commit", "--allow-empty", "-m",
                    f"[API Review] Empty baseline for {package_name}")

        git("push", "--force-with-lease", REMOTE, base_branch)

        # ---- Step 4: build review branch off base branch -----------------
        print(f"\n=== Creating review branch {review_branch} ===")
        git("checkout", "-B", review_branch, base_branch)
        write_bytes(api_path, target_api_bytes)
        git("add", api_relative)
        # If the bytes happen to be identical to the base, commit empty so we
        # still have something to PR.
        diff = git("diff", "--cached", "--quiet", capture=True, check=False)
        if diff.returncode == 0:
            git("commit", "--allow-empty", "-m",
                f"[API Review] API.md for {package_name} {target_version} (no diff vs baseline)")
        else:
            git("commit", "-m",
                f"[API Review] API.md for {package_name} {target_version}")

        git("push", "--force-with-lease", REMOTE, review_branch)

        # ---- Step 5: open PR --------------------------------------------
        title = f"[API Review] {package_name} {target_version} (base {base_version})"
        working_selector = args.target or original_branch
        working_ref = _working_reference_markdown(working_selector)
        body_lines = [
            f"Automated API review PR for `{package_name}`.",
            "",
            f"- **Working branch:** {working_ref}",
            f"- **Target:** `{args.target or 'origin/main'}` (version `{target_version}`)",
            f"- **Baseline:** {'tag `' + args.base + '`' if args.base else '_empty_'} "
            f"(version `{base_version}`)",
            "",
            "Generated by `scripts/api_md_workflow/create_api_review_pr.py`.",
        ]
        body = "\n".join(body_lines)

        print(f"\n=== Opening PR ===")
        compare_url = (
            f"https://github.com/Azure/azure-sdk-for-python/compare/"
            f"{base_branch}...{review_branch}?expand=1"
        )
        pr_result = run([
            "gh", "pr", "create",
            "--repo", "Azure/azure-sdk-for-python",
            "--base", base_branch,
            "--head", review_branch,
            "--title", title,
            "--body", body,
            "--draft",
        ], check=False, env=_env_with_real_git())
        if pr_result.returncode != 0:
            print(
                "\nWARNING: `gh pr create` failed. Both branches were pushed "
                "successfully -- open the PR manually here:\n"
                f"  {compare_url}\n"
                f"  Title: {title}"
            )

        return 0

    finally:
        # Restore the user's original branch.
        try:
            git("checkout", original_branch, check=False)
        finally:
            shutil.rmtree(tmp_script_dir, ignore_errors=True)


def _find_real_git_exe() -> Optional[str]:
    """Locate the real ``git.exe`` (skipping any .cmd/.bat shims on PATH).

    On Windows, some environments install a ``git.cmd`` wrapper in front of
    the real ``git.exe`` (e.g. ``C:\\Windows\\System32\\git.cmd``). ``gh``
    spawns ``git`` as a child process and is sensitive to argument quoting
    when the resolved binary is a ``.cmd`` shim -- subcommands like
    ``git merge-base`` get mangled into ``merge``. We search PATH for an
    actual ``git.exe`` so we can prefer it.
    """
    if os.name != "nt":
        return None
    seen = set()
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        entry = entry.strip('"')
        if not entry or entry.lower() in seen:
            continue
        seen.add(entry.lower())
        candidate = os.path.join(entry, "git.exe")
        if os.path.isfile(candidate):
            return candidate
    # Fallback: common install location.
    fallback = r"C:\Program Files\Git\cmd\git.exe"
    return fallback if os.path.isfile(fallback) else None


def _env_with_real_git() -> dict:
    """Return a copy of os.environ with the real git.exe directory pushed to
    the front of PATH (no-op on non-Windows or if no .exe is found)."""
    env = os.environ.copy()
    real_git = _find_real_git_exe()
    if not real_git:
        return env
    git_dir = os.path.dirname(real_git)
    current_path = env.get("PATH", "")
    # Only prepend if it isn't already first.
    parts = current_path.split(os.pathsep)
    if not parts or parts[0].rstrip("\\").lower() != git_dir.rstrip("\\").lower():
        env["PATH"] = git_dir + os.pathsep + current_path
        print(f"(prepending real git to PATH for gh: {git_dir})")
    return env


def _find_open_pr_for_head(head_selector: str) -> Optional[dict]:
    """Return best PR metadata for a head selector, or None when no PR exists.

    ``head_selector`` supports both ``branch`` and ``owner:branch``.
    Preference order:
    1) Open PRs
    2) Most recently updated PR (if only closed/merged PRs exist)
    """

    def _parse_prs(output: str) -> Optional[list]:
        try:
            prs = json.loads(output or "[]")
        except json.JSONDecodeError:
            return None
        if not isinstance(prs, list):
            return None
        return prs

    def _select_best(prs: list) -> Optional[dict]:
        candidates = [
            pr
            for pr in prs
            if isinstance(pr, dict)
            and "number" in pr
            and "url" in pr
            and "state" in pr
            and "updatedAt" in pr
        ]
        if not candidates:
            return None

        open_prs = [pr for pr in candidates if str(pr.get("state", "")).lower() == "open"]
        pool = open_prs or candidates
        # ISO-8601 timestamps sort correctly lexicographically.
        pool.sort(key=lambda pr: str(pr.get("updatedAt", "")), reverse=True)
        return pool[0]

    env = _env_with_real_git()
    selectors = [head_selector]
    if ":" in head_selector:
        _, branch_only = head_selector.split(":", 1)
        if branch_only and branch_only not in selectors:
            selectors.append(branch_only)

    all_prs = []

    # First attempt: native head filter for each selector form.
    for selector in selectors:
        direct = run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                "Azure/azure-sdk-for-python",
                "--head",
                selector,
                "--state",
                "all",
                "--json",
                "number,url,state,updatedAt",
                "--limit",
                "50",
            ],
            check=False,
            capture=True,
            env=env,
        )
        if direct.returncode == 0:
            direct_prs = _parse_prs(direct.stdout)
            if direct_prs:
                all_prs.extend(direct_prs)

    # Fallback: search filter for each selector form.
    for selector in selectors:
        search_query = f"repo:Azure/azure-sdk-for-python head:{selector}"
        search = run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                "Azure/azure-sdk-for-python",
                "--search",
                search_query,
                "--state",
                "all",
                "--json",
                "number,url,state,updatedAt",
                "--limit",
                "50",
            ],
            check=False,
            capture=True,
            env=env,
        )
        if search.returncode == 0:
            search_prs = _parse_prs(search.stdout)
            if search_prs:
                all_prs.extend(search_prs)

    if not all_prs:
        return None

    # De-duplicate by PR number.
    deduped = {}
    for pr in all_prs:
        if isinstance(pr, dict) and "number" in pr:
            deduped[pr["number"]] = pr

    return _select_best(list(deduped.values()))


def _working_reference_markdown(head_selector: str) -> str:
    """Build markdown for a working head selector, preferring an open PR link."""
    pr = _find_open_pr_for_head(head_selector)
    if pr:
        return f"[PR #{pr['number']}]({pr['url']})"

    if ":" in head_selector:
        owner, branch = head_selector.split(":", 1)
        branch_url = f"https://github.com/{owner}/azure-sdk-for-python/tree/{quote(branch, safe='')}"
        return f"[branch `{head_selector}`]({branch_url})"

    branch_url = f"https://github.com/Azure/azure-sdk-for-python/tree/{quote(head_selector, safe='')}"
    return f"[branch `{head_selector}`]({branch_url})"


def _generate_with_cached_script(cached_script: str, cached_export: str, package_name: str, package_dir: str) -> bytes:
    """Run the cached copy of generate_api_text.py against the currently
    checked-out ref and return the bytes of the resulting API.md."""
    print(f"--- Generating API.md on {current_branch_or_sha()} ---")
    env = os.environ.copy()
    env["AZSDK_REPO_ROOT"] = REPO_ROOT
    env["AZSDK_EXPORT_SCRIPT"] = cached_export
    run([sys.executable, cached_script, package_name], env=env)
    path = api_md_path(package_dir)
    if not os.path.exists(path):
        raise SystemExit(f"ERROR: did not produce {path}")
    with open(path, "rb") as f:
        return f.read()


if __name__ == "__main__":
    sys.exit(main())
