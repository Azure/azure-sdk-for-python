# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original patch assertions must require errors and distinguish absent fields."""

import ast
import asyncio
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from azure.cosmos import exceptions
from azure.cosmos.http_constants import StatusCodes


ROOT = Path(__file__).resolve().parents[2]
NEGATIVE_OPERATIONS = ("replace", "remove", "incr", "move")


def _original_patch_method(asynchronous):
    filename = "test_crud_async.py" if asynchronous else "test_crud.py"
    name = "test_patch_operations_async" if asynchronous else "test_patch_operations"
    tree = ast.parse((ROOT / "tests" / filename).read_text(encoding="utf-8"))
    method = next(node for node in ast.walk(tree) if getattr(node, "name", None) == name)
    namespace = {"uuid": uuid, "exceptions": exceptions, "StatusCodes": StatusCodes}
    exec(compile(ast.Module(body=[method], type_ignores=[]), filename, "exec"), namespace)
    return namespace[name]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("operation", NEGATIVE_OPERATIONS)
@pytest.mark.parametrize("outcome", ["400", "success", "503", "wrong_exception"])
def test_original_patch_requires_each_rejection(asynchronous, operation, outcome):
    method = _original_patch_method(asynchronous)
    calls = []

    def patch_item(*, item, partition_key, patch_operations):
        if len(patch_operations) == 6:
            calls.append("positive")
            return {"company": "CosmosDB", "address": {"new_city": "Atlanta"},
                    "number": 10, "favorite_color": "yellow"}
        current = patch_operations[0]["op"]
        calls.append(current)
        if current == operation:
            if outcome == "success":
                return {}
            if outcome == "wrong_exception":
                raise TypeError("controlled wrong exception")
            if outcome == "503":
                raise exceptions.CosmosHttpResponseError(status_code=503, message="controlled unavailable")
        raise exceptions.CosmosHttpResponseError(status_code=400, message="controlled invalid patch")

    container = MagicMock()
    container.create_item = AsyncMock() if asynchronous else MagicMock()
    container.patch_item = (AsyncMock if asynchronous else MagicMock)(side_effect=patch_item)
    container.read_item = (AsyncMock if asynchronous else MagicMock)(
        return_value={"favorite_color": "yellow"},
    )
    database = MagicMock()
    database.get_container_client.return_value = container
    case = unittest.TestCase()
    case.databaseForTest = case.database_for_test = database
    case.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="orders")

    def invoke():
        result = method(case)
        if asynchronous:
            asyncio.run(result)

    if outcome == "400":
        invoke()
        assert calls == ["positive", *NEGATIVE_OPERATIONS]
    else:
        error = TypeError if outcome == "wrong_exception" else AssertionError
        with pytest.raises(error):
            invoke()
        assert calls == ["positive", *NEGATIVE_OPERATIONS[:NEGATIVE_OPERATIONS.index(operation) + 1]]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("outcome", [
    "correct", "returned_prop_null", "returned_color_null",
    "stored_prop_null", "stored_color_null", "stored_prop_retained", "stored_color_retained",
    "stored_destination_missing", "stored_destination_wrong", "stored_destination_null",
    "returned_destination_wrong",
])
def test_original_patch_requires_removed_and_moved_fields_absent(asynchronous, outcome):
    method = _original_patch_method(asynchronous)
    stored, events, requests = {}, [], []
    expected_operations = [
        {"op": "add", "path": "/color", "value": "yellow"},
        {"op": "remove", "path": "/prop"},
        {"op": "replace", "path": "/company", "value": "CosmosDB"},
        {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
        {"op": "incr", "path": "/number", "value": 7},
        {"op": "move", "from": "/color", "path": "/favorite_color"},
    ]

    def create(body):
        events.append("create")
        stored.update(copy.deepcopy(body))
        return copy.deepcopy(stored)

    def patch_item(*, item, partition_key, patch_operations):
        requests.append((item, partition_key, copy.deepcopy(patch_operations)))
        if len(patch_operations) != 6:
            events.append(patch_operations[0]["op"])
            raise exceptions.CosmosHttpResponseError(status_code=400)
        events.append("positive")
        stored.pop("prop")
        stored.update(company="CosmosDB", number=10, favorite_color="yellow")
        stored["address"]["new_city"] = "Atlanta"
        result = copy.deepcopy(stored)
        if outcome == "returned_prop_null":
            result["prop"] = None
        elif outcome == "returned_color_null":
            result["color"] = None
        elif outcome == "stored_prop_null":
            stored["prop"] = None
        elif outcome == "stored_color_null":
            stored["color"] = None
        elif outcome == "stored_prop_retained":
            stored["prop"] = "prop1"
        elif outcome == "stored_color_retained":
            stored["color"] = "yellow"
        elif outcome == "stored_destination_missing":
            del stored["favorite_color"]
        elif outcome == "stored_destination_wrong":
            stored["favorite_color"] = "wrong"
        elif outcome == "stored_destination_null":
            stored["favorite_color"] = None
        elif outcome == "returned_destination_wrong":
            result["favorite_color"] = "wrong"
        return result

    def read(item, partition_key):
        events.append("read")
        assert item == stored["id"] and partition_key == stored["pk"]
        return copy.deepcopy(stored)

    mock = AsyncMock if asynchronous else MagicMock
    container = MagicMock()
    container.create_item = mock(side_effect=create)
    container.patch_item = mock(side_effect=patch_item)
    container.read_item = mock(side_effect=read)
    database = MagicMock()
    database.get_container_client.return_value = container
    case = unittest.TestCase()
    case.databaseForTest = case.database_for_test = database
    case.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="orders")

    def invoke():
        result = method(case)
        if asynchronous:
            asyncio.run(result)

    if outcome == "correct":
        invoke()
        assert events == ["create", "positive", "read", *NEGATIVE_OPERATIONS]
    else:
        with pytest.raises(AssertionError):
            invoke()
        assert events == ["create", "positive", *(["read"] if outcome.startswith("stored_") else [])]
    assert requests[0] == (stored["id"], stored["pk"], expected_operations)
    if outcome == "correct" or outcome.startswith("stored_"):
        container.read_item.assert_called_once_with(stored["id"], partition_key=stored["pk"])
