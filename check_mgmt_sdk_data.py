#!/usr/bin/env python
"""Check management SDK package and TypeSpec metadata from data.txt.

Quick usage from the azure-sdk-for-python repo root:

    python .\\check_mgmt_sdk_data.py <path-to-azure-rest-api-specs>

By default this reads ./data.txt, checks SDK packages under ./sdk, and writes
./result.md. Use --data, --sdk-repo, or --output to override those paths.
"""

from __future__ import annotations

import argparse
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


SDK_NAME_PATTERN = re.compile(r"\bazure-mgmt-[A-Za-z0-9][A-Za-z0-9_-]*")


@dataclass(frozen=True)
class DataRow:
    service_folder_1: str
    service_folder_2: str
    sdk_name: str = ""


@dataclass(frozen=True)
class ResultRow:
    row_id: int
    service_folder_1: str
    service_folder_2: str
    sdk_name: str
    path_exists: bool | None
    tsp_file_exists: bool | None


def parse_data_file(data_file: Path) -> list[DataRow]:
    rows: list[DataRow] = []
    for line in data_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        parts = shlex.split(stripped)
        if len(parts) < 2 or "service" in stripped.lower() and "folder" in stripped.lower():
            continue

        rows.append(DataRow(parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return rows


def candidate_tsp_roots(rest_repo: Path, service_folder_1: str, service_folder_2: str) -> list[Path]:
    service_folder_2_parts = Path(service_folder_2).parts
    roots = [
        rest_repo / service_folder_1 / service_folder_2,
        rest_repo / "specification" / service_folder_1 / service_folder_2,
    ]

    if service_folder_2_parts:
        spec_root = rest_repo / "specification" / service_folder_2_parts[0] / "resource-manager"
        service_remainder = Path(*service_folder_2_parts[1:]) if len(service_folder_2_parts) > 1 else Path()
        if service_remainder.parts and service_remainder.parts[0].lower() == service_folder_1.lower():
            roots.append(spec_root / service_remainder)
        else:
            roots.append(spec_root / service_folder_1 / service_remainder)
        roots.append(rest_repo / "specification" / service_folder_2_parts[0])

    return roots


def iter_tspconfigs(root: Path) -> Iterable[Path]:
    direct_tspconfig = root / "tspconfig.yaml"
    if direct_tspconfig.is_file():
        yield direct_tspconfig

    if root.is_dir():
        for tspconfig in sorted(root.rglob("tspconfig.yaml")):
            if tspconfig != direct_tspconfig:
                yield tspconfig


def find_sdk_name_from_tspconfig(rest_repo: Path, service_folder_1: str, service_folder_2: str) -> str:
    seen: set[Path] = set()
    for root in candidate_tsp_roots(rest_repo, service_folder_1, service_folder_2):
        for tspconfig in iter_tspconfigs(root):
            if tspconfig in seen:
                continue
            seen.add(tspconfig)
            match = SDK_NAME_PATTERN.search(tspconfig.read_text(encoding="utf-8"))
            if match:
                return match.group(0)
    return ""


def sdk_package_paths(sdk_repo: Path, sdk_name: str) -> list[Path]:
    if not sdk_name:
        return []
    return sorted(path for path in (sdk_repo / "sdk").glob(f"*/{sdk_name}") if path.is_dir())


def build_results(data_rows: Sequence[DataRow], rest_repo: Path, sdk_repo: Path) -> list[ResultRow]:
    results: list[ResultRow] = []
    for row_id, row in enumerate(data_rows, start=1):
        sdk_name = row.sdk_name or find_sdk_name_from_tspconfig(rest_repo, row.service_folder_1, row.service_folder_2)
        if row.sdk_name and not SDK_NAME_PATTERN.fullmatch(row.sdk_name):
            results.append(
                ResultRow(
                    row_id=row_id,
                    service_folder_1=row.service_folder_1,
                    service_folder_2=row.service_folder_2,
                    sdk_name=sdk_name,
                    path_exists=None,
                    tsp_file_exists=None,
                )
            )
            continue

        package_paths = sdk_package_paths(sdk_repo, sdk_name)
        results.append(
            ResultRow(
                row_id=row_id,
                service_folder_1=row.service_folder_1,
                service_folder_2=row.service_folder_2,
                sdk_name=sdk_name,
                path_exists=bool(package_paths),
                tsp_file_exists=any((package_path / "tsp-location.yaml").is_file() for package_path in package_paths),
            )
        )
    return results


def table_value(value: object) -> str:
    return str(value).replace("|", "\\|")


def check_value(value: bool | None) -> str:
    if value is None:
        return "-"
    return "Y" if value else "N"


def write_result_markdown(results: Sequence[ResultRow], output_file: Path) -> None:
    lines = [
        "| id | service folder 1 | service folder 2 | sdk name (azure-mgmt-*) | path exist (Y/N) | tsp file (Y/N) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    table_value(result.row_id),
                    table_value(result.service_folder_1),
                    table_value(result.service_folder_2),
                    table_value(result.sdk_name),
                    check_value(result.path_exists),
                    check_value(result.tsp_file_exists),
                ]
            )
            + " |"
        )

    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check management SDK packages listed in data.txt.")
    parser.add_argument("rest_repo", type=Path, help="Path to the azure-rest-api-specs repository.")
    parser.add_argument("--data", type=Path, default=Path("data.txt"), help="Input data file. Defaults to data.txt.")
    parser.add_argument("--output", type=Path, default=Path("result.md"), help="Output markdown file. Defaults to result.md.")
    parser.add_argument("--sdk-repo", type=Path, default=Path(__file__).resolve().parent, help="Path to this SDK repository.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    data_rows = parse_data_file(args.data)
    results = build_results(data_rows, args.rest_repo, args.sdk_repo)
    write_result_markdown(results, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())