# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline migration guards, not native execution or live parity evidence."""

import ast
from pathlib import Path

import pytest

from common.test_copy_generator_unit import _gen, _norm
from common.test_migration_enforcer_unit import _class_method_exists, _iter_test_functions, _source_ref
from config.collection import exclude_module, exclude_parameters, exclude_test
from create_item import test_assertion_correspondence_unit as correspondence

ROOT = Path(__file__).resolve().parents[2]
COPIES = [
    ROOT / "tests" / "create_item" / surface / filename
    for surface in ("sync", "aio")
    for filename in ("test_contracts.py", "test_input_variants.py")
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
        original = ast.parse(correspondence._read_file(filename)[0])
        assert _class_method_exists(original, cls, method), source


@pytest.mark.parametrize("local_exists", [False, True])
@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_original_source_ignores_modified_or_removed_legacy_files_rust(monkeypatch, tmp_path, local_exists, newline):
    original = "def test_original():\n    assert True\n"
    local = tmp_path / "tests" / "test_original.py"
    if local_exists:
        local.parent.mkdir()
        local.write_text("def test_local():\n    assert False\n", encoding="utf-8")
    monkeypatch.setattr(correspondence, "ROOT", tmp_path)
    monkeypatch.setattr(
        correspondence, "_main_sources",
        lambda: {"tests\\test_original.py": original.replace("\n", newline)},
    )
    text, functions = correspondence._read_file.__wrapped__("tests\\test_original.py")
    assert text == original
    assert set(functions) == {"test_original"}


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_aad_gap_skips_precede_fixture_setup_rust(surface):
    import importlib

    module = importlib.import_module(f"create_item.{surface}.test_contracts")
    for name in ("test_compact_utf8_item_write_with_aad_rust", "test_aad_credentials_rust"):
        function = getattr(module, name)
        skips = [mark for mark in function.pytestmark if mark.name == "skip"]
        assert len(skips) == 1
        assert skips[0].kwargs["reason"].startswith("driver-gap: Gap 40 -")
        assert not any(mark.name == "skipif" for mark in function.pytestmark)


def test_async_suppression_sequence_matches_main_rust():
    original = correspondence._read_file("tests\\test_crud_response_payload_on_write_disabled_async.py")[1][
        "TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_document_crud_async"
    ]
    replacement = correspondence._read_file("tests\\create_item\\aio\\test_contracts.py")[1][
        "test_document_crud_response_payload_on_write_disabled_rust"
    ]

    def create_modes(function):
        calls = [
            node for statement in function.body
            if isinstance(statement, (ast.Assign, ast.Assert, ast.Expr))
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "create_item"
        ]
        return [
            {
                keyword.arg: ast.literal_eval(keyword.value)
                for keyword in call.keywords
                if keyword.arg in {"enable_automatic_id_generation", "no_response"}
            }
            for call in sorted(calls, key=lambda node: node.lineno)
        ]

    assert create_modes(replacement) == create_modes(original)


def test_default_session_copy_retains_original_sequence_and_collection_rust():
    source_path = "tests\\test_user_configs.py"
    target_path = "tests\\create_item\\sync\\test_user_configs.py"
    original = correspondence._read_file(source_path)[1]
    replacement = correspondence._read_file(target_path)[1]
    source = original["TestUserConfigs.test_default_account_consistency"]
    target = replacement["TestUserConfigs.test_default_account_consistency_rust"]
    assert correspondence._fingerprint(original["get_test_item"]) == correspondence._fingerprint(
        replacement["get_test_item"]
    )

    def assertions(function):
        return [
            ast.dump(node)
            for node in ast.walk(function)
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "").startswith("assert")
        ]

    # Pinned main predates the Eventual/Strong read checks in the current legacy
    # file. Compare its Session prerequisite and two token assertions here.
    assert assertions(target)[:3] == assertions(source)[:3]
    for operation in ("create_container", "create_item", "read_item"):
        calls = [
            [
                ast.dump(node)
                for node in sorted(
                    (node for node in ast.walk(function)
                     if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == operation),
                    key=lambda node: node.lineno,
                )
            ]
            for function in (source, target)
        ]
        if operation == "read_item":
            assert calls[0][:1] == calls[1][:1], operation
        else:
            assert calls[0] == calls[1], operation
    path = ROOT.joinpath(*target_path.split("\\"))
    assert not exclude_module(path)
    assert not exclude_test(path, target.name)
    original_context = correspondence._annotation_context(
        source_path, "TestUserConfigs.test_default_account_consistency"
    )
    target_context = correspondence._annotation_context(
        target_path, "TestUserConfigs.test_default_account_consistency_rust"
    )
    assert correspondence._category_marks(target_context) == correspondence._category_marks(original_context)


def test_default_session_requires_session_before_provisioning_rust():
    from unittest.mock import MagicMock
    from create_item.sync.test_user_configs import TestUserConfigs

    case = TestUserConfigs("test_default_account_consistency_rust")
    case.key_client = MagicMock()
    case.data_client = MagicMock()
    account = case.key_client.client_connection.GetDatabaseAccount.return_value
    account.ConsistencyPolicy = {"defaultConsistencyLevel": "BoundedStaleness"}
    with pytest.raises(AssertionError, match="BoundedStaleness"):
        case.test_default_account_consistency_rust()
    case.key_client.create_database.assert_not_called()
    case.data_client.get_database_client.assert_not_called()


def test_async_suppression_observer_uses_last_write_session_rust(monkeypatch):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock

    from create_item.aio import test_contracts as contracts
    from azure.core.utils import CaseInsensitiveDict
    from azure.cosmos import CosmosDict, exceptions

    stored = []
    tokens = []

    async def create(body, **kwargs):
        if len(stored) == 4:
            raise exceptions.CosmosResourceExistsError(status_code=409)
        item = dict(body)
        item.setdefault("id", "generated")
        stored.append(item)
        tokens.append(f"0:-1#{len(stored)}")
        return CosmosDict(
            {} if kwargs.get("no_response", True) else item,
            response_headers=CaseInsensitiveDict({"x-ms-session-token": tokens[-1]}),
        )

    async def query(_query, **kwargs):
        # A fresh reader need not see the writes without the writer's token.
        if kwargs.get("session_token") == tokens[-1]:
            for item in stored:
                yield item

    writer = MagicMock(id="container")
    writer.create_item = AsyncMock(side_effect=create)
    reader = MagicMock()
    reader.query_items.side_effect = query
    client = MagicMock()
    client.get_database_client.return_value.get_container_client.return_value = writer
    observer = MagicMock()
    observer.get_database_client.return_value.get_container_client.return_value = reader
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=observer)
    context.__aexit__ = AsyncMock(return_value=False)
    monkeypatch.setattr(contracts.clients, "create_data_client_async", MagicMock(return_value=context))
    monkeypatch.setattr(contracts, "observe_native_create", MagicMock(return_value=None))
    asyncio.run(contracts.test_document_crud_response_payload_on_write_disabled_rust(
        SimpleNamespace(id="database"), lambda _partition_key: writer, client, monkeypatch, "rust",
    ))
    reader.query_items.assert_called_once_with(
        "SELECT * FROM c", partition_key="pk", session_token=tokens[-1],
    )
