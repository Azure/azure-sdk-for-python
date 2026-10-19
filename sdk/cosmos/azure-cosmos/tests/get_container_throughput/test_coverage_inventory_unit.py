# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep both comparison runners on the same original container assertions."""

import ast
import importlib.util
from pathlib import Path
import re
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


@pytest.mark.parametrize("operation,expected", [("get", 25), ("replace", 18)])
@pytest.mark.parametrize("backend", ["rust", "core-python"])
def test_same_original_selection_and_source_pins(monkeypatch, operation, expected, backend):
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
