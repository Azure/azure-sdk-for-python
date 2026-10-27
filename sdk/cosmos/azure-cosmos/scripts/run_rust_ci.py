# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run required Cosmos Rust suites without the inherited emulator marker filter."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest

PACKAGE = Path(__file__).resolve().parents[1]

# Parameter cross-products deliberately contain cases that do not apply to one
# surface/backend. These exact existing reasons are not environment exemptions.
OFFLINE_SKIPS = {
    "common/test_container_backend_unit.py": {"A genuine initial 404 is the create branch, covered separately."},
    "common/test_container_metadata_unit.py": {"Async cancellation contract"},
    "common/test_list_containers_backend_unit.py": {
        "Rust-specific option rejection",
        "Rust-specific binding failure",
        "Legacy transport timeout checks are bypassed by the fake HTTP response",
    },
    "common/test_list_databases_telemetry_unit.py": {"Sync thread handoff", "Async cancellation"},
    "common/test_list_containers_telemetry_unit.py": {"Sync thread handoff", "Async cancellation"},
    "common/test_query_containers_backend_unit.py": {
        "Rust-specific option rejection",
        "Rust-specific binding failures",
        "Fake legacy transport does not enforce socket timeouts",
    },
    "common/test_read_container_backend_unit.py": {
        "Rust binding failures do not apply to explicit legacy selection",
        "Async Rust cancellation case",
    },
    "common/test_replace_container_backend_unit.py": {
        "Rust-specific eligibility",
        "Rust response mapping",
        "Rust binding failures",
    },
    "common/test_rust_telemetry_unit.py": {
        "Synchronous cross-thread consumption",
        "Async cancellation",
        "Async interruption",
        "No replacement step in a read",
        "Replacement boundary",
        "Replacement inputs",
        "Async task cancellation",
    },
    "read_item/test_read_item_contract_unit.py": {"Legacy validates the address in its transport preparation."},
    "read_all_items/test_read_all_items_contract_unit.py": {"async cancellation"},
    "test_change_feed_contract_unit.py": {"async cancellation"},
    "patch_item/test_patch_item_contract_unit.py": {"Async cancellation contract."},
}


def discover_tests(root: Path, suite: str) -> list[Path]:
    """Include new matching modules automatically, including unmarked parity tests.

    :param root: Package source directory.
    :type root: pathlib.Path
    :param suite: Offline or service-parity selection.
    :type suite: str
    :return: Required test module paths.
    :rtype: list[pathlib.Path]
    """
    tests = root / "tests"
    if suite == "offline":
        files = sorted(tests.rglob("test_*_unit.py"))
    else:
        files = sorted(
            path
            for path in tests.rglob("test_*.py")
            if not path.name.endswith("_unit.py")
            and path.relative_to(tests).parts[0] not in ("auth", "common")
            and ("parity" in path.stem or "legacy" in path.relative_to(tests).parts)
        )
        for surface in ("sync", "aio"):
            if not any(surface in path.relative_to(tests).parts for path in files):
                raise RuntimeError(f"Required {surface} parity suite is missing.")
    if not files:
        raise RuntimeError(f"No {suite} test modules found.")
    return files


def declared_tests(path: Path) -> set[str]:
    """Check method coverage independently of pytest's selection and name filters.

    :param path: Test module source.
    :type path: pathlib.Path
    :return: Declared test names, qualified by class where applicable.
    :rtype: set[str]
    """
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_"):
                    names.add(f"{node.name}::{method.name}")
    return names


class RequiredCoverage:
    """Fail selection gaps, unexpected skips, xfails and unfinished executions.

    :param files: Required test module paths.
    :type files: list[pathlib.Path]
    :param results: Directory for the coverage report.
    :type results: pathlib.Path
    :param expected_skips: Exact, file-scoped reasons for inapplicable parameter combinations.
    :type expected_skips: dict[pathlib.Path, set[str]] or None
    """

    def __init__(self, files: list[Path], results: Path, expected_skips: dict[Path, set[str]] | None = None):
        self.expected = {path.resolve(): declared_tests(path) for path in files}
        self.results = results
        self.selected: set[str] = set()
        self.file_ids: dict[Path, set[str]] = {}
        self.allowed_skips: dict[str, set[str]] = {}
        self.expected_skips = expected_skips or {}
        self.passed: set[str] = set()
        self.skipped: set[str] = set()
        self.errors: list[str] = []

    def pytest_deselected(self, items):
        self.errors.append(f"{len(items)} required tests were deselected.")

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_finish(self, session):
        observed: dict[Path, set[str]] = {}
        for item in session.items:
            path = Path(item.path).resolve()
            name = getattr(item, "originalname", None) or item.name.split("[", 1)[0]
            cls = getattr(item, "cls", None)
            if cls is not None:
                name = f"{cls.__name__}::{name}"
            observed.setdefault(path, set()).add(name)
            self.file_ids.setdefault(path, set()).add(item.nodeid)
            self.selected.add(item.nodeid)
            # Existing unconditional skips document intentionally unsupported contracts.
            # Environment-dependent skipif/importorskip never qualifies.
            reasons = {
                mark.kwargs["reason"] for mark in item.iter_markers("skip") if mark.kwargs.get("reason")
            } | self.expected_skips.get(path, set())
            if reasons:
                self.allowed_skips[item.nodeid] = reasons
        for path, names in self.expected.items():
            if path not in observed:
                self.errors.append(f"No tests collected from {path}.")
            elif names - observed[path]:
                self.errors.append(f"Missing tests in {path}: {sorted(names - observed[path])}")
        if not self.selected:
            self.errors.append("No required tests collected.")
        if self.errors:
            raise pytest.UsageError("\n".join(self.errors))

    def pytest_runtest_logreport(self, report):
        if hasattr(report, "wasxfail"):
            self.errors.append(f"Unexpected xfail/xpass: {report.nodeid}")
        elif report.skipped:
            self.skipped.add(report.nodeid)
            reason = report.longrepr[2].removeprefix("Skipped: ") if isinstance(report.longrepr, tuple) else ""
            if reason not in self.allowed_skips.get(report.nodeid, set()):
                self.errors.append(f"Unexpected skip: {report.nodeid}: {report.longrepr}")
        elif report.when == "call" and report.passed:
            self.passed.add(report.nodeid)

    def pytest_sessionfinish(self, session, exitstatus):
        if not session.config.option.collectonly:
            missing = self.selected - self.passed - self.skipped
            if missing:
                self.errors.append(f"{len(missing)} tests did not complete successfully.")
            if not self.passed:
                self.errors.append("No required test bodies passed.")
            for path in self.expected:
                file_ids = self.file_ids.get(path, set())
                if file_ids and file_ids.isdisjoint(self.passed):
                    self.errors.append(f"No test bodies passed in {path}.")
        summary = {
            "files": len(self.expected),
            "collected": len(self.selected),
            "passed": len(self.passed),
            "explicit_skips": sorted(self.skipped & self.allowed_skips.keys()),
            "errors": self.errors,
            "collection_only": session.config.option.collectonly,
            "pytest_exitstatus": int(exitstatus),
        }
        self.results.mkdir(parents=True, exist_ok=True)
        (self.results / "coverage.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        if self.errors:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
            reporter = session.config.pluginmanager.get_plugin("terminalreporter")
            if reporter:
                reporter.write_sep("=", "Required Rust coverage failed", red=True)
                for error in self.errors:
                    reporter.write_line(error, red=True)


def run_native(results: Path) -> int:
    """Run the actual test harness, not cargo build or cargo test --no-run.

    :param results: Directory for the Cargo transcript.
    :type results: pathlib.Path
    :return: Cargo's exit code, after checking successful runs for missing execution.
    :rtype: int
    """
    command = ["cargo", "test", "--workspace", "--locked", "--", "--test-threads=1"]
    results.mkdir(parents=True, exist_ok=True)
    with (results / "cargo-test.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, cwd=PACKAGE, stdout=log, stderr=subprocess.STDOUT, check=False)
    output = (results / "cargo-test.log").read_text(encoding="utf-8")
    print(output)
    if completed.returncode:
        return completed.returncode
    summaries = re.findall(
        r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; \d+ measured; (\d+) filtered out", output
    )
    if (
        not summaries
        or sum(int(row[0]) for row in summaries) == 0
        or any(int(row[1]) or int(row[3]) for row in summaries)
    ):
        raise RuntimeError("Cargo did not report an unfiltered, nonempty successful test run.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("offline", "parity", "native"))
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--require-installed-wheel", action="store_true")
    args = parser.parse_args()
    results = args.results.resolve()
    if args.suite == "native":
        if args.collect_only:
            parser.error("native coverage requires execution")
        return run_native(results)
    # Import before exposing the checkout for packaging-helper unit tests.
    native = importlib.import_module("azure.cosmos._rust")
    if args.require_installed_wheel and Path(native.__file__).resolve().is_relative_to(PACKAGE):
        raise RuntimeError("CI must load the installed wheel, not a checkout extension.")
    print(f"Native extension: {native.__file__}")
    if args.suite == "offline":
        importlib.import_module("opentelemetry.sdk.trace")
        importlib.import_module("azure.core.tracing.ext.opentelemetry_span")
    for variable in ("PYTEST_ADDOPTS", "COSMOS_PARITY_CAPTURE_BACKEND_LABEL"):
        if os.environ.get(variable):
            raise RuntimeError(f"Unset {variable}; required coverage cannot accept selection/label overrides.")
    if args.suite == "parity":
        if os.environ.get("COSMOS_BACKEND") != "rust":
            raise RuntimeError("The service lane requires COSMOS_BACKEND=rust.")
        if not os.environ.get("ACCOUNT_HOST") or not os.environ.get("ACCOUNT_KEY"):
            raise RuntimeError("The service lane requires emulator endpoint and key.")
    files = discover_tests(PACKAGE, args.suite)
    sys.path[:0] = [str(PACKAGE), str(PACKAGE / "tests")]
    os.chdir(PACKAGE)
    options = [
        *map(str, files),
        "--import-mode=importlib",
        "-o",
        "addopts=",
        "-m",
        "",
        "-k",
        "",
        "-p",
        "no:cacheprovider",
        f"--junitxml={results / 'pytest.xml'}",
    ]
    if args.collect_only:
        options.append("--collect-only")
    expected_skips = (
        {(PACKAGE / "tests" / name).resolve(): reasons for name, reasons in OFFLINE_SKIPS.items()}
        if args.suite == "offline"
        else {}
    )
    results.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="pytest-", dir=results) as temporary:
        options.append(f"--basetemp={temporary}")
        return int(pytest.main(options, plugins=[RequiredCoverage(files, results, expected_skips)]))


if __name__ == "__main__":
    sys.exit(main())
