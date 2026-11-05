# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline migration guards, not native execution or live parity evidence."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from auth.sync import test_token_credential_parity as token_tests
from common.test_legacy_copy_generator_unit import _gen, _norm
from common.test_legacy_migration_enforcer_unit import _class_method_exists, _iter_test_functions, _source_ref
from config.collection import exclude_parameters

ROOT = Path(__file__).resolve().parents[2]
COPIES = [
    ROOT / "tests" / "create_item" / surface / filename
    for surface in ("sync", "aio")
    for filename in ("test_legacy_contracts.py", "test_legacy_variants.py")
]


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_bucket_copies_match_generator_rust(surface):
    spec = getattr(_gen, f"CREATE_ITEM_{surface.upper()}_HEADERS")
    copy = ROOT / "tests" / "create_item" / surface / "test_headers.py"
    assert _norm(_gen.render_legacy_file(spec)) == _norm(copy.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", COPIES, ids=lambda path: "/".join(path.parts[-2:]))
def test_create_source_lineage_and_collection_rust(path):
    text = path.read_text(encoding="utf-8")
    functions = list(_iter_test_functions(ast.parse(text)))
    assert functions
    assert '_backend="rust"' in text
    assert "pytest.mark.cosmosEmulator" in text
    assert exclude_parameters(path, {"backend": "core-python"})
    assert not exclude_parameters(path, {"backend": "rust"})
    for _, function in functions:
        assert function.name.endswith("_rust")
        source = _source_ref(function, text.splitlines())
        assert source, function.name
        filename, qualified = source.split("::")
        cls, method = qualified.split(".")
        original = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        assert _class_method_exists(original, cls, method), source


def test_aad_create_parity_isolates_ids_and_requires_success_rust(monkeypatch):
    credential = SimpleNamespace(close=Mock())
    monkeypatch.setattr(token_tests, "make_sync_token_credential", lambda: credential)
    bodies = []

    def create_item(*, body):
        assert body["id"] not in {item["id"] for item in bodies}, "Backend creates reused an ID"
        bodies.append(dict(body))
        return dict(body)

    container = SimpleNamespace(create_item=create_item)
    database = SimpleNamespace(get_container_client=lambda _: container)
    client = SimpleNamespace(get_database_client=lambda _: database)
    outcomes = SimpleNamespace(
        core_python=SimpleNamespace(raised=None), rust=SimpleNamespace(raised=None),
        print_report=Mock(), assert_functional_parity=Mock(),
    )

    def compare(operation, **_):
        operation(client)
        operation(client)
        return outcomes

    monkeypatch.setattr(token_tests, "run_on_both_backends", compare)
    token_tests.test_create_item_parity_with_token_credential_rust(SimpleNamespace(id="container"))
    assert len(bodies) == 2
    credential.close.assert_called_once()
    outcomes.rust.raised = RuntimeError("Rust create failed")
    with pytest.raises(AssertionError):
        token_tests.test_create_item_parity_with_token_credential_rust(SimpleNamespace(id="container"))
