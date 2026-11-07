# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise the required-lane guard with real pytest collection and reports."""

import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

pytest_plugins = ["pytester"]
PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("run_rust_ci", PACKAGE / "scripts" / "run_rust_ci.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def run_guard(pytester, source, *args, extra_expected=(), skip_reasons=(), strict=False, expected_count=None):
    test = pytester.makepyfile(test_required=source)
    results = pytester.path / "results"
    guard = runner.RequiredCoverage(
        [test, *extra_expected],
        results,
        {test.resolve(): set(skip_reasons)},
        required_case_counts={} if expected_count is None else {test: expected_count},
        allow_declared_skips=not strict,
    )
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
@pytest.mark.parametrize("strict", [False, True])
def test_runtime_skip_requires_exact_reviewed_reason_rust(pytester, reason, expected_exit, strict):
    outcome, report = run_guard(
        pytester,
        f"import pytest\ndef test_case(): pytest.skip({reason!r})\ndef test_other(): pass",
        skip_reasons=("Async cancellation",),
        strict=strict,
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


def test_network_lane_rejects_missing_parameter_combinations_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "import pytest\n@pytest.mark.parametrize('n', [1, 2])\ndef test_cases(n): pass",
        expected_count=3,
        strict=True,
    )
    assert outcome.ret != 0
    assert any("Expected 3 cases" in error for error in report["errors"])


def test_network_lane_rejects_even_explicit_skips_rust(pytester):
    outcome, report = run_guard(
        pytester,
        "import pytest\n@pytest.mark.skip(reason='disabled')\ndef test_disabled(): pass\n" "def test_control(): pass",
        strict=True,
        expected_count=2,
    )
    assert outcome.ret != 0
    assert any("Unexpected skip" in error for error in report["errors"])


def test_network_discovery_requires_all_three_modules_rust(tmp_path):
    folder = tmp_path / "tests" / "toxiproxy"
    folder.mkdir(parents=True)
    for name in runner.TOXIPROXY_CASE_COUNTS:
        (folder / name).write_text("def test_case(): pass\n", encoding="utf-8")
    assert {path.name for path in runner.discover_tests(tmp_path, "toxiproxy")} == set(runner.TOXIPROXY_CASE_COUNTS)
    assert sorted(runner.TOXIPROXY_CASE_COUNTS.values()) == [6, 8, 32]
    (folder / "test_toxiproxy_write.py").unlink()
    with pytest.raises(RuntimeError, match="Required Toxiproxy module"):
        runner.discover_tests(tmp_path, "toxiproxy")


def test_telemetry_discovery_requires_shared_and_operation_modules_rust(tmp_path):
    for name in runner.TELEMETRY_MODULES:
        path = tmp_path / "tests" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_case(): pass\n", encoding="utf-8")
    extra = tmp_path / "tests" / "telemetry" / "test_new_coverage_unit.py"
    extra.write_text("def test_added(): pass\n", encoding="utf-8")
    paths = runner.discover_tests(tmp_path, "telemetry")
    assert {path.relative_to(tmp_path / "tests").as_posix() for path in paths} == {
        *runner.TELEMETRY_MODULES,
        "telemetry/test_new_coverage_unit.py",
    }
    assert set(paths) <= set(runner.discover_tests(tmp_path, "offline"))
    (tmp_path / "tests" / runner.TELEMETRY_MODULES[0]).unlink()
    with pytest.raises(RuntimeError, match="Required telemetry module"):
        runner.discover_tests(tmp_path, "telemetry")


@pytest.mark.parametrize(
    "missing",
    [
        "opentelemetry.sdk.trace",
        "azure.core.tracing.ext.opentelemetry_span",
        "azure.monitor.opentelemetry.exporter",
    ],
)
def test_telemetry_dependencies_are_required_before_collection_rust(tmp_path, monkeypatch, missing):
    monkeypatch.setattr(
        runner.sys,
        "argv",
        [
            "run_rust_ci.py",
            "telemetry",
            "--require-installed-wheel",
            "--results",
            str(tmp_path),
        ],
    )

    def import_module(name):
        if name == "azure.cosmos._rust":
            return SimpleNamespace(__file__=str(tmp_path / "installed" / "_rust.pyd"))
        if name == missing:
            raise ModuleNotFoundError(f"No module named {name}")
        return SimpleNamespace()

    monkeypatch.setattr(runner.importlib, "import_module", import_module)
    with pytest.raises(ModuleNotFoundError, match=missing):
        runner.main()


def test_collection_only_is_explicit_not_execution_rust(pytester):
    outcome, report = run_guard(pytester, "def test_present(): pass", "--collect-only")
    assert outcome.ret == 0
    assert report["collection_only"] is True
    assert report["passed"] == 0


def test_discovery_covers_unmarked_parity_copies_and_offline_rust(tmp_path):
    paths = [
        "tests/common/test_governance_unit.py",
        "tests/binding/test_binding_contract_parity.py",
        "tests/read_item/aio/test_crud.py",
        "tests/read_item/aio/test_read_item_unit.py",
        "tests/auth/test_aad_parity.py",
        "tests/test_crud.py",
        "tests/read_item/sync/core_python/test_crud.py",
        "tests/read_item/sync/test_neighbor.py",
    ]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("def test_case(): pass", encoding="utf-8")
    (tmp_path / paths[2]).write_text(
        "def test_case():\n    # Source: tests/test_crud.py::test_case\n    pass\n",
        encoding="utf-8",
    )
    (tmp_path / paths[6]).write_text(
        "def test_case():\n    # Source: tests/test_crud.py::test_case\n    pass\n",
        encoding="utf-8",
    )
    (tmp_path / paths[7]).write_text('"""Mentions # Source: without a provenance comment."""\n', encoding="utf-8")
    sync_copy = tmp_path / "tests" / "read_item" / "sync" / "test_crud.py"
    sync_copy.write_text(
        "def test_case():\n    # Source: tests/test_crud.py::test_case\n    pass\n",
        encoding="utf-8",
    )
    original_unit = tmp_path / "tests" / "test_partition_split_retry_unit.py"
    original_unit.write_text("def test_case(): pass\n", encoding="utf-8")
    parity = runner.discover_tests(tmp_path, "parity")
    offline = runner.discover_tests(tmp_path, "offline")
    assert {path.relative_to(tmp_path).as_posix() for path in parity} == {
        paths[1],
        paths[2],
        sync_copy.relative_to(tmp_path).as_posix(),
    }
    assert {path.relative_to(tmp_path).as_posix() for path in offline} == {paths[0], paths[3]}


def test_discovery_includes_rust_behavior_modules_by_header_rust(tmp_path):
    marker = runner.RUST_BEHAVIOR_TEST_MARKER
    files = {
        "tests/list_containers/sync/test_list_containers_paging.py": f"{marker}\ndef test_case(): pass\n",
        "tests/list_containers/aio/test_list_containers_paging_async.py": f"{marker}\ndef test_case(): pass\n",
        "tests/list_containers/test_list_containers_root.py": f"{marker}\ndef test_case(): pass\n",
        "tests/list_containers/sync/test_mentions_marker.py": f'"""Mentions {marker} in prose."""\n',
    }
    for name, text in files.items():
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
    service = runner.discover_tests(tmp_path, "parity")
    assert {path.relative_to(tmp_path).as_posix() for path in service} == set(list(files)[:2])


def test_required_inventory_matches_default_exclusions_rust():
    for suite in ("offline", "parity", "telemetry"):
        files = runner.discover_tests(PACKAGE, suite)
        assert all(not runner.test_collection.exclude_module(path) for path in files)
    mixed = PACKAGE / "tests" / "binding" / "test_binding_contract_parity.py"
    assert runner.declared_tests(mixed) == {
        "test_binding_rejects_invalid_timeout_with_real_handle",
    }


def test_offline_inventory_keeps_shared_backend_contracts_not_legacy_rust():
    files = runner.discover_tests(PACKAGE, "offline")
    shared = PACKAGE / "tests" / "common" / "test_backend_contract_unit.py"
    legacy = PACKAGE / "tests" / "common" / "test_legacy_backend_unit.py"
    assert shared in files
    assert legacy not in files
    assert runner.declared_tests(shared) == {
        "TestBackendContract::test_operation_routing_is_frozen_rust",
        "TestBackendContract::test_backend_execution_errors_never_replay_rust",
        "TestBackendContract::test_async_backend_execution_errors_never_replay_rust",
    }


def test_required_guard_allows_only_explicit_legacy_parameter_exclusions_rust(tmp_path):
    path = PACKAGE / "tests" / "create_item" / "sync" / "test_legacy_variants.py"
    guard = runner.RequiredCoverage([path], tmp_path)
    legacy = SimpleNamespace(path=path, callspec=SimpleNamespace(params={"backend": "core-python"}))
    rust = SimpleNamespace(path=path, callspec=SimpleNamespace(params={"backend": "rust"}))
    guard.pytest_deselected([legacy])
    assert guard.errors == []
    guard.pytest_deselected([rust])
    assert guard.errors == ["1 required tests were deselected."]


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


@pytest.mark.parametrize("outcome", [0, 7, "timeout"])
def test_network_worker_preserves_required_arguments_and_failure_evidence_rust(tmp_path, monkeypatch, outcome):
    from toxiproxy import _process_tree
    from toxiproxy._toxiproxy_config import digest

    extension = tmp_path / "_rust.pyd"
    extension.write_bytes(b"unit-test binary")
    native = SimpleNamespace(__file__=str(extension), __rust_driver_commit__="unit-test-revision")
    results = tmp_path / "results"
    arguments = ["toxiproxy", "--require-installed-wheel", "--results", str(results)]
    monkeypatch.setattr(runner.sys, "argv", [str(PACKAGE / "scripts" / "run_rust_ci.py"), *arguments])

    def owned_worker(command, *, cwd, env, log, state):
        assert command == [
            runner.sys.executable,
            "-I",
            str(Path(runner.__file__).resolve()),
            *arguments,
            "--toxiproxy-worker",
        ]
        assert cwd == PACKAGE
        assert env is not runner.os.environ
        log.write("worker evidence\n")
        state.update(worker_pid=123, process_tree_stopped=True)
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(command, 600)
        return outcome

    monkeypatch.setattr(_process_tree, "run_owned_worker", owned_worker)
    if outcome == "timeout":
        with pytest.raises(subprocess.TimeoutExpired):
            runner.run_toxiproxy_worker(results, native)
    else:
        assert runner.run_toxiproxy_worker(results, native) == outcome
    record = json.loads((results / "run.json").read_text())
    assert record["native_sha256"] == digest(extension)
    assert record["driver_commit"] == native.__rust_driver_commit__
    assert record["process_tree_stopped"] is True
    if outcome == "timeout":
        assert record["outer_timeout"] is True and "exit_code" not in record
    else:
        assert record["exit_code"] == outcome
    assert (results / "live.txt").read_text() == "worker evidence\n"


def test_pipeline_wires_toxiproxy_through_existing_central_hook_rust():
    repository = PACKAGE.parents[2]
    ci = yaml.safe_load((repository / "sdk" / "cosmos" / "ci.yml").read_text())
    assert ci["extends"]["template"] == "/eng/pipelines/templates/stages/archetype-sdk-client.yml"
    parameters = ci["extends"]["parameters"]
    assert parameters["TestMarkArgument"] == "cosmosEmulator"
    assert parameters["BeforeTestSteps"][0]["template"].endswith("/cosmos-emulator.yml")
    assert parameters["AfterTestSteps"] == [
        {"template": "/sdk/cosmos/templates/telemetry-tests.yml"},
        {"template": "/sdk/cosmos/templates/toxiproxy-tests.yml"},
    ]
    archetype = (repository / "eng/pipelines/templates/stages/archetype-sdk-client.yml").read_text()
    assert "AfterTestSteps: ${{ parameters.AfterTestSteps }}" in archetype
    template = (repository / "sdk/cosmos/templates/toxiproxy-tests.yml").read_text()
    parsed = yaml.safe_load(template)
    for step in parsed["steps"]:
        assert "Windows_NT" in step["condition"]
        assert "'3.13'" in step["condition"] and "'whl,sdist'" in step["condition"]
    assert "continueOnError" not in template
    assert "--collect-only" not in template
    assert "--require-installed-wheel" in template
    assert "failTaskOnMissingResultsFile: true" in template
    assert "_toxiproxy_config.py --install" in template
    assert "run_rust_ci.py toxiproxy" in template
    assert "uploadLlmArtifacts" in template
    assert "llm-artifacts/cosmos-toxiproxy" in template


def test_pipeline_telemetry_installs_dependencies_and_runs_offline_rust():
    repository = PACKAGE.parents[2]
    template = (repository / "sdk/cosmos/templates/telemetry-tests.yml").read_text()
    parsed = yaml.safe_load(template)
    script, publish = parsed["steps"]
    for step in (script, publish):
        assert "Windows_NT" in step["condition"]
        assert "'3.13'" in step["condition"] and "'whl,sdist'" in step["condition"]
    assert "-r dev_requirements.txt -r samples/requirements-telemetry.txt" in script["pwsh"]
    assert "run_rust_ci.py telemetry" in script["pwsh"]
    assert "--require-installed-wheel" in script["pwsh"]
    assert "Tee-Object" in script["pwsh"] and "live.txt" in script["pwsh"]
    assert "uploadLlmArtifacts" in script["pwsh"]
    assert script["env"]["APPLICATIONINSIGHTS_CONNECTION_STRING"] == ""
    assert script["env"]["COSMOSDBCONNECTIONSTRING"] == ""
    assert "--azure-monitor" not in template
    assert "--collect-only" not in template
    assert "continueOnError" not in template
    assert publish["inputs"]["failTaskOnFailedTests"] is True
    assert publish["inputs"]["failTaskOnMissingResultsFile"] is True
    assert "cosmos-telemetry/pytest.xml" in publish["inputs"]["testResultsFiles"]
