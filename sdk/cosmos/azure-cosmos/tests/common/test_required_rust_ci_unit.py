# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise the required-lane guard with real pytest collection and reports."""

import ast
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

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


@pytest.mark.parametrize("extra_name", ["test_new_coverage_unit.py", "nested/test_new_coverage_unit.py"])
def test_telemetry_discovery_requires_shared_and_operation_modules_rust(tmp_path, extra_name):
    for name in runner.TELEMETRY_MODULES:
        path = tmp_path / "tests" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_case(): pass\n", encoding="utf-8")
    extra = tmp_path / "tests" / "telemetry" / extra_name
    extra.parent.mkdir(parents=True, exist_ok=True)
    extra.write_text("def test_added(): pass\n", encoding="utf-8")
    other_paths = {
        tmp_path / "tests" / name
        for name in (
            "common/test_other_unit.py",
            "common/test_telemetry_helper_unit.py",
            "fault_injection/test_fault_unit.py",
        )
    }
    for path in other_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_case(): pass\n", encoding="utf-8")
    paths = runner.discover_tests(tmp_path, "telemetry")
    assert {path.relative_to(tmp_path / "tests").as_posix() for path in paths} == {
        *runner.TELEMETRY_MODULES,
        f"telemetry/{extra_name}",
    }
    offline = set(runner.discover_tests(tmp_path, "offline"))
    assert offline == other_paths
    assert offline.isdisjoint(paths)
    (tmp_path / "tests" / runner.TELEMETRY_MODULES[0]).unlink()
    with pytest.raises(RuntimeError, match="Required telemetry module"):
        runner.discover_tests(tmp_path, "telemetry")
    assert set(runner.discover_tests(tmp_path, "offline")) == other_paths


def test_offline_and_telemetry_partition_maintained_unit_inventory_rust():
    tests = PACKAGE / "tests"
    maintained = {
        path for path in tests.rglob("test_*_unit.py") if not runner.test_collection.exclude_module(path, tests_root=tests)
    }
    offline = set(runner.discover_tests(PACKAGE, "offline"))
    telemetry = set(runner.discover_tests(PACKAGE, "telemetry"))
    assert offline.isdisjoint(telemetry)
    assert offline | telemetry == maintained


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
            return SimpleNamespace(
                __file__=str(tmp_path / "installed" / "_rust.pyd"),
                **{probe: Mock() for probe in runner.DEBUG_PROBE_EXPORTS},
            )
        if name == missing:
            raise ModuleNotFoundError(f"No module named {name}")
        return SimpleNamespace()

    monkeypatch.setattr(runner.importlib, "import_module", import_module)
    with pytest.raises(ModuleNotFoundError, match=missing):
        runner.main()


@pytest.mark.parametrize("suite", ["offline", "telemetry"])
@pytest.mark.parametrize("declared", [False, True])
def test_telemetry_lane_rejects_offline_skip_allowances_rust(tmp_path, monkeypatch, suite, declared):
    module = "telemetry/test_skip_unit.py"
    test = tmp_path / "tests" / module
    test.parent.mkdir(parents=True)
    test.write_text(
        "import pytest\n"
        + (
            "@pytest.mark.skip(reason='Async cancellation')\ndef test_skipped(): pass\n"
            if declared
            else "def test_skipped(): pytest.skip('Async cancellation')\n"
        )
        + "def test_control(): pass\n",
        encoding="utf-8",
    )
    results = tmp_path / "results"
    native = SimpleNamespace(
        __file__=str(tmp_path / "_rust.pyd"),
        **{probe: Mock() for probe in runner.DEBUG_PROBE_EXPORTS},
    )
    monkeypatch.setattr(runner, "PACKAGE", tmp_path)
    monkeypatch.setattr(runner, "OFFLINE_SKIPS", {module: {"Async cancellation"}})
    monkeypatch.setattr(runner, "discover_tests", lambda root, selected: [test])
    monkeypatch.setattr(runner, "importlib", SimpleNamespace(import_module=Mock(return_value=native)))
    monkeypatch.setattr(runner.sys, "argv", ["run_rust_ci.py", suite, "--results", str(results)])
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.chdir(tmp_path)
    pytest_main = pytest.main
    monkeypatch.setattr(
        runner.pytest,
        "main",
        lambda args, plugins: pytest_main([*args, "--noconftest", "-q"], plugins=plugins),
    )

    status = runner.main()
    report = json.loads((results / "coverage.json").read_text(encoding="utf-8"))
    assert status == (pytest.ExitCode.TESTS_FAILED if suite == "telemetry" else pytest.ExitCode.OK)
    assert report["passed"] == 1
    assert any("Unexpected skip" in error for error in report["errors"]) == (suite == "telemetry")


@pytest.mark.parametrize(
    "platform,suite,module,reason,accepted",
    [
        ("linux", "offline", "toxiproxy/test_toxiproxy_local_unit.py", "Windows process-tree ownership", True),
        ("darwin", "offline", "toxiproxy/test_toxiproxy_local_unit.py", "Windows process-tree ownership", True),
        ("win32", "offline", "toxiproxy/test_toxiproxy_local_unit.py", "Windows process-tree ownership", False),
        ("freebsd", "offline", "toxiproxy/test_toxiproxy_local_unit.py", "Windows process-tree ownership", False),
        ("linux", "telemetry", "toxiproxy/test_toxiproxy_local_unit.py", "Windows process-tree ownership", False),
        ("linux", "offline", "toxiproxy/test_toxiproxy_local_unit.py", "missing dependency", False),
        ("linux", "offline", "common/test_other_unit.py", "Windows process-tree ownership", False),
    ],
)
def test_offline_windows_skip_allowance_is_platform_suite_file_and_reason_scoped_rust(
    tmp_path, monkeypatch, platform, suite, module, reason, accepted
):
    test = tmp_path / "tests" / module
    test.parent.mkdir(parents=True)
    test.write_text(
        "import pytest\n"
        f"@pytest.mark.skipif(True, reason={reason!r})\ndef test_platform_case(): pass\n"
        "def test_control(): pass\n",
        encoding="utf-8",
    )
    results = tmp_path / "results"
    native = SimpleNamespace(
        __file__=str(tmp_path / "_rust.pyd"),
        **{probe: Mock() for probe in runner.DEBUG_PROBE_EXPORTS},
    )
    monkeypatch.setattr(runner, "PACKAGE", tmp_path)
    monkeypatch.setattr(runner, "discover_tests", lambda root, selected: [test])
    monkeypatch.setattr(runner, "importlib", SimpleNamespace(import_module=Mock(return_value=native)))
    # Model the runner's OS without changing pytest's host-platform behavior.
    monkeypatch.setattr(runner.sys, "argv", ["run_rust_ci.py", suite, "--results", str(results)])
    monkeypatch.setattr(
        runner, "sys",
        SimpleNamespace(platform=platform, path=list(runner.sys.path)),
    )
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    monkeypatch.chdir(tmp_path)
    pytest_main = pytest.main
    # Distinct import names prevent earlier nested runs from supplying cached test bodies.
    monkeypatch.setattr(
        runner.pytest, "main",
        lambda args, plugins: pytest_main(
            [*args, "--noconftest", "-q", f"--rootdir={tmp_path.parent}"], plugins=plugins
        ),
    )

    status = runner.main()
    report = json.loads((results / "coverage.json").read_text(encoding="utf-8"))
    assert status == (pytest.ExitCode.OK if accepted else pytest.ExitCode.TESTS_FAILED)
    assert report["passed"] == 1
    if accepted:
        assert len(report["explicit_skips"]) == 1
    assert any("Unexpected skip" in error for error in report["errors"]) == (not accepted)


def test_telemetry_without_eager_task_factory_runs_supported_cases_rust(pytester):
    pytester.makepyfile(
        "import asyncio\n"
        "import sys\n"
        f"sys.path.insert(0, {str(PACKAGE / 'tests')!r})\n"
        "if hasattr(asyncio, 'eager_task_factory'):\n"
        "    del asyncio.eager_task_factory\n"
        "from telemetry.test_rust_telemetry_unit import (\n"
        "    item_harness, recording_setup,\n"
        "    test_patch_deadline_authorizes_only_its_worker_rust,\n"
        ")\n"
    )
    result = pytester.runpytest_subprocess("--noconftest", "-q", "-o", "addopts=")
    result.assert_outcomes(passed=2, skipped=0)
    assert result.ret == pytest.ExitCode.OK


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
        "test_native_listing_accepts_remaining_duration_rust",
    }


def test_offline_inventory_excludes_core_python_tests_rust():
    files = runner.discover_tests(PACKAGE, "offline")
    legacy = PACKAGE / "tests" / "common" / "test_core_python_backend_unit.py"
    assert legacy not in files
    reads = PACKAGE / "tests" / "read_database"
    assert reads / "test_read_database_backend_unit.py" in files
    assert reads / "test_read_database_legacy_unit.py" not in files
    containers = PACKAGE / "tests" / "common"
    assert containers / "test_container_backend_unit.py" in files
    assert containers / "test_container_legacy_unit.py" not in files


def test_required_guard_allows_only_explicit_core_python_parameter_exclusions_rust(tmp_path):
    path = PACKAGE / "tests" / "create_item" / "sync" / "test_input_variants.py"
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
    commands = []

    def execute(command, **kwargs):
        commands.append(command)
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
    if exitcode:
        assert len(commands) == 1
    elif passed and not filtered:
        assert commands[1:] == [
            ["cargo", "test", "--workspace", "--locked", "--no-default-features", "--", "--test-threads=1"],
            [
                "cargo", "test", "--workspace", "--locked", "--no-default-features",
                "--features", "azure_cosmos_rust/test-probes",
                "--", "--test-threads=1",
            ],
        ]
        assert {path.name for path in tmp_path.iterdir()} == {
            "cargo-clippy.log", "cargo-test.log", "cargo-test-probes.log"
        }


def test_native_runner_exposes_interpreter_import_paths_rust(tmp_path, monkeypatch):
    dependencies = tmp_path / "venv dependencies"
    dependencies.mkdir()
    (dependencies / "native_test_dependency.py").write_text("VALUE = 42\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner.sys, "path", ["", dependencies.name, *runner.sys.path])
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "unrelated"))
    monkeypatch.setenv("COSMOS_NATIVE_TEST_ENV", "preserved")
    original_environment = os.environ.copy()
    run = subprocess.run
    commands = []

    def execute(command, **kwargs):
        commands.append(command)
        environment = kwargs.get("env", os.environ)
        result = run(
            [
                runner.sys.executable,
                "-S",
                "-c",
                "import native_test_dependency; assert native_test_dependency.VALUE == 42",
            ],
            cwd=kwargs["cwd"],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert "" not in environment["PYTHONPATH"].split(os.pathsep)
        assert environment["COSMOS_NATIVE_TEST_ENV"] == "preserved"
        kwargs["stdout"].write("test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    assert runner.run_native(tmp_path / "results") == 0
    assert [command[1] for command in commands] == ["clippy", "test", "test"]
    assert os.environ == original_environment


@pytest.mark.parametrize("variant,expected_commands", [
    ("default", ["clippy", "test"]),
    ("probes", ["test"]),
])
@pytest.mark.parametrize("exitcode", [0, 1])
def test_native_variants_run_only_their_feature_set_rust(tmp_path, monkeypatch, variant, expected_commands, exitcode):
    commands = []

    def execute(command, **kwargs):
        commands.append(command)
        kwargs["stdout"].write("test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;\n")
        return SimpleNamespace(returncode=exitcode if command[1] == "test" else 0)

    monkeypatch.setattr(runner.subprocess, "run", execute)
    assert runner.run_native(tmp_path, variant) == exitcode
    assert [command[1] for command in commands] == expected_commands
    assert "--no-default-features" in commands[-1]
    assert ("--features" in commands[-1]) == (variant == "probes")
    if variant == "probes":
        assert "azure_cosmos_rust/test-probes" in commands[-1]


@pytest.mark.parametrize("variant", ["default", "probes"])
def test_native_variant_cli_reaches_runner_rust(tmp_path, monkeypatch, variant):
    execute = Mock(return_value=7)
    monkeypatch.setattr(runner, "run_native", execute)
    monkeypatch.setattr(runner.sys, "argv", [
        "run_rust_ci.py", "native", "--native-variant", variant, "--results", str(tmp_path),
    ])
    assert runner.main() == 7
    execute.assert_called_once_with(tmp_path.resolve(), variant)


def test_cancellation_lane_rejects_extension_without_probe_rust(tmp_path, monkeypatch):
    import azure.cosmos

    native = SimpleNamespace(
        __file__=str(tmp_path / "_rust.pyd"),
        **{probe: Mock() for probe in runner.DEBUG_PROBE_EXPORTS},
    )
    monkeypatch.setattr(azure.cosmos, "_rust", native)
    monkeypatch.setitem(runner.sys.modules, "azure.cosmos._rust", native)
    monkeypatch.setattr(
        runner.sys, "argv",
        ["run_rust_ci.py", "cancellation", "--require-installed-wheel", "--results", str(tmp_path / "results")],
    )
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    monkeypatch.setenv("COSMOS_BACKEND", "rust")
    monkeypatch.setenv("ACCOUNT_HOST", "https://localhost:8081/")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    pytest_main = Mock(return_value=0)
    monkeypatch.setattr(runner.pytest, "main", pytest_main)
    with pytest.raises(RuntimeError):
        runner.main()
    pytest_main.assert_not_called()


def test_cancellation_lane_requires_both_end_to_end_cases_rust():
    files = runner.discover_tests(PACKAGE, "cancellation")
    assert files == [PACKAGE / "tests" / "fault_injection" / "aio" / "test_async_cancellation_fault.py"]
    assert runner.declared_tests(files[0]) == {"test_cancelled_read_drops_native_future_and_client_recovers_rust"}
    # Cancellation stays separate from the emulator suite even with a probe wheel.
    tree = ast.parse(files[0].read_text(encoding="utf-8"))
    marks = {
        node.value.attr
        for node in tree.body
        if isinstance(node, ast.Assign) and [target.id for target in node.targets] == ["pytestmark"]
    }
    assert marks == {"cosmosRustProbes"}


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


def test_toxiproxy_lane_accepts_current_driver_revision_rust(tmp_path, monkeypatch):
    import azure.cosmos
    from toxiproxy import _toxiproxy_config

    native = SimpleNamespace(
        __file__=str(tmp_path / "_rust.pyd"), __rust_driver_commit__="unit-test-revision",
        **{probe: Mock() for probe in runner.DEBUG_PROBE_EXPORTS},
    )
    monkeypatch.setattr(azure.cosmos, "_rust", native)
    monkeypatch.setitem(runner.sys.modules, "azure.cosmos._rust", native)
    monkeypatch.setattr(runner.sys, "path", list(runner.sys.path))
    monkeypatch.setattr(runner.sys, "platform", "win32")
    results = tmp_path / "results"
    monkeypatch.setattr(
        runner.sys, "argv",
        ["run_rust_ci.py", "toxiproxy", "--require-installed-wheel", "--results", str(results)],
    )
    monkeypatch.delenv("PYTEST_ADDOPTS", raising=False)
    monkeypatch.setenv("COSMOS_BACKEND", "rust")
    monkeypatch.setenv("ACCOUNT_HOST", "https://localhost:8081/")
    monkeypatch.setenv("ACCOUNT_KEY", "unit-test-key")
    monkeypatch.setenv("TOXIPROXY_SERVER", str(tmp_path / "toxiproxy.exe"))
    monkeypatch.setattr(runner, "discover_tests", Mock(return_value=[]))
    verify = Mock()
    monkeypatch.setattr(_toxiproxy_config, "verify_server", verify)
    execute = Mock(return_value=0)
    monkeypatch.setattr(runner, "run_toxiproxy_worker", execute)
    assert runner.main() == 0
    verify.assert_called_once_with(str(tmp_path / "toxiproxy.exe"))
    execute.assert_called_once_with(results, native)


@pytest.mark.parametrize("pipeline", ["ci.yml", "tests.yml", "templates/emulator-probe-tests.yml"])
def test_pipeline_preserves_unicode_failure_output_rust(pipeline):
    repository = PACKAGE.parents[2]
    config = yaml.safe_load((repository / "sdk" / "cosmos" / pipeline).read_text())
    if "extends" in config:
        environment = config["extends"]["parameters"].get("EnvVars", {})
    else:
        step = next(step for step in config["steps"] if "dispatch_checks.py" in step.get("pwsh", ""))
        environment = step["env"]
    # Model Windows redirected output even when this test runs on another OS.
    env = {**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}
    if "PYTHONIOENCODING" in environment:
        env["PYTHONIOENCODING"] = environment["PYTHONIOENCODING"]
    result = subprocess.run(
        [runner.sys.executable, "-c", r"print('\U0001f4a5 source build failed')"],
        env=env, capture_output=True, check=True,
    )
    assert result.stdout.decode("utf-8").strip() == "\U0001f4a5 source build failed"


@pytest.mark.parametrize("checks", ["whl,sdist", "import_all,whl_no_aio", "latestdependency"])
def test_internal_emulator_matrix_covers_public_python_versions_rust(checks):
    public = yaml.safe_load(
        (PACKAGE.parent / "cosmos-emulator-public-matrix.json").read_text()
    )["matrix"]["EmulatorConfig"]
    internal = yaml.safe_load(
        (PACKAGE.parent / "cosmos-emulator-internal-matrix.json").read_text()
    )["matrix"]["EmulatorConfig"]
    expected_versions = sorted({job["PythonVersion"] for job in public.values()})
    actual_versions = sorted(
        job["PythonVersion"] for job in internal.values() if job["ChecksOverride"] == checks
    )
    assert actual_versions == expected_versions


def test_pipeline_wires_toxiproxy_through_existing_central_hook_rust():
    repository = PACKAGE.parents[2]
    ci = yaml.safe_load((repository / "sdk" / "cosmos" / "ci.yml").read_text())
    assert ci["extends"]["template"] == "/eng/pipelines/templates/stages/archetype-sdk-client.yml"
    parameters = ci["extends"]["parameters"]
    assert parameters["TestMarkArgument"] == "cosmosCustomerWheel"
    assert parameters["BeforeTestSteps"][0]["template"].endswith("/prepare-test-probes.yml")
    assert parameters["BeforeTestSteps"][1]["template"].endswith("/cosmos-emulator.yml")
    assert parameters["AfterTestSteps"] == [
        {"template": "/sdk/cosmos/templates/emulator-probe-tests.yml"},
        {"template": "/sdk/cosmos/templates/rust-tests.yml"},
        {"template": "/sdk/cosmos/templates/telemetry-tests.yml"},
        {"template": "/sdk/cosmos/templates/toxiproxy-tests.yml"},
    ]
    archetype = (repository / "eng/pipelines/templates/stages/archetype-sdk-client.yml").read_text()
    assert "AfterTestSteps: ${{ parameters.AfterTestSteps }}" in archetype
    template = (repository / "sdk/cosmos/templates/toxiproxy-tests.yml").read_text()
    assert "continueOnError" not in template
    assert "--collect-only" not in template
    assert "--require-installed-wheel" in template
    assert "failTaskOnMissingResultsFile: true" in template
    assert "_toxiproxy_config.py --install" in template
    assert "run_rust_ci.py toxiproxy" in template
    assert "uploadLlmArtifacts" in template
    assert "llm-artifacts/cosmos-toxiproxy" in template


@pytest.mark.parametrize(
    "template",
    ["rust-tests.yml", "rust-native-tests.yml", "rust-offline-tests.yml", "telemetry-tests.yml", "toxiproxy-tests.yml"],
)
def test_supplemental_checks_run_on_every_standard_python_job_rust(template):
    config = yaml.safe_load((PACKAGE.parent / "templates" / template).read_text())
    condition = (
        "and(succeededOrFailed(), eq(variables['Agent.OS'], 'Windows_NT'), "
        "eq(variables['ChecksOverride'], 'whl,sdist'))"
    )
    if template in ("rust-native-tests.yml", "rust-offline-tests.yml", "telemetry-tests.yml"):
        assert config["parameters"] == [{"name": "Condition", "type": "string", "default": condition}]
        condition = "${{ parameters.Condition }}"
    for step in config["steps"]:
        if "template" in step:
            assert step in [
                {"template": "/sdk/cosmos/templates/rust-native-tests.yml"},
                {"template": "/sdk/cosmos/templates/rust-offline-tests.yml"},
            ]
            continue
        assert step["condition"] == condition, step["displayName"]


def test_live_supplemental_checks_select_one_linux_and_one_macos_job_rust():
    live = yaml.safe_load((PACKAGE.parent / "tests.yml").read_text())["extends"]["parameters"]
    native, bash, offline, telemetry, publish, publish_telemetry = live["PostSteps"]
    condition = (
        "and(succeededOrFailed(), in(variables['Agent.OS'], 'Linux', 'Darwin'), "
        "eq(variables['CosmosRunSupplementalTests'], 'true'))"
    )
    assert native == {
        "template": "/sdk/cosmos/templates/rust-native-tests.yml",
        "parameters": {"Condition": condition},
    }
    assert bash["condition"] == (
        "and(succeededOrFailed(), eq(variables['Agent.OS'], 'Darwin'), "
        "eq(variables['CosmosRunSupplementalTests'], 'true'))"
    )
    script = bash["pwsh"]
    assert "$PSNativeCommandUseErrorActionPreference = $true" in script
    assert script.index("brew install bash") < script.index("brew --prefix bash")
    assert script.index("[[ -v value ]]") < script.index("##vso[task.prependpath]$bashDirectory")
    assert bash["env"] == {"HOMEBREW_NO_AUTO_UPDATE": "1"}
    assert offline == {
        "template": "/sdk/cosmos/templates/rust-offline-tests.yml",
        "parameters": {"Condition": condition},
    }
    assert telemetry == {
        "template": "/sdk/cosmos/templates/telemetry-tests.yml",
        "parameters": {"Condition": condition},
    }
    assert publish["condition"] == condition
    assert publish["task"] == "1ES.PublishPipelineArtifact@1"
    assert publish["inputs"] == {
        "targetPath": "$(Build.ArtifactStagingDirectory)/llm-artifacts/cosmos-rust",
        "artifactName": "cosmos-rust-supplemental-$(System.JobId)-$(System.JobAttempt)",
    }
    assert publish_telemetry["condition"] == condition
    assert publish_telemetry["task"] == "1ES.PublishPipelineArtifact@1"
    assert publish_telemetry["inputs"] == {
        "targetPath": "$(Build.ArtifactStagingDirectory)/llm-artifacts/cosmos-telemetry",
        "artifactName": "cosmos-telemetry-$(System.JobId)-$(System.JobAttempt)",
    }
    selected = []
    for matrix in live["MatrixConfigs"] + live["FixedAccountMatrixConfigs"]:
        config = json.loads((PACKAGE.parents[2] / matrix["Path"]).read_text())
        for group in config["include"]:
            for jobs in group.values():
                selected.extend(job for job in jobs.values() if job.get("CosmosRunSupplementalTests") == "true")
    assert sorted((job["OSVmImage"], job["PythonVersion"]) for job in selected) == [
        ("env:LINUXVMIMAGE", "3.10"),
        ("env:MACVMIMAGE", "3.11"),
    ]
    # Supplemental checks must use a hook the live job actually invokes.
    job = (PACKAGE.parents[2] / "eng/pipelines/templates/jobs/live.tests.yml").read_text()
    assert "- ${{ parameters.PostSteps }}" in job


def test_supplemental_rust_checks_reuse_existing_standard_test_jobs_rust():
    repository = PACKAGE.parents[2]
    ci = yaml.safe_load((repository / "sdk" / "cosmos" / "ci.yml").read_text())
    parameters = ci["extends"]["parameters"]
    assert parameters["TestMarkArgument"] == "cosmosCustomerWheel"
    assert parameters["TestTimeoutInMinutes"] == 240
    template = (repository / "sdk/cosmos/templates/rust-tests.yml").read_text()
    parsed = yaml.safe_load(template)
    assert set(parsed) == {"steps"}
    assert "install-msrust-toolchain.yml" not in template
    assert all("checkout" not in step for step in parsed["steps"])
    assert all(step.get("task") != "DownloadPipelineArtifact@2" for step in parsed["steps"])
    assert "use-python-version.yml" not in template
    assert "cosmos-emulator.yml" not in template
    assert "run_rust_ci.py parity" not in template
    assert "continueOnError" not in template
    assert "--collect-only" not in template


def test_supplemental_rust_checks_require_built_wheel_and_save_results_rust():
    repository = PACKAGE.parents[2]
    parsed = yaml.safe_load((repository / "sdk/cosmos/templates/rust-tests.yml").read_text())
    prepare, native_template, offline_template, cancellation, publish_cancellation = parsed["steps"]
    assert native_template == {"template": "/sdk/cosmos/templates/rust-native-tests.yml"}
    assert offline_template == {"template": "/sdk/cosmos/templates/rust-offline-tests.yml"}
    native, native_probes = yaml.safe_load(
        (PACKAGE.parent / "templates" / "rust-native-tests.yml").read_text()
    )["steps"]
    offline, publish = yaml.safe_load(
        (PACKAGE.parent / "templates" / "rust-offline-tests.yml").read_text()
    )["steps"]
    results = "$(Build.ArtifactStagingDirectory)/llm-artifacts/cosmos-rust"
    assert results in prepare["pwsh"]
    assert "uploadLlmArtifacts" in prepare["pwsh"]
    assert "$PSNativeCommandUseErrorActionPreference = $true" in prepare["pwsh"]
    assert "$(CosmosProbePython)" in prepare["pwsh"]
    assert "$env:PYO3_PYTHON = '$(CosmosProbePython)'" in native["pwsh"]
    assert "run_rust_ci.py native" in native["pwsh"]
    assert f"--results '{results}/native'" in native["pwsh"]
    assert "exit $LASTEXITCODE" in native["pwsh"]
    assert "--native-variant default" in native["pwsh"]
    assert "--native-variant probes" in native_probes["pwsh"]
    assert f"--results '{results}/native'" in native_probes["pwsh"]
    assert "$env:PYO3_PYTHON = '$(CosmosProbePython)'" in native_probes["pwsh"]
    assert "exit $LASTEXITCODE" in native_probes["pwsh"]
    build = yaml.safe_load(
        (PACKAGE.parent / "templates" / "prepare-test-probes.yml").read_text()
    )["steps"][-1]
    assert native["env"] == native_probes["env"] == build["env"]
    assert "run_rust_ci.py offline" in offline["pwsh"]
    assert "--require-installed-wheel" in offline["pwsh"]
    assert f"--results '{results}/offline'" in offline["pwsh"]
    assert "exit $LASTEXITCODE" in offline["pwsh"]
    assert offline["env"] == {
        "APPLICATIONINSIGHTS_CONNECTION_STRING": "",
        "COSMOSDBCONNECTIONSTRING": "",
    }
    assert publish["task"] == "PublishTestResults@2"
    assert publish["inputs"]["testResultsFiles"] == f"{results}/offline/pytest.xml"
    assert publish["inputs"]["failTaskOnFailedTests"] is True
    assert publish["inputs"]["failTaskOnMissingResultsFile"] is True
    script = cancellation["pwsh"]
    assert "$(CosmosProbePython)" in script
    assert "maturin build" not in script
    assert "run_rust_ci.py cancellation" in script and "--require-installed-wheel" in script
    assert f"$results = '{results}/cancellation'" in script
    assert cancellation["env"]["COSMOS_BACKEND"] == "rust"
    assert cancellation["env"]["ACCOUNT_HOST"] == "https://localhost:8081/"
    assert publish_cancellation["inputs"]["testResultsFiles"] == f"{results}/cancellation/pytest.xml"
    assert publish_cancellation["inputs"]["failTaskOnFailedTests"] is True
    assert publish_cancellation["inputs"]["failTaskOnMissingResultsFile"] is True


def test_probe_wheels_stay_out_of_customer_artifacts_and_keep_emulator_coverage_rust():
    repository = PACKAGE.parents[2]
    template = yaml.safe_load(
        (repository / "sdk/cosmos/templates/prepare-test-probes.yml").read_text()
    )
    install, build = template["steps"]
    assert install["template"].endswith("/install-msrust-toolchain.yml")
    script = build["pwsh"]
    assert "$wheelDirectory = '$(Agent.TempDirectory)/cosmos-test-probes-wheels'" in script
    tool_path = '$env:PATH = "$(Split-Path -Parent $python)$([IO.Path]::PathSeparator)$env:PATH"'
    assert script.index("$python = ") < script.index(tool_path) < script.index("pip wheel")
    assert "pip wheel . --no-deps --no-build-isolation" in script
    assert "maturin.build-args=--features test-probes --locked" in script
    assert "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR = $nativeAssets" in script
    assert "install --no-deps --force-reinstall $wheels[0].FullName" in script
    assert "task.setvariable variable=CosmosProbePython" in script
    assert "task.setvariable variable=CosmosProbeWheelDirectory" in script
    preserve, customer_publish, emulator, functional_publish, faults, faults_publish = yaml.safe_load(
        (repository / "sdk/cosmos/templates/emulator-probe-tests.yml").read_text()
    )["steps"]
    assert "customer-wheel" in preserve["pwsh"]
    assert customer_publish["inputs"]["failTaskOnMissingResultsFile"] is True
    assert 'dispatch_checks.py azure-cosmos' in emulator["pwsh"]
    assert '--wheel_dir="$(CosmosProbeWheelDirectory)"' in emulator["pwsh"]
    assert '--mark_arg="cosmosEmulator and not cosmosSdkFaultInjection and not cosmosToxiproxy and not cosmosRustProbes"' in emulator["pwsh"]
    assert '--checks="$(ChecksOverride)"' in emulator["pwsh"]
    assert "--max-parallel=1" in emulator["pwsh"]
    assert emulator["env"]["COSMOS_REQUIRE_TEST_PROBES"] == "1"
    assert emulator["env"]["MATURIN_PEP517_ARGS"] == "--features test-probes"
    assert emulator["condition"] == "succeededOrFailed()"
    for step, publish, folder in (
        (emulator, functional_publish, "emulator-functional"),
        (faults, faults_publish, "sdk-fault-injection"),
    ):
        script = step["pwsh"]
        assert "$status = $LASTEXITCODE" in script and "exit $status" in script
        assert script.index("Remove-Item") < script.index("dispatch_checks.py") < script.index("Copy-Item")
        assert "$PSNativeCommandUseErrorActionPreference = $false" in script
        assert "--max-parallel=1" in script
        assert step["env"] == emulator["env"]
        assert step["condition"] == "succeededOrFailed()"
        assert f"/{folder}/test-junit-*.xml" in publish["inputs"]["testResultsFiles"]
        assert publish["inputs"]["failTaskOnFailedTests"] is True
        assert publish["inputs"]["failTaskOnMissingResultsFile"] is True
    assert "Where-Object { $_ -ne 'import_all' }" in faults["pwsh"]
    assert '--checks="$checks"' in faults["pwsh"]
    assert '--mark_arg="cosmosEmulator and cosmosSdkFaultInjection and not cosmosToxiproxy and not cosmosRustProbes"' in faults["pwsh"]
    live = yaml.safe_load((repository / "sdk/cosmos/tests.yml").read_text())["extends"]["parameters"]
    # The existing live-job template actually invokes PreSteps, not BeforeTestSteps.
    assert live["PreSteps"][-1]["template"].endswith("/prepare-test-probes.yml")
    assert live["AdditionalTestArgs"] == '--wheel_dir="$(CosmosProbeWheelDirectory)"'


@pytest.mark.parametrize("suite", ["offline", "parity", "toxiproxy"])
@pytest.mark.parametrize("missing", runner.DEBUG_PROBE_EXPORTS)
def test_probe_lanes_reject_missing_debug_exports_before_running_tests_rust(tmp_path, monkeypatch, suite, missing):
    native = SimpleNamespace(
        __file__=str(tmp_path / "_rust.pyd"),
        **{name: Mock() for name in runner.DEBUG_PROBE_EXPORTS if name != missing},
    )
    monkeypatch.setattr(runner.importlib, "import_module", Mock(return_value=native))
    monkeypatch.setattr(runner.sys, "argv", ["run_rust_ci.py", suite, "--results", str(tmp_path)])
    execute = Mock()
    monkeypatch.setattr(runner.pytest, "main", execute)
    with pytest.raises(RuntimeError, match=f"test-probes.*{missing}"):
        runner.main()
    execute.assert_not_called()


@pytest.mark.parametrize("required", [False, True])
@pytest.mark.parametrize("instrumented", [False, True])
def test_standard_pytest_lane_enforces_probe_build_only_when_requested_rust(monkeypatch, required, instrumented):
    import azure.cosmos

    spec = importlib.util.spec_from_file_location("_probe_conftest_under_test", PACKAGE / "tests" / "conftest.py")
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    native = SimpleNamespace()
    if instrumented:
        native._AsyncOperationProbe = Mock()
        native._debug_operation_count = Mock()
    monkeypatch.setattr(azure.cosmos, "_rust", native)
    if required:
        monkeypatch.setenv("COSMOS_REQUIRE_TEST_PROBES", "1")
    else:
        monkeypatch.delenv("COSMOS_REQUIRE_TEST_PROBES", raising=False)
    if required and not instrumented:
        with pytest.raises(pytest.UsageError, match="--features test-probes"):
            plugin.pytest_sessionstart(None)
    else:
        plugin.pytest_sessionstart(None)


def test_pipeline_telemetry_installs_dependencies_and_runs_offline_rust():
    repository = PACKAGE.parents[2]
    template = (repository / "sdk/cosmos/templates/telemetry-tests.yml").read_text()
    parsed = yaml.safe_load(template)
    script, publish = parsed["steps"]
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
