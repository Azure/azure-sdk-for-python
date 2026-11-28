# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check that every test in this package is run by at least one CI pipeline.

A pipeline chooses tests in one of two ways: by file (the suites in
scripts/run_rust_ci.py) or by pytest marker (the --mark_arg expressions in
ci.yml, tests.yml and the templates they use). We call the tests a pipeline
runs its "CI selection". A test that no pipeline runs is allowed only if it
is listed in CI_SELECTION_GAPS with a reason; we call such a test a "gap".
"""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import warnings

import pytest
from _pytest.mark import MarkMatcher
from _pytest.mark.expression import Expression
import yaml

from common.sdk_subprocess import sdk_python_command

pytest_plugins = ["pytester"]
PACKAGE = Path(__file__).resolve().parents[2]

# Tests that no CI pipeline runs yet, each with the reason. These tests are not
# skipped; they are simply not run in CI.
_RERANKER_GAP = "environment-gap: no semanticReranker CI job with a configured inference service"
CI_SELECTION_GAPS = {
    "semantic_rerank/sync/test_semantic_reranker.py::TestSemanticReranker::test_semantic_reranker_rust": _RERANKER_GAP,
    "semantic_rerank/sync/test_semantic_reranker.py::TestSemanticReranker::test_semantic_reranker_json_documents_rust":
        _RERANKER_GAP,
    "semantic_rerank/sync/test_semantic_reranker.py::TestSemanticReranker::test_semantic_reranker_nested_json_documents_rust":
        _RERANKER_GAP,
    "semantic_rerank/aio/test_semantic_reranker_async.py::TestSemanticRerankerAsync::test_semantic_reranker_async_rust":
        _RERANKER_GAP,
    "semantic_rerank/aio/test_semantic_reranker_async.py::TestSemanticRerankerAsync::test_semantic_reranker_async_json_documents_rust":
        _RERANKER_GAP,
    "semantic_rerank/aio/test_semantic_reranker_async.py::TestSemanticRerankerAsync::test_semantic_reranker_async_nested_json_documents_rust":
        _RERANKER_GAP,
}


def _config_nodes(value):
    """Yield every dict inside a loaded YAML file, at any depth."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _config_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _config_nodes(child)


def _pipeline_selections():
    """Read ci.yml and tests.yml, follow the Cosmos templates they use, and return
    the test files and marker expressions that CI runs.

    The ``native`` suite is left out because it runs compiled-module tests, not
    pytest.
    """
    repository = PACKAGE.parents[2]
    pending = [PACKAGE.parent / "ci.yml", PACKAGE.parent / "tests.yml"]
    visited, expressions, suites = set(), set(), set()
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        for node in _config_nodes(yaml.safe_load(path.read_text(encoding="utf-8"))):
            if "TestMarkArgument" in node:
                expressions.add(node["TestMarkArgument"])
            for key in ("template", "Path"):
                reference = node.get(key, "").lstrip("/")
                if reference.startswith("sdk/cosmos/"):
                    pending.append(repository / reference)
            script = node.get("pwsh", "")
            expressions.update(re.findall(r"""--mark_arg=["']([^"']+)["']""", script))
            suites.update(re.findall(r"\brun_rust_ci\.py\s+(\w+)", script))
    spec = importlib.util.spec_from_file_location("selection_runner", PACKAGE / "scripts" / "run_rust_ci.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    files = {
        path.resolve()
        for suite in suites - {"native"}
        for path in runner.discover_tests(PACKAGE, suite)
    }
    assert files and expressions, "No configured CI selections found"
    return files, expressions


class SelectionAudit:
    """A pytest plugin that, after tests are collected, sorts each test into: run
    by CI, listed as a gap, or not run at all.

    If emulator job expressions are given, it also checks that each emulator test
    is in exactly one emulator job.
    """

    def __init__(self, root, files, expressions, gaps, emulator_expressions=()):
        self.root = root
        self.files = files
        self.expressions = [Expression.compile(expression) for expression in expressions]
        self.gaps = gaps
        self.emulator_expressions = [Expression.compile(expression) for expression in emulator_expressions]
        self.report = {}

    def pytest_collection_finish(self, session):
        selected, unselected, gaps = [], [], {}
        partition_errors = []
        partition_counts = [0] * len(self.emulator_expressions)
        for item in session.items:
            nodeid = item.path.relative_to(self.root).as_posix() + "::" + item.nodeid.split("::", 1)[1]
            nodeid_without_params = nodeid.split("[", 1)[0]
            matcher = MarkMatcher.from_markers(item.iter_markers())
            if self.emulator_expressions:
                matches = [expression.evaluate(matcher) for expression in self.emulator_expressions]
                expected = int(matcher("cosmosEmulator") and not (
                    matcher("cosmosToxiproxy") or matcher("cosmosRustProbes")
                ))
                if sum(matches) != expected:
                    partition_errors.append(f"{nodeid}: expected {expected} emulator category, got {sum(matches)}")
                partition_counts = [count + int(match) for count, match in zip(partition_counts, matches)]
            if item.path.resolve() in self.files or any(expression.evaluate(matcher) for expression in self.expressions):
                selected.append(nodeid)
            elif nodeid_without_params in self.gaps:
                gaps[nodeid] = self.gaps[nodeid_without_params]
            else:
                unselected.append(nodeid)
        observed_gaps = {nodeid.split("[", 1)[0] for nodeid in gaps}
        self.report = {
            "collected": len(session.items),
            "selected": len(selected),
            "unselected": sorted(unselected),
            "explicit_gaps": gaps,
            "stale_gaps": sorted(self.gaps.keys() - observed_gaps),
            "emulator_partition_errors": partition_errors,
            "emulator_partition_counts": partition_counts,
        }


def collect_ci_selection(report_path):
    """Collect every test in the package without running it, audit it against the
    CI selections, and write the result to ``report_path`` as JSON."""
    files, expressions = _pipeline_selections()
    template = yaml.safe_load((PACKAGE.parent / "templates" / "emulator-probe-tests.yml").read_text())
    emulator_expressions = [
        expression for step in template["steps"]
        for expression in re.findall(r'--mark_arg="([^"]+)"', step.get("pwsh", ""))
    ]
    assert len(emulator_expressions) == 2, "Functional and SDK fault-injection selections are required"
    audit = SelectionAudit(PACKAGE / "tests", files, expressions, CI_SELECTION_GAPS, emulator_expressions)
    exit_code = pytest.main([
        str(PACKAGE / "tests"), "--collect-only", "--import-mode=importlib",
        "-o", "addopts=", "-m", "", "-k", "", "-q", "-p", "no:cacheprovider",
    ], plugins=[audit])
    Path(report_path).write_text(json.dumps(audit.report, indent=2), encoding="utf-8")
    return int(exit_code)


def test_every_test_is_run_by_ci_or_listed_as_gap_rust(tmp_path):
    """Every test is run by a CI pipeline or listed as a gap.

    Gap entries for tests that now run or no longer exist must be removed. Each
    emulator test must be in exactly one of the two emulator jobs, and both jobs
    must run at least one test. Remaining gaps are shown as a warning.
    """
    report_path = tmp_path / "ci-selection.json"
    env = dict(os.environ)
    # Collect in a separate process with no extra pytest options, so this run's
    # settings do not change the result.
    env.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        sdk_python_command(
            "from common.test_ci_selection_unit import collect_ci_selection; "
            "raise SystemExit(collect_ci_selection(sys.argv[1]))",
            str(report_path),
        ),
        cwd=PACKAGE, env=env, capture_output=True, text=True, timeout=300, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["collected"] and report["selected"], report
    assert not report["unselected"], "No CI selection for:\n" + "\n".join(report["unselected"])
    assert not report["stale_gaps"], "Remove obsolete CI gap entries:\n" + "\n".join(report["stale_gaps"])
    assert not report["emulator_partition_errors"], "\n".join(report["emulator_partition_errors"])
    assert all(report["emulator_partition_counts"]), "Both emulator categories must select tests"
    if report["explicit_gaps"]:
        warnings.warn(
            pytest.PytestWarning("Uncovered CI cases:\n" + "\n".join(
                f"{nodeid}: {reason}" for nodeid, reason in report["explicit_gaps"].items()
            )),
            stacklevel=2,
        )


def test_audit_checks_each_test_not_just_each_file_rust(pytester):
    """A marker on a class applies to all its tests; a marker on one parameter
    applies to that case only.

    Here ``test_partial[2]`` has no marker, so it is reported as not run, even
    though ``test_partial[1]`` in the same function is run.
    """
    offline_file = pytester.makepyfile(test_offline="def test_without_marker(): pass")
    pytester.makepyfile(test_cases="""
        import pytest

        @pytest.mark.service
        class TestInherited:
            @pytest.mark.parametrize("value", [1, 2])
            def test_selected(self, value): pass

        @pytest.mark.parametrize("value", [pytest.param(1, marks=pytest.mark.service), 2])
        def test_partial(value): pass

        @pytest.mark.service
        @pytest.mark.excluded
        def test_excluded(): pass

        def test_gap(): pass
        def test_unowned(): pass
    """)
    gaps = {"test_cases.py::test_gap": "environment-gap: test environment unavailable"}
    audit = SelectionAudit(pytester.path, {offline_file.resolve()}, {"service and not excluded"}, gaps)
    result = pytester.runpytest_inprocess(
        "--collect-only", "--noconftest", "-q", plugins=[audit],
    )
    assert result.ret == 0
    assert audit.report["selected"] == 4
    assert audit.report["unselected"] == [
        "test_cases.py::test_excluded", "test_cases.py::test_partial[2]", "test_cases.py::test_unowned",
    ]
    assert audit.report["explicit_gaps"] == gaps
    assert audit.report["stale_gaps"] == []


def test_audit_reports_outdated_gap_entries_rust(pytester):
    """A gap entry is outdated if its test is now run by CI or no longer exists.
    Both kinds are reported."""
    offline_file = pytester.makepyfile(test_offline="def test_now_selected(): pass")
    gaps = {
        "test_offline.py::test_now_selected": "environment-gap: previously unavailable",
        "test_removed.py::test_deleted": "environment-gap: previously unavailable",
    }
    audit = SelectionAudit(pytester.path, {offline_file.resolve()}, set(), gaps)
    result = pytester.runpytest_inprocess("--collect-only", "--noconftest", "-q", plugins=[audit])
    assert result.ret == 0
    assert audit.report["selected"] == 1
    assert audit.report["stale_gaps"] == sorted(gaps)


@pytest.mark.parametrize("fault_expression,errors", [
    ("cosmosEmulator and cosmosSdkFaultInjection", 0),
    ("cosmosEmulator", 2),
    ("never_selected", 1),
])
def test_each_emulator_test_is_in_exactly_one_emulator_job_rust(pytester, fault_expression, errors):
    """Each emulator test must be in exactly one emulator job.

    Network-fault (``cosmosToxiproxy``) and special-build (``cosmosRustProbes``)
    tests are in neither. A fault-injection expression that also picks functional
    and network-fault tests gives 2 errors; one that picks nothing gives 1 error.
    """
    pytester.makepyfile(test_cases="""
        import pytest
        @pytest.mark.cosmosEmulator
        def test_functional(): pass
        @pytest.mark.cosmosEmulator
        @pytest.mark.cosmosSdkFaultInjection
        def test_fault(): pass
        @pytest.mark.cosmosEmulator
        @pytest.mark.cosmosToxiproxy
        def test_network(): pass
        @pytest.mark.cosmosRustProbes
        def test_cancellation(): pass
    """)
    audit = SelectionAudit(pytester.path, set(), set(), {}, [
        "cosmosEmulator and not cosmosSdkFaultInjection and not cosmosToxiproxy",
        fault_expression,
    ])
    result = pytester.runpytest_inprocess("--collect-only", "--noconftest", "-q", plugins=[audit])
    assert result.ret == 0
    assert len(audit.report["emulator_partition_errors"]) == errors
    if not errors:
        assert audit.report["emulator_partition_counts"] == [1, 1]
