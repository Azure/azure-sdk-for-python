#!/usr/bin/env python
"""Find azure-mgmt-* packages whose latest CHANGELOG version is not yet on PyPI.

Steps:
  1. Discover all CHANGELOG.md files matching ``sdk/*/azure-mgmt-*/CHANGELOG.md``.
  2. Parse the latest version section header (``## <version> (<date>)``) and check
     whether that version exists on PyPI.
  3. Write the results (unreleased versions only) to a Markdown table.

Usage:
    python check_unreleased_mgmt.py [--repo-root PATH] [--output PATH]
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Tuple

# Matches a CHANGELOG section header, e.g. "## 26.0.0b1 (2026-06-08)".
VERSION_HEADER_RE = re.compile(r"^##\s+([0-9][\w.+-]*)\s*(?:\(([^)]*)\))?\s*$")

GITHUB_BLOB_BASE = "https://github.com/Azure/azure-sdk-for-python/blob/main"
PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
PYPI_PROJECT_URL = "https://pypi.org/project/{package}/#history"


def find_changelogs(repo_root: Path):
    """Yield CHANGELOG.md paths matching sdk/*/azure-mgmt-*/CHANGELOG.md."""
    return sorted(repo_root.glob("sdk/*/azure-mgmt-*/CHANGELOG.md"))


def parse_latest_version(changelog: Path) -> Optional[str]:
    """Return the first (latest) version string from a CHANGELOG, or None."""
    try:
        with changelog.open("r", encoding="utf-8") as handle:
            for line in handle:
                match = VERSION_HEADER_RE.match(line.strip())
                if match:
                    return match.group(1)
    except OSError:
        return None
    return None


def is_version_on_pypi(package: str, version: str) -> bool:
    """Return True if the given version of package is published on PyPI."""
    url = PYPI_JSON_URL.format(package=package)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            # Package itself has never been published.
            return False
        raise
    releases = data.get("releases", {})
    return version in releases


def github_changelog_link(repo_root: Path, changelog: Path) -> str:
    rel = changelog.relative_to(repo_root).as_posix()
    return f"{GITHUB_BLOB_BASE}/{rel}"


def process(repo_root: Path, changelog: Path) -> Optional[Tuple[str, str, str, str]]:
    """Return a result row if the latest version is unreleased, else None."""
    package = changelog.parent.name
    version = parse_latest_version(changelog)
    if not version:
        return None
    if is_version_on_pypi(package, version):
        return None
    changelog_link = github_changelog_link(repo_root, changelog)
    pypi_link = PYPI_PROJECT_URL.format(package=package)
    return (package, version, changelog_link, pypi_link)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Path to the repository root (default: parent directory of this script).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("unreleased_mgmt_packages.md"),
        help="Output Markdown file (default: unreleased_mgmt_packages.md).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=16,
        help="Number of concurrent PyPI lookups (default: 16).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    changelogs = find_changelogs(repo_root)
    print(f"Found {len(changelogs)} azure-mgmt-* CHANGELOG.md files.")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process, repo_root, cl): cl for cl in changelogs}
        for future in as_completed(futures):
            changelog = futures[future]
            try:
                row = future.result()
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"  ! Error processing {changelog.parent.name}: {exc}", file=sys.stderr)
                continue
            if row:
                print(f"  - Unreleased: {row[0]} {row[1]}")
                results.append(row)

    results.sort(key=lambda r: r[0])

    lines = [
        "# Unreleased azure-mgmt-* Packages",
        "",
        f"Total: {len(results)} package(s) with an unreleased latest CHANGELOG version.",
        "",
        "| SDK Name | Unreleased Version | CHANGELOG | PyPI |",
        "| --- | --- | --- | --- |",
    ]
    for package, version, changelog_link, pypi_link in results:
        lines.append(
            f"| {package} | {version} | [CHANGELOG.md]({changelog_link}) | [release history]({pypi_link}) |"
        )
    lines.append("")

    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(results)} result(s) to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())