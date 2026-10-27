# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep both comparison runners on the same original container assertions."""

import ast
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from common._retired_test_sources import RETIRED_THROUGHPUT_SOURCES


ROOT = Path(__file__).resolve().parents[2]


def runner():
    script_dir = ROOT / "scripts" / "v5"
    spec = importlib.util.spec_from_file_location("container_throughput_runner", script_dir / "run_container_throughput_parity.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(script_dir))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(script_dir))
    return module


def assertions(method, cls):
    nodes = list(ast.walk(method))
    names = {
        node.func.attr for node in nodes if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "self" and not node.func.attr.startswith("assert")
    }
    nodes.extend(
        child for helper in cls.body if getattr(helper, "name", None) in names for child in ast.walk(helper)
    )
    return {
        ast.dump(node) for node in nodes if isinstance(node, ast.Assert) or (
            isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert")
        )
    }


@pytest.mark.parametrize("operation,expected", [("get", 27), ("replace", 18)])
@pytest.mark.parametrize("backend", ["rust", "core-python"])
def test_same_original_selection_and_source_pins_rust(monkeypatch, operation, expected, backend):
    module = runner()
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(sys, "argv", ["runner", "--operation", operation, "--backend", backend])
    observed = []
    references = []

    def collect(arguments):
        targets = [argument for argument in arguments if "::" in argument]
        assert len(targets) == len(set(targets)) == expected
        for target in targets:
            filename, class_name, method_name = target.split("::")
            text = Path(filename).read_text(encoding="utf-8")
            tree = ast.parse(text)
            pins = [
                node.value.value for node in ast.walk(tree)
                if isinstance(node, ast.keyword) and node.arg == "_backend" and isinstance(node.value, ast.Constant)
            ]
            assert pins == [backend]
            cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
            method = next(node for node in cls.body if getattr(node, "name", None) == method_name)
            reference, = re.findall(r"# Source: (tests/\S+)", ast.get_source_segment(text, method))
            source, qualified = RETIRED_THROUGHPUT_SOURCES.get(reference, reference).split("::")
            original_class, original_method = qualified.split(".")
            original = ast.parse((ROOT / source).read_text(encoding="utf-8"))
            original_cls = next(node for node in original.body if isinstance(node, ast.ClassDef) and node.name == original_class)
            original_node = next(node for node in original_cls.body if getattr(node, "name", None) == original_method)
            if method_name != "test_offer_methods":
                assert assertions(original_node, original_cls) <= assertions(method, cls), reference
            references.append(reference)
        observed.extend(targets)
        return 0

    monkeypatch.setattr(module.pytest, "main", collect)
    assert module.main() == 0
    assert sys.path[:2] == [str(ROOT), str(ROOT / "tests")]
    assert len(observed) == expected
    assert len(set(references)) == expected
    assert sum("container_recreate" in ref for ref in references) == 4
    assert sum("responses" in ref for ref in references) == 2
    assert sum("test_none_options" in ref for ref in references) == (2 if operation == "get" else 0)


def test_explicit_none_original_calls_and_assertions_are_preserved_rust():
    def calls(method):
        return [
            ast.dump(node) for node in ast.walk(method)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get_throughput"
        ]

    for surface, suffix in (("sync", ""), ("aio", "_async")):
        source_path = ROOT / "tests" / f"test_none_options{suffix}.py"
        reference = (
            f"tests/{source_path.name}::TestNoneOptions{'Async' if suffix else ''}"
            f".test_get_throughput_none_options{suffix}"
        )
        filename, qualified = RETIRED_THROUGHPUT_SOURCES.get(reference, reference).split("::")
        original_class, original_method = qualified.split(".")
        original = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        original_cls = next(
            node for node in original.body if isinstance(node, ast.ClassDef) and node.name == original_class
        )
        original_node = next(node for node in original_cls.body if getattr(node, "name", None) == original_method)
        copied = ROOT / "tests" / "get_container_throughput" / surface / "legacy" / "test_none_options.py"
        tree = ast.parse(copied.read_text(encoding="utf-8"))
        assert calls(original_node) == calls(tree)
        assert len(calls(tree)) == 1
        assert any(
            isinstance(node, ast.keyword) and node.arg == "response_hook"
            and isinstance(node.value, ast.Constant) and node.value.value is None
            for node in ast.walk(tree)
        )


@pytest.mark.parametrize("selection,expected", [("get", 27), ("replace", 18), ("live", 34)])
def test_marker_selection_collects_without_original_test_sources_rust(selection, expected):
    script = r'''
import importlib.util
import os
from pathlib import Path
import sys

root = Path.cwd()
sys.path[:0] = [str(root), str(root / "tests"), str(root / "scripts" / "v5")]
blocked = {path.stem for path in (root / "tests").glob("test_*.py")}
paths = {os.path.normcase(str(root / "tests" / (name + ".py"))) for name in blocked}
def guard(event, args):
    if event == "import" and args[0] in blocked:
        raise AssertionError("Imported original test source: " + args[0])
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        if os.path.normcase(os.path.abspath(os.fsdecode(args[0]))) in paths:
            raise AssertionError("Read original test source")
sys.addaudithook(guard)
selection, expected = sys.argv[1], int(sys.argv[2])
if selection == "live":
    targets = [
        str(root / "tests" / family / name)
        for family, names in (
            ("get_container_throughput", (
                "test_container_throughput_parity.py",
                "sync/test_get_throughput_parity.py", "aio/test_get_throughput_parity_async.py",
            )),
            ("replace_throughput", (
                "test_container_throughput_parity.py",
                "sync/test_replace_throughput_parity.py", "aio/test_replace_throughput_parity_async.py",
            )),
        )
        for name in names
    ]
else:
    spec = importlib.util.spec_from_file_location("runner", root / "scripts/v5/run_container_throughput_parity.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    targets = [target for path in runner.test_files(selection) for target in runner.test_targets(path, selection)]
class Counts:
    def pytest_collection_finish(self, session):
        assert len(session.items) == expected
        assert all(item.get_closest_marker("cosmosEmulator") is not None for item in session.items)
import pytest
raise SystemExit(pytest.main([
    "--noconftest", "--import-mode=importlib", "--collect-only", "-q",
    "-m", "cosmosEmulator", "-p", "no:cacheprovider", *targets,
], plugins=[Counts()]))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "tests")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("COSMOS_PARITY_CAPTURE_OP", None)
    result = subprocess.run(
        [sys.executable, "-c", script, selection, str(expected)], cwd=ROOT, env=env,
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
