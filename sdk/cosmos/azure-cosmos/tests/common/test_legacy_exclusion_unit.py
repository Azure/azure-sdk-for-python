# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep originals available locally without collecting them in normal runs."""

import ast
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from config import collection


@pytest.mark.parametrize("relative", [
    "test_crud.py",
    "test_crud_async.py",
    "test_config.py",
    "test_partition_split_retry_unit.py",
    "test_partition_split_scenarios.py",
    "test_partition_split_scenarios_async.py",
    "common/test_legacy_backend_unit.py",
    "patch_item/sync/core_python/test_headers.py",
    "patch_item/aio/core_python/test_headers.py",
    "read_item/sync/test_read_item_parity.py",
    "get_latest_session_token/test_session_token_backend_parity.py",
])
def test_original_and_comparison_modules_are_excluded_rust(relative):
    assert collection.exclude_module(collection.TESTS_ROOT / relative)


@pytest.mark.parametrize("relative", [
    "test_aio_extras_packaging_unit.py",
    "test_change_feed_contract_unit.py",
    "test_change_feed_telemetry_unit.py",
    "test_cosmos_paged_unit.py",
    "test_point_operation_response_hook_parity_unit.py",
    "test_future_rust_unit.py",
    "read_item/sync/test_crud.py",
    "read_item/aio/test_crud_async.py",
    "get_latest_session_token/sync/test_latest_session_token.py",
    "get_latest_session_token/aio/test_latest_session_token_async.py",
    "common/test_parity_helpers_unit.py",
    "common/test_backend_contract_unit.py",
    "common/test_legacy_migration_enforcer_unit.py",
    "config/settings.py",
    "conftest.py",
])
def test_maintained_modules_are_not_excluded_by_name_rust(relative):
    path = collection.TESTS_ROOT / relative
    assert not collection.exclude_module(path)
    assert not collection.exclude_test(path, "test_customer_behavior_rust")


def test_exclusions_do_not_apply_to_other_packages_rust(tmp_path):
    assert not collection.exclude_module(tmp_path / "test_crud.py")


def test_inventory_paths_and_retained_functions_exist_rust():
    for relative in collection.LEGACY_MODULES | collection.LOCAL_COMPARISON_MODULES:
        assert (collection.TESTS_ROOT / relative).is_file(), relative
    for relative, retained in collection.RETAINED_COMPARISON_TESTS.items():
        assert relative in collection.LOCAL_COMPARISON_MODULES
        tree = ast.parse((collection.TESTS_ROOT / relative).read_text(encoding="utf-8-sig"))
        functions = {
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert retained <= functions, relative


def test_source_linked_rust_copies_remain_collectable_rust():
    copies = []
    for path in collection.TESTS_ROOT.rglob("test_*.py"):
        if path.parent.name not in ("sync", "aio"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        if not any(line.lstrip().startswith("# Source:") for line in text.splitlines()):
            continue
        copies.append(path)
        assert not collection.exclude_module(path), path
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                assert not collection.exclude_test(path, node.name), (path, node.name)
    assert copies


def test_mixed_module_keeps_rust_checks_but_not_paired_calls_rust():
    path = collection.TESTS_ROOT / "auth" / "sync" / "test_token_credential_parity.py"
    assert not collection.exclude_module(path)
    assert collection.exclude_test(path, "test_create_item_parity_with_token_credential_rust")
    assert not collection.exclude_test(path, "test_engine_shared_for_one_credential_object_rust")


@pytest.mark.parametrize("relative", sorted(collection.ADAPTER_PARAMETER_MODULES))
@pytest.mark.parametrize("parameter", ["backend", "backend_name"])
def test_only_real_legacy_parameter_cases_are_deselected_rust(relative, parameter):
    path = collection.TESTS_ROOT / relative
    assert collection.exclude_parameters(path, {parameter: "core-python"})
    assert collection.exclude_parameters(path, {parameter: "core_python"})
    assert not collection.exclude_parameters(path, {parameter: "rust"})
    assert not collection.exclude_parameters(path, {})
    assert not collection.exclude_parameters(
        collection.TESTS_ROOT / "common" / "test_public_runtime_unit.py", {parameter: "core-python"},
    )


@pytest.fixture
def collection_project(tmp_path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_crud.py").write_text(
        "import unittest\n"
        "class TestOriginal(unittest.TestCase):\n"
        "    def test_original(self):\n"
        "        raise AssertionError('original executed')\n",
        encoding="utf-8",
    )
    (tests / "test_config.py").write_text("print('LEGACY_CONFIG_IMPORTED')\n", encoding="utf-8")
    (tests / "test_kept_unit.py").write_text(
        "from test_crud import TestOriginal\n"
        "def test_maintained_rust():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    mixed = tests / "auth" / "sync"
    mixed.mkdir(parents=True)
    (mixed / "test_token_credential_parity.py").write_text(
        "def test_create_item_parity_with_token_credential_rust():\n"
        "    raise AssertionError('paired comparison executed')\n"
        "def test_engine_shared_for_one_credential_object_rust():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    return tests


def _run_collection_project(tests, *arguments):
    code = textwrap.dedent("""
        import importlib.util
        from pathlib import Path
        import sys
        import pytest
        from config import collection
        original_root = collection.TESTS_ROOT
        collection.TESTS_ROOT = Path(sys.argv[1])
        spec = importlib.util.spec_from_file_location("exclusion_test_plugin", original_root / "conftest.py")
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        raise SystemExit(pytest.main(["-q", "-s", "-p", "no:cacheprovider", *sys.argv[2:]], plugins=[plugin]))
    """)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join((
        str(collection.TESTS_ROOT), str(collection.TESTS_ROOT.parent),
    ))
    environment.pop("PYTEST_ADDOPTS", None)
    environment.pop("COSMOS_PARITY_CAPTURE_OP", None)
    return subprocess.run(
        [sys.executable, "-c", code, str(tests), *arguments],
        cwd=tests.parent, env=environment, capture_output=True, text=True, timeout=60, check=False,
    )


def test_default_discovery_omits_originals_and_legacy_configuration_rust(collection_project):
    result = _run_collection_project(collection_project, "--collect-only", str(collection_project))
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "2 tests collected" in output, output
    assert "test_maintained_rust" in output
    assert "test_engine_shared_for_one_credential_object_rust" in output
    assert "test_original" not in output
    assert "test_create_item_parity" not in output
    assert "LEGACY_CONFIG_IMPORTED" not in output


def test_local_opt_in_restores_original_and_comparison_collection_rust(collection_project):
    result = _run_collection_project(
        collection_project, "--collect-only", "--include-legacy-tests", str(collection_project),
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "5 tests collected" in output, output
    assert "test_original" in output
    assert "test_create_item_parity" in output
    assert "LEGACY_CONFIG_IMPORTED" in output


def test_explicit_original_path_requires_local_opt_in_rust(collection_project):
    result = _run_collection_project(collection_project, "--collect-only", str(collection_project / "test_crud.py"))
    output = result.stdout + result.stderr
    assert result.returncode == pytest.ExitCode.USAGE_ERROR, output
    assert "Use --include-legacy-tests" in output


def test_imported_original_class_does_not_execute_or_add_skips_rust(collection_project):
    result = _run_collection_project(collection_project, str(collection_project / "test_kept_unit.py"))
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "1 passed" in output
    assert "skipped" not in output
