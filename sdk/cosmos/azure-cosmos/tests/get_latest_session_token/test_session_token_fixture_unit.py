# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Freeze retained coverage without importing or reading legacy test sources."""

import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

import pytest

from get_latest_session_token._fixtures import create_split_ranges


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parents[1]

# These AST-body fingerprints freeze all inputs, loops, assertions and calls,
# not whitespace or source comments. The first nine methods and six helpers
# are unchanged copies. Split bodies differ only in owned fixture references
# and the explicit legacy-routing-cache gate. Do not regenerate these hashes
# merely to make a weakened or missing assertion pass.
METHOD_BODIES = {
    "sync/legacy/test_session_token_helpers_owned.py": {
        "test_get_session_token_update": "963c27bf13dfa1bf7f40fc7ac02b490c60ff6b9c49f685ad349ec62aabeb5f73",
        "test_many_session_tokens_update_same_range": "6f89f0f71c95b5e704b4d72c3eabbac5c4c160da4fd5209669a9d13470e170b2",
        "test_many_session_tokens_update": "d10b48f5ed8619092260b61abe6b49277ac5939da76a8a6f839b3f84e7b2b193",
        "test_simulated_splits_merges": "f8465ca99fa0ac65267839a29283542ce8dfdffa0d382de302d04a2adbd226f3",
        "test_invalid_feed_range": "db20272a219e78701cacf3b62cf178d619565bb8ceecc048a826002e96da99b7",
    },
    "sync/legacy/test_latest_session_token.py": {
        "test_latest_session_token_hpk": "2f935a84eac50b39bc95ae68f88f628567f1d95fa29f9c1d80e2f15e63de1519",
        "test_latest_session_token_logical_hpk": "66162d59cd92f847d3e7b0ba9c6d5ae0c40d7708eab08d9075f4166e7908aec3",
    },
    "aio/legacy/test_latest_session_token_async.py": {
        "test_latest_session_token_hpk": "5dc721307d493ac3f9352feb1957ab11c8beffba4b43d3dff0bf1750ef568720",
        "test_latest_session_token_logical_hpk": "ebf0804f3484d0f7e5b5ac05dcdfff80209dbb32e63e21937589871dbd1ecc8a",
    },
    "sync/legacy/test_latest_session_token_real_split.py": {
        "test_change_feed_session_token_and_read_items_after_split":
            "192adbbda150de45aacdb368987068a80baa1bf23afe8dd45a49fa7dae2a014d",
    },
    "aio/legacy/test_latest_session_token_real_split_async.py": {
        "test_change_feed_session_token_and_read_items_after_split_async":
            "12dab49471b7f4611f39707b2d261f01fa781de9d26376ab69fd11323a4bf5dd",
    },
}
HELPER_BODIES = {
    "create_split_ranges": "d3ca3a11bfd3227c6e043cd1a5193d82234393b066da83551eb5e12c8f3a3cee",
    "create_item": "f0a7b8d927e74233eabe2398aab96266102d81c3a209768003dd6fe01a1a27d1",
    "create_items_logical_pk": "7d1e0b4f8b4b799afb75b7d6c425746d31f4cc9cbf1b78e58af0018010fa25ae",
    "create_items_physical_pk": "d4119d3caf8ad413c461005cc8fdfffee11e508298721f4279dfc44a7abc0508",
    "create_items_logical_pk_async": "2121dbf8187693d9bab5e9c51de92aa5a1d2344f7926e0a81c74d403390e8888",
    "create_items_physical_pk_async": "7bf7ec32574c56aa7fd3e3faecc91bc3b0503a58060875dafe3d586ae3e7a808",
}


def _body_hash(node):
    return hashlib.sha256(ast.dump(ast.Module(body=node.body, type_ignores=[])).encode()).hexdigest()


def test_retained_manifest_covers_every_copied_file_and_case_rust():
    paths = {path.relative_to(ROOT).as_posix() for path in ROOT.glob("*/legacy/test_*.py")}
    assert paths == set(METHOD_BODIES)
    assert sum(len(methods) for methods in METHOD_BODIES.values()) == 11
    assert len(create_split_ranges()) == 13
    assert 11 - 1 + len(create_split_ranges()) == 23
    for surface in ("sync", "aio"):
        assert (ROOT / surface / "legacy" / "__init__.py").is_file()


@pytest.mark.parametrize("name", METHOD_BODIES)
def test_copied_method_bodies_match_retained_manifest_rust(name):
    source = (ROOT / name).read_text(encoding="utf-8")
    copied = ast.parse(source)
    methods = {
        node.name: node for node in ast.walk(copied)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    }
    assert {
        method_name.removesuffix("_rust"): _body_hash(method)
        for method_name, method in methods.items()
    } == METHOD_BODIES[name]
    for method in methods.values():
        assert any(
            line.strip().startswith("# Source: tests/")
            for line in source.splitlines()[method.lineno:method.end_lineno]
        )
    assert source.count('_backend="rust"') == 1
    assert any(
        isinstance(node, ast.Attribute) and node.attr == "cosmosEmulator"
        for node in ast.walk(copied)
    )
    if "real_split" not in name:
        assert not any(
            isinstance(node, ast.Name) and node.id in ("trigger_split", "trigger_split_async")
            for node in ast.walk(copied)
        )
        assert not any(
            isinstance(node, ast.Attribute) and node.attr in ("trigger_split", "trigger_split_async")
            for node in ast.walk(copied)
        )


def test_retained_write_helpers_and_split_inputs_are_unchanged_rust():
    tree = ast.parse((ROOT / "_fixtures.py").read_text(encoding="utf-8"))
    assert {
        node.name: _body_hash(node) for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    } == HELPER_BODIES


@pytest.mark.parametrize("mode", ["collection", "units"])
def test_retained_suite_collects_and_runs_units_without_legacy_sources_rust(mode):
    """Block original imports AND dynamic reads, without touching shared files."""
    script = r'''
import os
from pathlib import Path
import sys

blocked = {
    "test_session_token_helpers", "test_partition_split_scenarios",
    "test_partition_split_scenarios_async", "_split_test_utils", "test_config",
}
def guard(event, args):
    if event == "import" and args[0].rsplit(".", 1)[-1] in blocked:
        raise AssertionError("Retained suite imported a legacy test: " + args[0])
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name = Path(os.fsdecode(args[0])).name.split(".", 1)[0]
        if name in blocked:
            raise AssertionError("Retained suite read a legacy test: " + name)
sys.addaudithook(guard)
import pytest

class Counts:
    def pytest_collection_finish(self, session):
        if sys.argv[1] == "collection":
            assert len(session.items) == 23, len(session.items)
            print("OWNERSHIP: 23 marker-selected copied cases; legacy reads/imports blocked")

options = ["--noconftest", "--import-mode=importlib", "-p", "no:cacheprovider", "-q"]
root = Path("tests") / "get_latest_session_token"
if sys.argv[1] == "collection":
    options += ["--collect-only", "-m", "cosmosEmulator", str(root)]
else:
    options += [
        "-k", "not test_retained_suite_collects_and_runs_units_without_legacy_sources",
        str(root / "test_get_latest_session_token_unit.py"),
        str(root / "test_session_token_fixture_unit.py"),
        str(root / "test_session_token_split_fixture_unit.py"),
    ]
code = pytest.main(options, plugins=[Counts()])
assert not blocked.intersection(sys.modules)
raise SystemExit(code)
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(PACKAGE), str(PACKAGE / "tests")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("COSMOS_SESSION_TOKEN_REAL_SPLIT", None)
    env.pop("COSMOS_PARITY_CAPTURE_OP", None)
    env.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        [sys.executable, "-c", script, mode],
        cwd=PACKAGE, env=env, capture_output=True, text=True, timeout=120, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
