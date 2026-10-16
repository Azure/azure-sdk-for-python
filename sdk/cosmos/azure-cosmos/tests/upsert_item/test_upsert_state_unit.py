# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run the real copied upsert assertions against controlled stored-state failures."""

import ast
import asyncio
import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos.exceptions import CosmosHttpResponseError


ROOT = Path(__file__).resolve().parents[2]
COPY = ROOT / "tests" / "upsert_item" / "sync" / "legacy" / "test_crud.py"


def test_upsert_copy_preserves_complete_original_method():
    def method(path):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "TestCRUDOperations")
        return next(node for node in cls.body if getattr(node, "name", None) == "test_document_upsert")

    assert ast.dump(method(COPY)) == ast.dump(method(ROOT / "tests" / "test_crud.py"))


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "item_id,error_type,message",
    [(7, TypeError, "Id type must be a string."),
     (True, TypeError, "Id type must be a string."),
     (["doc"], TypeError, "Id type must be a string."),
     ("bad/id", ValueError, "Id contains illegal chars."),
     ("trailing ", ValueError, "Id ends with a space or newline.")],
)
def test_upsert_rejects_invalid_id_before_execution(asynchronous, item_id, error_type, message):
    from azure.cosmos._helpers._item_operations import ItemHelper
    from azure.cosmos.aio._helpers._item_operations import AsyncItemHelper

    backend = MagicMock()
    execute = AsyncMock() if asynchronous else MagicMock()
    execute.side_effect = AssertionError("Invalid ID reached backend execution")
    backend.execute = execute
    body = {"id": item_id, "pk": "pk"}
    original = copy.deepcopy(body)
    helper = AsyncItemHelper(backend) if asynchronous else ItemHelper(backend)
    with pytest.raises(error_type) as caught:
        if asynchronous:
            asyncio.run(helper.upsert_item(container_link="dbs/d/colls/c", body=body))
        else:
            helper.upsert_item(container_link="dbs/d/colls/c", body=body)
    assert str(caught.value) == message
    execute.assert_not_called()
    assert body == original


@pytest.mark.parametrize(
    "failure",
    [None, "create_not_saved", "replacement_not_saved", "wrong_stored_create", "wrong_stored_replacement",
     "database", "container", "delete", "close", "replacement_and_delete"],
)
def test_upsert_checks_both_stored_states_and_cleanup(monkeypatch, failure):
    spec = importlib.util.spec_from_file_location("upsert_crud_copy", COPY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = MagicMock()
    database = client.create_database.return_value
    container = database.get_container_client.return_value
    store = {}
    events, reads = [], []
    version = 0

    def upsert(body, **kwargs):
        nonlocal version
        if not isinstance(body["id"], str):
            raise TypeError("id must be a string")
        key = (body["id"], body["pk"])
        if kwargs.get("etag") is not None and kwargs["etag"] != store[key]["_etag"]:
            raise CosmosHttpResponseError(status_code=412, message="stale etag")
        version += 1
        result = copy.deepcopy(body)
        result["_etag"] = str(version)
        is_replacement = key in store
        if not (
            failure == "create_not_saved"
            or (is_replacement and failure in ("replacement_not_saved", "replacement_and_delete"))
        ):
            store[key] = copy.deepcopy(result)
        if (
            failure == "wrong_stored_create" and not is_replacement
            or failure == "wrong_stored_replacement" and is_replacement
        ):
            store[key]["spam"] = "wrong"
        return result

    def read(item, partition_key):
        value = copy.deepcopy(store[(item, partition_key)])
        reads.append(value)
        return value

    def delete_database(database_id):
        events.append("delete")
        if failure in ("delete", "replacement_and_delete"):
            raise RuntimeError("delete failed")

    def close():
        events.append("close")
        if failure == "close":
            raise RuntimeError("close failed")

    container.upsert_item.side_effect = upsert
    container.read_item.side_effect = read
    container.read_all_items.side_effect = lambda: copy.deepcopy(list(store.values()))
    container.delete_item.side_effect = lambda item, partition_key: store.pop((item["id"], partition_key))
    client.delete_database.side_effect = delete_database
    client.close.side_effect = close
    if failure == "database":
        client.create_database.side_effect = RuntimeError("database failed")
    if failure == "container":
        database.create_container.side_effect = RuntimeError("container failed")
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    monkeypatch.setenv("ACCOUNT_HOST", "https://example.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    case = module.TestCRUDOperations("test_document_upsert")
    result = unittest.TestResult()
    case.run(result)

    assert result.wasSuccessful() is (failure is None)
    assert events == (["close"] if failure == "database" else ["delete", "close"])
    if failure != "database":
        client.delete_database.assert_called_once_with(case._db_id)
    if failure in (
        "create_not_saved", "replacement_not_saved", "wrong_stored_create",
        "wrong_stored_replacement", "replacement_and_delete",
    ):
        assert len(result.failures) == 1
    if failure in ("delete", "replacement_and_delete"):
        assert "delete failed" in result.errors[0][1]
    if failure is None:
        assert [row["spam"] for row in reads] == ["eggs", "not eggs"]
        assert [row["id"] for row in reads] == ["doc", "doc"]
        assert not store
