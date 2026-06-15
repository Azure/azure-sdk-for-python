#!/usr/bin/env python3
"""Generate a Markdown report of stable, non-SDK-bot management (mgmt) SDKs.

Workflow:
  (1) Discover all mgmt SDKs via the glob ``sdk/*/azure-mgmt-*/tsp-location.yaml``
      (ignoring cache/virtualenv folders such as ``.tox``, ``.venv``,
      ``.pytest_cache``, ``.mypy_cache``, ...).
  (2) Read each SDK's api-version from the ``:keyword api_version:`` docstring in
      ``azure/mgmt/*/_client.py``. If the api-version contains ``preview`` ->
      drop the SDK.
  (3) Read the latest sdk version + release date from ``CHANGELOG.md``. If the
      version contains ``b`` (beta/preview release) -> keep the SDK; otherwise
      -> drop the SDK.
  (4) Find the latest merged PR that touched the package directory (via the
      squash-merge ``(#NNNN)`` reference on the last commit), then read the PR
      body with ``gh``. If the body contains ``Submitted by`` -> drop the SDK.
  (5) Write a Markdown table:
      id / sdk name / api version / sdk version / pr link / release date.

Use ``--limit 1`` to process a single SDK quickly for a manual sanity check.

Requires the GitHub CLI (``gh``) to be installed and authenticated
(``gh auth login``) for the PR-body check.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO = "Azure/azure-sdk-for-python"
ROOT = Path(__file__).resolve().parent

# Folders that may contain installed/cached copies of packages we must ignore.
IGNORED_PARTS = {
    ".tox",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".pyright",
    "__pycache__",
    "node_modules",
    ".git",
    "build",
    "dist",
    ".eggs",
}

# Regex helpers.
# The ``:keyword api_version:`` docstring block, captured up to ``:paramtype``.
_API_VERSION_DOC_RE = re.compile(
    r":keyword api_version:.*?:paramtype\s+api_version:", re.DOTALL
)
# First quoted date-like api-version inside that block (e.g. "2026-01-01" or
# "2025-03-01-preview").
_API_VERSION_VALUE_RE = re.compile(r'"(\d{4}-\d{2}-\d{2}[^"]*)"')
# CHANGELOG heading like ``## 5.0.0b1 (2026-05-27)``.
_CHANGELOG_RE = re.compile(r"^##\s+(\S+)\s+\((\d{4}-\d{2}-\d{2})\)")
_PR_NUMBER_RE = re.compile(r"\(#(\d+)\)")


def log(message: str) -> None:
    """Print progress to stderr so stdout stays clean."""
    print(message, file=sys.stderr, flush=True)


def find_mgmt_sdks() -> list[Path]:
    """Return sorted package directories that contain a tsp-location.yaml.

    Paths under cache/virtualenv folders are filtered out.
    """
    pattern = str(ROOT / "sdk" / "*" / "azure-mgmt-*" / "tsp-location.yaml")
    result: list[Path] = []
    for match in glob.glob(pattern):
        path = Path(match)
        if IGNORED_PARTS.intersection(path.parts):
            continue
        result.append(path.parent)
    return sorted(result)


def get_api_version(pkg_dir: Path) -> Optional[str]:
    """Read the api-version from the _client.py ``:keyword api_version:`` docstring."""
    candidates = [
        c for c in pkg_dir.glob("azure/mgmt/*/_client.py") if "aio" not in c.parts
    ]
    if not candidates:
        candidates = [
            c for c in pkg_dir.glob("azure/mgmt/**/_client.py") if "aio" not in c.parts
        ]
    for client in sorted(candidates):
        block = _API_VERSION_DOC_RE.search(client.read_text(encoding="utf-8"))
        if not block:
            continue
        value = _API_VERSION_VALUE_RE.search(block.group(0))
        if value:
            return value.group(1)
    return None


def get_version_and_release_date(pkg_dir: Path) -> tuple[Optional[str], Optional[str]]:
    """Read the latest (version, release date) from CHANGELOG.md."""
    changelog = pkg_dir / "CHANGELOG.md"
    if not changelog.exists():
        return None, None
    for line in changelog.read_text(encoding="utf-8").splitlines():
        match = _CHANGELOG_RE.match(line.strip())
        if match:
            return match.group(1), match.group(2)
    return None, None


def get_latest_pr_number(pkg_dir: Path) -> Optional[str]:
    """Find the latest merged PR number touching the package directory.

    Uses ``git log`` over the package path and extracts the squash-merge
    ``(#NNNN)`` reference from the most recent commit subject that has one.
    """
    rel_path = pkg_dir.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "log", "-n", "50", "--format=%s", "--", rel_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log(f"  ! git log failed for {rel_path}: {result.stderr.strip()}")
        return None
    for subject in result.stdout.splitlines():
        match = _PR_NUMBER_RE.search(subject)
        if match:
            return match.group(1)
    return None


def get_pr_body_and_url(pr_number: str) -> tuple[Optional[str], str]:
    """Return (body, url) for a PR using the gh CLI.

    Returns (None, url) when the body could not be retrieved.
    """
    url = f"https://github.com/{REPO}/pull/{pr_number}"
    result = subprocess.run(
        ["gh", "pr", "view", pr_number, "--repo", REPO, "--json", "body,url"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log(f"  ! gh pr view {pr_number} failed: {result.stderr.strip()}")
        return None, url
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, url
    return data.get("body") or "", data.get("url") or url


def build_report(rows: list[dict]) -> str:
    """Render the kept SDK rows as a Markdown document with a table."""
    lines = [
        "# Stable Management SDK Report",
        "",
        f"Total kept SDKs: {len(rows)}",
        "",
        "| id | sdk name | api version | sdk version | pr link | release date |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(rows, start=1):
        pr_link = f"[#{row['pr_number']}]({row['pr_url']})" if row.get("pr_number") else ""
        lines.append(
            f"| {index} | {row['name']} | {row['api_version']} | "
            f"{row.get('sdk_version') or ''} | {pr_link} | "
            f"{row.get('release_date') or ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Process only the first N discovered SDKs (use 1 for a quick check). 0 = all.",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "mgmt_sdk_report.md"),
        help="Path to the output Markdown file.",
    )
    args = parser.parse_args()

    sdks = find_mgmt_sdks()
    log(f"Discovered {len(sdks)} mgmt SDK(s).")
    if args.limit > 0:
        sdks = sdks[: args.limit]
        log(f"Limiting to first {len(sdks)} SDK(s) (--limit {args.limit}).")

    kept: list[dict] = []
    for pkg_dir in sdks:
        name = pkg_dir.name
        log(f"Processing {name} ...")

        api_version = get_api_version(pkg_dir)
        if not api_version:
            log("  - skip: no api-version found")
            continue
        if "preview" in api_version.lower():
            log(f"  - skip: preview api-version ({api_version})")
            continue

        sdk_version, release_date = get_version_and_release_date(pkg_dir)
        if not sdk_version:
            log("  - skip: no version found in CHANGELOG.md")
            continue
        if "b" not in sdk_version.lower():
            log(f"  - skip: non-beta sdk version ({sdk_version})")
            continue

        pr_number = get_latest_pr_number(pkg_dir)
        if not pr_number:
            log("  - skip: no PR found for package path")
            continue

        body, pr_url = get_pr_body_and_url(pr_number)
        if body is not None and "Submitted by" in body:
            log(f"  - skip: PR #{pr_number} body contains 'Submitted by'")
            continue

        kept.append(
            {
                "name": name,
                "api_version": api_version,
                "sdk_version": sdk_version,
                "release_date": release_date,
                "pr_number": pr_number,
                "pr_url": pr_url,
            }
        )
        log(
            f"  + keep: api={api_version}, version={sdk_version}, "
            f"release={release_date}, pr=#{pr_number}"
        )

    report = build_report(kept)
    output_path = Path(args.output)
    output_path.write_text(report, encoding="utf-8")
    log(f"Wrote {len(kept)} row(s) to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
