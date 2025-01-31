#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import os
import argparse
import json
import json
import logging
from typing import Optional
from breaking_changes_allowlist import RUN_BREAKING_CHANGES_PACKAGES, IGNORE_BREAKING_CHANGES
from code_reporter import CodeReporter
from breaking_changes_tracker import BreakingChangesTracker
from changelog_tracker import ChangelogTracker
from pathlib import Path
from supported_checkers import CHECKERS

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
_LOGGER = logging.getLogger(__name__)

def test_compare_reports(pkg_dir: str, changelog: bool, source_report: str = "stable.json", target_report: str = "current.json") -> None:
    package_name = os.path.basename(pkg_dir)

    with open(os.path.join(pkg_dir, source_report), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, target_report), "r") as fd:
        current = json.load(fd)

    if "azure-mgmt-" in package_name:
        stable = report_azure_mgmt_versioned_module(stable)
        current = report_azure_mgmt_versioned_module(current)

    checker = BreakingChangesTracker(
        stable,
        current,
        package_name,
        checkers = CHECKERS,
        ignore = IGNORE_BREAKING_CHANGES
    )
    if changelog:
        checker = ChangelogTracker(stable, current, package_name, checkers = CHECKERS, ignore = IGNORE_BREAKING_CHANGES)
    checker.run_checks()

    remove_json_files(pkg_dir)

    print(checker.report_changes())

    if not changelog and checker.breaking_changes:
        exit(1)


def remove_json_files(pkg_dir: str) -> None:
    stable_json = os.path.join(pkg_dir, "stable.json")
    current_json = os.path.join(pkg_dir, "current.json")
    if os.path.isfile(stable_json):
        os.remove(stable_json)
    if os.path.isfile(current_json):
        os.remove(current_json)
    _LOGGER.info("cleaning up")


def report_azure_mgmt_versioned_module(code_report):
    
    def parse_module_name(module):
        split_module = module.split(".")
        # Azure mgmt packages are typically in the form of: azure.mgmt.<service>
        # If the module has a version, it will be in the form of: azure.mgmt.<service>.<version> or azure.mgmt.<service>.<version>.<submodule>
        if len(split_module) >= 4:
            for i in range(3, len(split_module)):
                if re.search(r"v\d{4}_\d{2}_\d{2}", split_module[i]):
                    split_module.pop(i)
                    break
        return ".".join(split_module)

    sorted_modules = sorted(code_report.keys())
    merged_report = {}
    for module in sorted_modules:
        non_version_module_name = parse_module_name(module)
        if non_version_module_name not in merged_report:
            merged_report[non_version_module_name] = code_report[module]
            continue
        merged_report[non_version_module_name].update(code_report[module])
    return merged_report

def main(
        target_module: str,
        version: str,
        in_venv: bool,
        pkg_dir: str,
        changelog: bool,
        code_report: bool,
        latest_pypi_version: bool,
        source_report: Optional[Path],
        target_report: Optional[Path]
    ):
    code_reporter = CodeReporter(pkg_dir, pkg_version=version, target_module=target_module, in_venv=in_venv, latest_pypi_version=latest_pypi_version)

    # If code_report is set, only generate a code report for the package and return
    if code_report:
        public_api = code_reporter.build_library_report()
        with open("code_report.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("code_report.json is written.")
        return

    # If source_report and target_report are provided, compare the two reports
    if source_report and target_report:
        test_compare_reports(pkg_dir, changelog, str(source_report), str(target_report))
        return

    try:
        code_reporter.report()
        test_compare_reports(pkg_dir, changelog)
    except Exception as err:  # catch any issues with capturing the public API and building the report
        print("\n*****See aka.ms/azsdk/breaking-changes-tool to resolve any build issues*****\n")
        remove_json_files(pkg_dir)
        raise err


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run breaking changes checks against target folder."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to will be <target_package>/azure.",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--module",
        dest="target_module",
        help="The target module. The target module passed will be the top most module in the package",
    )

    parser.add_argument(
        "-v",
        "--in-venv",
        dest="in_venv",
        help="Check if we are in the newly created venv.",
        default=False
    )

    parser.add_argument(
        "-s",
        "--stable-version",
        dest="stable_version",
        help="The stable version of the target package, if it exists on PyPi.",
        default=None
    )

    parser.add_argument(
        "-c",
        "--changelog",
        dest="changelog",
        help="Output changes listed in changelog format.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--code-report",
        dest="code_report",
        help="Output a code report for a package.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--source-report",
        dest="source_report",
        help="Path to the code report for the previous package version.",
    )

    parser.add_argument(
        "--target-report",
        dest="target_report",
        help="Path to the code report for the new package version.",
    )

    parser.add_argument(
        "--latest-pypi-version",
        dest="latest_pypi_version",
        help="Use the latest package version on PyPi (can be preview or stable).",
        action="store_true",
        default=False,
    )

    args, unknown = parser.parse_known_args()
    if unknown:
        _LOGGER.info(f"Ignoring unknown arguments: {unknown}")

    in_venv = args.in_venv
    stable_version = args.stable_version
    target_module = args.target_module
    pkg_dir = os.path.abspath(args.target_package)
    package_name = os.path.basename(pkg_dir)
    changelog = args.changelog
    logging.basicConfig(level=logging.INFO)

    # We dont need to block for code report generation
    if not args.code_report:
        if package_name not in RUN_BREAKING_CHANGES_PACKAGES and not any(bool(re.findall(p, package_name)) for p in RUN_BREAKING_CHANGES_PACKAGES):
            _LOGGER.info(f"{package_name} opted out of breaking changes checks. "
                        f"See http://aka.ms/azsdk/breaking-changes-tool to opt-in.")
            exit(0)

    if args.source_report:
        if not args.target_report:
            _LOGGER.exception("If providing the `--source-report` flag, the `--target-report` flag is also required.")
            exit(1)
    if args.target_report:
        if not args.source_report:
            _LOGGER.exception("If providing the `--target-report` flag, the `--source-report` flag is also required.")
            exit(1)

    in_venv = True if in_venv == "true" else False  # subprocess sends back string so convert to bool

    main(target_module, stable_version, in_venv, pkg_dir, changelog, args.code_report, args.latest_pypi_version, args.source_report, args.target_report)
