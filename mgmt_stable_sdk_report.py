#!/usr/bin/env python3
"""Append stable-management-SDK refresh status rows to mgmt_sdk_report.md.

Workflow:
  (1) Read management SDK package names from PR 47885's data set.
  (2) Keep only packages that exist locally under sdk/*/azure-mgmt-* and have
      tsp-location.yaml.
  (3) Read apiVersions from _metadata.json. If any api-version contains
      "preview", abandon the SDK.
  (4) Read the latest SDK version from CHANGELOG.md.
      * stable SDK version + stable apiVersions -> state Done, with a best-effort
        stable refresh PR link from git history.
      * beta SDK version + stable apiVersions -> state Not Started.
  (5) Append new rows to mgmt_sdk_report.md without editing existing rows.

Requires the GitHub CLI (gh) to be installed and authenticated.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

REPO = "Azure/azure-sdk-for-python"
PR_NUMBER = "47885"
ROOT = Path(__file__).resolve().parent

SDK_NAME_RE = re.compile(r"\bazure-mgmt-[A-Za-z0-9][A-Za-z0-9_-]*\b")
CHANGELOG_RE = re.compile(r"^##\s+(\S+)\s+\((\d{4}-\d{2}-\d{2})\)")
PR_NUMBER_RE = re.compile(r"\(#(\d+)\)")
REPORT_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*(azure-mgmt-[^|\s]+)")


@dataclass(frozen=True)
class PackageRow:
    name: str
    api_versions: list[str]
    sdk_version: str
    release_date: str
    state: str
    beta_refresh_pr: str = ""
    stable_refresh_pr: str = ""


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def run_command(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def run_gh_json(args: Sequence[str]) -> dict:
    result = run_command(["gh", *args])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def fetch_pr_file(pr_number: str, file_name: str) -> str:
    pr_data = run_gh_json(["pr", "view", pr_number, "--repo", REPO, "--json", "headRefName,headRepositoryOwner,headRepository"])
    owner = pr_data["headRepositoryOwner"]["login"]
    repo = pr_data["headRepository"]["name"]
    ref = pr_data["headRefName"]
    contents = run_gh_json(["api", f"repos/{owner}/{repo}/contents/{file_name}?ref={ref}"])
    encoded = "".join(str(contents["content"]).splitlines())
    return base64.b64decode(encoded).decode("utf-8")


def sdk_names_from_data(data_text: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for line in data_text.splitlines():
        stripped = line.strip()
        if not stripped or ("service" in stripped.lower() and "folder" in stripped.lower()):
            continue
        for part in shlex.split(stripped):
            if SDK_NAME_RE.fullmatch(part) and part not in seen:
                seen.add(part)
                names.append(part)
    return names


def sdk_names_from_result(result_text: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for line in result_text.splitlines():
        if not line.startswith("|") or "azure-mgmt" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        name = cells[3]
        if SDK_NAME_RE.fullmatch(name) and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def get_candidate_sdk_names(pr_number: str) -> list[str]:
    data_names = sdk_names_from_data(fetch_pr_file(pr_number, "data.txt"))
    try:
        result_names = sdk_names_from_result(fetch_pr_file(pr_number, "result.md"))
    except Exception as ex:  # pylint: disable=broad-except
        log(f"Could not read result.md from PR {pr_number}; using explicit data.txt names only: {ex}")
        return data_names

    names: list[str] = []
    seen: set[str] = set()
    for name in [*result_names, *data_names]:
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def package_dir(sdk_name: str) -> Path | None:
    matches = sorted((ROOT / "sdk").glob(f"*/{sdk_name}"))
    for match in matches:
        if (match / "tsp-location.yaml").is_file():
            return match
    return None


def get_api_versions(pkg_dir: Path) -> list[str]:
    metadata = pkg_dir / "_metadata.json"
    if not metadata.is_file():
        return []
    data = json.loads(metadata.read_text(encoding="utf-8"))
    api_versions = data.get("apiVersions")
    if isinstance(api_versions, dict):
        values = api_versions.values()
    elif isinstance(api_versions, list):
        values = api_versions
    else:
        values = [data.get("apiVersion")]
    return sorted({str(value) for value in values if value})


def has_preview_api_version(api_versions: Sequence[str]) -> bool:
    return any("preview" in version.lower() for version in api_versions)


def get_version_and_release_date(pkg_dir: Path) -> tuple[str, str]:
    changelog = pkg_dir / "CHANGELOG.md"
    if not changelog.is_file():
        return "", ""
    for line in changelog.read_text(encoding="utf-8").splitlines():
        match = CHANGELOG_RE.match(line.strip())
        if match:
            return match.group(1), match.group(2)
    return "", ""


def is_beta_version(version: str) -> bool:
    return bool(re.search(r"\d+b\d*", version.lower()))


def find_refresh_pr(pkg_dir: Path) -> str:
    rel_path = pkg_dir.relative_to(ROOT).as_posix()
    result = run_command(["git", "log", "-n", "80", "--format=%s", "--", rel_path])
    if result.returncode != 0:
        log(f"  ! git log failed for {rel_path}: {result.stderr.strip()}")
        return ""

    for subject in result.stdout.splitlines():
        match = PR_NUMBER_RE.search(subject)
        if match and "refresh" in subject.lower():
            return match.group(1)
    return ""


def build_rows(sdk_names: Sequence[str], limit: int = 0) -> list[PackageRow]:
    rows: list[PackageRow] = []
    processed = 0
    for sdk_name in sdk_names:
        if limit and processed >= limit:
            break
        processed += 1
        log(f"Processing {sdk_name} ...")

        pkg_dir = package_dir(sdk_name)
        if not pkg_dir:
            log("  - skip: local package with tsp-location.yaml not found")
            continue

        api_versions = get_api_versions(pkg_dir)
        if not api_versions:
            log("  - skip: _metadata.json/apiVersions not found")
            continue
        if has_preview_api_version(api_versions):
            log(f"  - skip: preview api-version ({', '.join(api_versions)})")
            continue

        sdk_version, release_date = get_version_and_release_date(pkg_dir)
        if not sdk_version:
            log("  - skip: no version found in CHANGELOG.md")
            continue

        if is_beta_version(sdk_version):
            rows.append(
                PackageRow(
                    name=sdk_name,
                    api_versions=api_versions,
                    sdk_version=sdk_version,
                    release_date=release_date,
                    state="Not Started",
                )
            )
            log(f"  + keep: beta SDK version ({sdk_version}); state=Not Started")
        else:
            refresh_pr = find_refresh_pr(pkg_dir)
            rows.append(
                PackageRow(
                    name=sdk_name,
                    api_versions=api_versions,
                    sdk_version=sdk_version,
                    release_date=release_date,
                    state="Done",
                    stable_refresh_pr=refresh_pr,
                )
            )
            log(f"  + keep: stable SDK version ({sdk_version}); state=Done")
    return rows


def existing_report_state(report_path: Path) -> tuple[int, set[str]]:
    if not report_path.is_file():
        return 0, set()
    max_id = 0
    existing_names: set[str] = set()
    for line in report_path.read_text(encoding="utf-8").splitlines():
        match = REPORT_ROW_RE.match(line)
        if not match:
            continue
        max_id = max(max_id, int(match.group(1)))
        existing_names.add(match.group(2))
    return max_id, existing_names


def markdown_link(pr_number: str) -> str:
    if not pr_number:
        return ""
    return f"[#{pr_number}](https://github.com/{REPO}/pull/{pr_number})"


def table_value(value: str) -> str:
    return value.replace("|", "\\|")


def format_row(row_id: int, row: PackageRow) -> str:
    return "| " + " | ".join(
        [
            str(row_id),
            table_value(row.name),
            table_value(", ".join(row.api_versions)),
            table_value(row.sdk_version),
            markdown_link(row.beta_refresh_pr),
            table_value(row.release_date),
            table_value(row.state),
            markdown_link(row.stable_refresh_pr),
        ]
    ) + " |"


def append_rows(report_path: Path, rows: Sequence[PackageRow], include_existing: bool) -> int:
    max_id, existing_names = existing_report_state(report_path)
    rows_to_append = [row for row in rows if include_existing or row.name not in existing_names]
    if not rows_to_append:
        log("No new rows to append.")
        return 0

    existing_text = report_path.read_text(encoding="utf-8") if report_path.is_file() else ""
    prefix = "" if not existing_text or existing_text.endswith("\n") else "\n"
    lines = [format_row(max_id + index, row) for index, row in enumerate(rows_to_append, start=1)]
    with report_path.open("a", encoding="utf-8") as report_file:
        report_file.write(prefix + "\n".join(lines) + "\n")
    return len(rows_to_append)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pr", default=PR_NUMBER, help=f"PR number to read package data from. Defaults to {PR_NUMBER}.")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N candidate SDKs. 0 = all.")
    parser.add_argument("--output", type=Path, default=ROOT / "mgmt_sdk_report.md", help="Report file to append to.")
    parser.add_argument("--include-existing", action="store_true", help="Append rows even when the SDK name already exists in the report.")
    parser.add_argument("--dry-run", action="store_true", help="Print rows to stdout instead of appending to the report.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    sdk_names = get_candidate_sdk_names(args.pr)
    log(f"Discovered {len(sdk_names)} candidate SDK name(s) from PR {args.pr}.")
    rows = build_rows(sdk_names, args.limit)
    rows.sort(key=lambda row: (row.release_date, row.name), reverse=True)

    if args.dry_run:
        for index, row in enumerate(rows, start=1):
            print(format_row(index, row))
        return 0

    appended = append_rows(args.output, rows, args.include_existing)
    log(f"Appended {appended} row(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
