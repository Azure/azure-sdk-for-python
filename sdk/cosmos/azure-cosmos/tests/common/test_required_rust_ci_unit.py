# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise the required-lane guard with real pytest collection and reports."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

pytest_plugins = ["pytester"]
PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("run_rust_ci", PACKAGE / "scripts" / "run_rust_ci.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def run_guard(pytester, source, *args, extra_expected=(), skip_reasons=()):
    test = pytester.makepyfile(test_required=source)
    results = pytester.path / "results"
    guard = runner.RequiredCoverage([test, *extra_expected], results, {test.resolve(): set(skip_reasons)})
    outcome = pytester.runpytest_inprocess("--noconftest", "-p", "no:cacheprovider", *args, str(test), plugins=[guard])
    report = json.loads((results / "coverage.json").read_text(encoding="utf-8"))
    return outcome, report


def test_required_collection_and_execution_rust(pytester):
    outcome, report = run_guard(pytester, "def test_present(): pass")
    assert outcome.ret == 0
    assert report["collected"] == report["passed"] == 1
    assert report["errors"] == []


@pytest.mark.parametrize("selection", [("-k", "one"), ("-m", "cosmosEmulator")])
def test_partial_or_zero_selection_fails_rust(pytester, selection):
    outcome, report = run_guard(pytester, "def test_one(): pass\n\ndef test_two(): pass", *selection)
    assert outcome.ret != 0
    assert any("deselected" in error for error in report["errors"])


def test_missing_module_fails_rust(pytester):
    absent = pytester.makepyfile(test_absent="def test_lost(): pass")
    outcome, report = run_guard(pytester, "def test_present(): pass", extra_expected=[absent])
    assert outcome.ret != 0
    assert any("No tests collected" in error for error in report["errors"])


def test_missing_method_fails_even_with_other_tests_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "def test_one(): pass\n\ndef test_two(): pass",
        "-o",
        "python_functions=test_one",
    )
    assert outcome.ret != 0
    assert any("Missing tests" in error for error in report["errors"])


@pytest.mark.parametrize(
    "source",
    [
        "import pytest\n@pytest.mark.skipif(True, reason='missing binding')\ndef test_missing(): pass",
        "import pytest\ndef test_missing(): pytest.skip('no emulator')",
        "import pytest\n@pytest.mark.xfail(reason='hidden regression')\ndef test_missing(): assert False",
        "import pytest\npytest.importorskip('deliberately_absent_cosmos_dependency')",
    ],
)
def test_environment_skips_and_xfails_fail_rust(pytester, source):
    outcome, report = run_guard(pytester, source)
    assert outcome.ret != 0
    assert report["errors"]


def test_documented_skip_is_reported_but_not_a_pass_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "import pytest\n"
        "@pytest.mark.skip(reason='API deliberately excludes this option')\n"
        "def test_excluded(): pass\n"
        "def test_supported(): pass",
    )
    assert outcome.ret == 0
    assert report["passed"] == 1
    assert len(report["explicit_skips"]) == 1


def test_all_explicitly_skipped_is_not_green_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "import pytest\n@pytest.mark.skip(reason='disabled')\ndef test_disabled(): pass",
    )
    assert outcome.ret != 0
    assert report["passed"] == 0


@pytest.mark.parametrize("reason,expected_exit", [("Async cancellation", 0), ("missing binding", 1)])
def test_runtime_skip_requires_exact_reviewed_reason_rust(pytester, reason, expected_exit):
    outcome, report = run_guard(
        pytester,
        f"import pytest\ndef test_case(): pytest.skip({reason!r})\ndef test_other(): pass",
        skip_reasons=("Async cancellation",),
    )
    assert bool(outcome.ret) == bool(expected_exit)
    assert bool(report["errors"]) == bool(expected_exit)


def test_interrupted_execution_fails_rust(pytester):
    outcome, report = run_guard(pytester, "def test_first(): assert False\n\ndef test_second(): pass", "-x")
    assert outcome.ret != 0
    assert any("did not complete" in error for error in report["errors"])


def test_parameterized_cases_are_all_required_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "import pytest\n@pytest.mark.parametrize('number', [1, 2, 3])\ndef test_cases(number): assert number > 0",
    )
    assert outcome.ret == 0
    assert report["passed"] == 3


def test_collection_only_is_explicit_not_execution_rust(pytester):
    outcome, report = run_guard(pytester, "def test_present(): pass", "--collect-only")
    assert outcome.ret == 0
    assert report["collection_only"] is True
    assert report["passed"] == 0


def test_discovery_covers_unmarked_parity_copies_and_offline_rust(tmp_path):
    paths = [
        "tests/common/test_governance_unit.py",
        "tests/read_item/sync/test_read_item_parity.py",
        "tests/read_item/aio/legacy/test_crud.py",
        "tests/read_item/aio/test_read_item_unit.py",
        "tests/auth/test_aad_parity.py",
        "tests/test_crud.py",
    ]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("def test_case(): pass", encoding="utf-8")
    parity = runner.discover_tests(tmp_path, "parity")
    offline = runner.discover_tests(tmp_path, "offline")
    assert {path.relative_to(tmp_path).as_posix() for path in parity} == set(paths[1:3])
    assert {path.relative_to(tmp_path).as_posix() for path in offline} == {paths[0], paths[3]}


def test_empty_discovery_fails_rust(tmp_path):
    with pytest.raises(RuntimeError, match="No offline"):
        runner.discover_tests(tmp_path, "offline")
    with pytest.raises(RuntimeError, match="sync parity"):
        runner.discover_tests(tmp_path, "parity")


@pytest.mark.parametrize("passed,filtered,exitcode", [(2, 0, 0), (0, 0, 0), (2, 1, 0), (2, 0, 1)])
def test_native_runner_requires_actual_unfiltered_tests_rust(tmp_path, monkeypatch, passed, filtered, exitcode):
    def execute(command, **kwargs):
        assert command == ["cargo", "test", "--workspace", "--locked", "--", "--test-threads=1"]
        assert kwargs["cwd"] == PACKAGE
        kwargs["stdout"].write(
            f"test result: ok. {passed} passed; 0 failed; 2 ignored; 0 measured; {filtered} filtered out;\n"
        )
        return SimpleNamespace(returncode=exitcode)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    if not exitcode and (not passed or filtered):
        with pytest.raises(RuntimeError, match="unfiltered, nonempty"):
            runner.run_native(tmp_path)
    else:
        assert runner.run_native(tmp_path) == exitcode


def test_pipeline_wires_required_jobs_without_marker_filters_rust():
    repository = PACKAGE.parents[2]
    ci = yaml.safe_load((repository / "sdk" / "cosmos" / "ci.yml").read_text())
    assert ci["extends"]["parameters"]["RunRustTests"] is True
    cosmos = (repository / "eng/pipelines/templates/stages/cosmos-sdk-client.yml").read_text()
    archetype = (repository / "eng/pipelines/templates/stages/archetype-sdk-client.yml").read_text()
    assert "AdditionalJobs:" in cosmos and "/sdk/cosmos/templates/rust-tests.yml" in cosmos
    assert "- ${{ parameters.AdditionalJobs }}" in archetype
    template = (repository / "sdk/cosmos/templates/rust-tests.yml").read_text()
    parsed = yaml.safe_load(template)
    lanes = next(parameter["default"] for parameter in parsed["parameters"] if parameter["name"] == "Lanes")
    assert {lane["suite"] for lane in lanes} == {"offline", "parity"}
    assert "continueOnError" not in template
    assert "--collect-only" not in template
    assert "--require-installed-wheel" in template
    assert "failTaskOnMissingResultsFile: true" in template
