# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run required Cosmos Rust suites without the inherited emulator marker filter."""

from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
# Header line that opts a standalone sync/aio Rust test module into the service lane.
RUST_BEHAVIOR_TEST_MARKER = "# Rust behavior test"
TOXIPROXY_CASE_COUNTS = {
    "test_toxiproxy_route.py": 32,
    "test_toxiproxy_write.py": 8,
    "test_toxiproxy_reset_socket.py": 6,
}
TELEMETRY_MODULES = (
    "telemetry/test_rust_telemetry_unit.py",
    "telemetry/test_tracing_settings_unit.py",
    "telemetry/test_rust_azure_export_unit.py",
    "telemetry/test_rust_failure_proof_unit.py",
    "common/test_list_databases_telemetry_unit.py",
    "common/test_list_containers_telemetry_unit.py",
    "execute_item_batch/test_batch_telemetry_unit.py",
    "read_all_items/test_read_all_items_telemetry_unit.py",
    "query_items/test_query_items_telemetry_unit.py",
    "test_change_feed_telemetry_unit.py",
)
_COLLECTION_SPEC = importlib.util.spec_from_file_location(
    "_cosmos_test_collection",
    PACKAGE / "tests" / "config" / "collection.py",
)
test_collection = importlib.util.module_from_spec(_COLLECTION_SPEC)
_COLLECTION_SPEC.loader.exec_module(test_collection)

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
    "common/test_list_containers_telemetry_unit.py": {
        "Sync thread handoff",
        "Async cancellation",
        "Synchronous nested listing in a synchronous hook",
    },
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
    "telemetry/test_rust_telemetry_unit.py": {
        "Synchronous cross-thread consumption",
        "Async cancellation",
        "Async interruption",
        "No replacement step in a read",
        "Replacement boundary",
        "Replacement inputs",
        "Async task cancellation",
    },
    "execute_item_batch/test_batch_telemetry_unit.py": {
        "Synchronous nested batch inside a synchronous hook",
        "Async cancellation",
    },
    "read_all_items/test_read_all_items_telemetry_unit.py": {
        "Synchronous nested fetch in a synchronous hook",
        "Async cancellation",
    },
    "query_items/test_query_items_telemetry_unit.py": {
        "Synchronous nested query inside a synchronous hook",
        "Async cancellation",
    },
    "test_change_feed_telemetry_unit.py": {
        "Synchronous nested poll inside a synchronous hook",
        "Async cancellation",
    },
    "read_item/test_read_item_contract_unit.py": {"Legacy validates the address in its transport preparation."},
    "read_all_items/test_read_all_items_contract_unit.py": {"async cancellation"},
    "test_change_feed_contract_unit.py": {"async cancellation"},
    "patch_item/test_patch_item_contract_unit.py": {"Async cancellation contract."},
}


def discover_tests(root: Path, suite: str) -> list[Path]:
    """Include maintained matching modules, excluding local-only originals and comparisons.

    :param root: Package source directory.
    :type root: pathlib.Path
    :param suite: Offline, telemetry, Toxiproxy, or service selection (CLI name parity).
    :type suite: str
    :return: Required test module paths.
    :rtype: list[pathlib.Path]
    """
    tests = root / "tests"
    if suite == "toxiproxy":
        files = [tests / "toxiproxy" / name for name in TOXIPROXY_CASE_COUNTS]
        for path in files:
            if not path.is_file():
                raise RuntimeError(f"Required Toxiproxy module is missing: {path}")
    elif suite == "telemetry":
        files = [tests / name for name in TELEMETRY_MODULES]
        for path in files:
            if not path.is_file():
                raise RuntimeError(f"Required telemetry module is missing: {path}")
        files = sorted(set(files) | set((tests / "telemetry").rglob("test_*_unit.py")))
    elif suite == "offline":
        files = sorted(
            path for path in tests.rglob("test_*_unit.py") if not test_collection.exclude_module(path, tests_root=tests)
        )
    else:
        files = sorted(
            path
            for path in tests.rglob("test_*.py")
            if not path.name.endswith("_unit.py")
            and not test_collection.exclude_module(path, tests_root=tests)
            and path.relative_to(tests).parts[0] not in ("auth", "common")
            and (
                "parity" in path.stem
                or (
                    path.parent.name in ("sync", "aio")
                    and any(
                        line.lstrip().startswith(("# Source:", RUST_BEHAVIOR_TEST_MARKER))
                        for line in path.read_text(encoding="utf-8").splitlines()
                    )
                )
            )
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
            if not test_collection.exclude_test(path, node.name):
                names.add(node.name)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_"):
                    if not test_collection.exclude_test(path, method.name):
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

    def __init__(
        self,
        files: list[Path],
        results: Path,
        expected_skips: dict[Path, set[str]] | None = None,
        *,
        required_case_counts: dict[Path, int] | None = None,
        allow_declared_skips: bool = True,
    ):
        self.expected = {path.resolve(): declared_tests(path) for path in files}
        self.results = results
        self.selected: set[str] = set()
        self.file_ids: dict[Path, set[str]] = {}
        self.allowed_skips: dict[str, set[str]] = {}
        self.expected_skips = expected_skips or {}
        self.passed: set[str] = set()
        self.skipped: set[str] = set()
        self.errors: list[str] = []
        self.required_case_counts = {path.resolve(): count for path, count in (required_case_counts or {}).items()}
        self.allow_declared_skips = allow_declared_skips

    def pytest_deselected(self, items):
        unexpected = [
            item
            for item in items
            if not test_collection.exclude_parameters(
                item.path,
                getattr(getattr(item, "callspec", None), "params", {}),
            )
        ]
        if unexpected:
            self.errors.append(f"{len(unexpected)} required tests were deselected.")

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
            reasons = (
                {mark.kwargs["reason"] for mark in item.iter_markers("skip") if mark.kwargs.get("reason")}
                if self.allow_declared_skips
                else set()
            ) | self.expected_skips.get(path, set())
            if reasons:
                self.allowed_skips[item.nodeid] = reasons
        for path, names in self.expected.items():
            if path not in observed:
                self.errors.append(f"No tests collected from {path}.")
            elif names - observed[path]:
                self.errors.append(f"Missing tests in {path}: {sorted(names - observed[path])}")
        if not self.selected:
            self.errors.append("No required tests collected.")
        for path, count in self.required_case_counts.items():
            observed_count = len(self.file_ids.get(path, set()))
            if observed_count != count:
                self.errors.append(f"Expected {count} cases in {path}, collected {observed_count}.")
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


def run_toxiproxy_worker(results, native):
    """Own the whole network-test process tree, including timed-out proxy servers."""
    from toxiproxy._process_tree import run_owned_worker
    from toxiproxy._toxiproxy_config import digest

    state = {}
    results.mkdir(parents=True, exist_ok=True)
    record = {
        "native_extension": str(native.__file__),
        "native_sha256": digest(Path(native.__file__)),
        "driver_commit": native.__rust_driver_commit__,
    }
    try:
        with (results / "live.txt").open("w", encoding="utf-8") as log:
            status = run_owned_worker(
                [sys.executable, "-I", str(Path(__file__).resolve()), *sys.argv[1:], "--toxiproxy-worker"],
                cwd=PACKAGE,
                env=os.environ.copy(),
                log=log,
                state=state,
            )
        record["exit_code"] = status
        print((results / "live.txt").read_text(encoding="utf-8"))
        return status
    except subprocess.TimeoutExpired:
        record["outer_timeout"] = True
        raise
    finally:
        (results / "run.json").write_text(json.dumps({**record, **state}, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("offline", "parity", "native", "toxiproxy", "telemetry"))
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--require-installed-wheel", action="store_true")
    parser.add_argument("--toxiproxy-worker", action="store_true", help=argparse.SUPPRESS)
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
    if args.suite in ("offline", "telemetry"):
        importlib.import_module("opentelemetry.sdk.trace")
        importlib.import_module("azure.core.tracing.ext.opentelemetry_span")
    if args.suite == "telemetry":
        importlib.import_module("azure.monitor.opentelemetry.exporter")
    if os.environ.get("PYTEST_ADDOPTS"):
        raise RuntimeError("Unset PYTEST_ADDOPTS; required coverage cannot accept selection overrides.")
    if args.toxiproxy_worker:
        if args.suite != "toxiproxy" or sys.stdin.buffer.read(1) != b"1":
            raise RuntimeError("Runner did not establish Toxiproxy process-tree ownership.")
    if args.suite in ("parity", "toxiproxy"):
        if os.environ.get("COSMOS_BACKEND") != "rust":
            raise RuntimeError("The service lane requires COSMOS_BACKEND=rust.")
        if not os.environ.get("ACCOUNT_HOST") or not os.environ.get("ACCOUNT_KEY"):
            raise RuntimeError("The service lane requires emulator endpoint and key.")
    files = discover_tests(PACKAGE, args.suite)
    sys.path[:0] = [str(PACKAGE), str(PACKAGE / "tests")]
    if args.suite == "toxiproxy":
        from toxiproxy._toxiproxy_config import DRIVER_COMMIT, validate_endpoint, verify_server

        if sys.platform != "win32":
            raise RuntimeError("The required Toxiproxy lane uses the Windows emulator.")
        validate_endpoint(os.environ["ACCOUNT_HOST"])
        verify_server(os.environ.get("TOXIPROXY_SERVER", ""))
        if native.__rust_driver_commit__ != DRIVER_COMMIT:
            raise RuntimeError("Toxiproxy requires the pinned Rust driver build.")
        if not args.toxiproxy_worker:
            if args.collect_only:
                parser.error("required Toxiproxy coverage requires execution")
            return run_toxiproxy_worker(results, native)
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
    if args.suite == "toxiproxy":
        options.extend(
            [
                "--confcutdir=" + str(PACKAGE / "tests" / "toxiproxy"),
                "-o",
                "junit_logging=all",
                "-o",
                "junit_log_passing_tests=true",
            ]
        )
    expected_skips = (
        {(PACKAGE / "tests" / name).resolve(): reasons for name, reasons in OFFLINE_SKIPS.items()}
        if args.suite in ("offline", "telemetry")
        else {}
    )
    results.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="pytest-", dir=results) as temporary:
        options.append(f"--basetemp={temporary}")
        counts = (
            {PACKAGE / "tests" / "toxiproxy" / name: count for name, count in TOXIPROXY_CASE_COUNTS.items()}
            if args.suite == "toxiproxy"
            else {}
        )
        return int(
            pytest.main(
                options,
                plugins=[
                    RequiredCoverage(
                        files,
                        results,
                        expected_skips,
                        required_case_counts=counts,
                        allow_declared_skips=args.suite not in ("toxiproxy", "telemetry"),
                    )
                ],
            )
        )


if __name__ == "__main__":
    sys.exit(main())
