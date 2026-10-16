# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Conditional patch assertions must cover rejection and stored state."""

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


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "scenario",
    ["correct", "unexpected_success", "wrong_status", "unsupported",
     "rejected_number_changed", "rejected_address_changed", "rejected_field_added",
     "accepted_not_stored", "accepted_id_changed", "accepted_address_changed",
     "accepted_removed_field_retained"],
)
def test_original_conditional_patch_checks_state(asynchronous, scenario):
    filename = "test_crud_async.py" if asynchronous else "test_crud.py"
    name = "test_conditional_patching_async" if asynchronous else "test_conditional_patching"
    tree = ast.parse((ROOT / "tests" / filename).read_text(encoding="utf-8"))
    method = next(node for node in ast.walk(tree) if getattr(node, "name", None) == name)
    namespace = {"uuid": uuid, "exceptions": exceptions, "StatusCodes": StatusCodes}
    exec(compile(ast.Module(body=[method], type_ignores=[]), filename, "exec"), namespace)
    state = {}
    events = []

    def create(body):
        state.update(copy.deepcopy(body))
        events.append("create")
        return copy.deepcopy(state)

    def patch_item(*, item, partition_key, patch_operations, filter_predicate):
        assert item == state["id"]
        assert partition_key == state["pk"]
        assert len(patch_operations) == 6
        if filter_predicate.endswith(" = 4"):
            events.append("rejected_patch")
            if scenario == "unexpected_success":
                return copy.deepcopy(state)
            if scenario == "unsupported":
                raise NotImplementedError("controlled unsupported filter")
            if scenario == "rejected_number_changed":
                state["number"] = 10
            if scenario == "rejected_address_changed":
                state["address"]["city"] = "wrong"
            if scenario == "rejected_field_added":
                state["favorite_color"] = "yellow"
            status = 503 if scenario == "wrong_status" else 412
            raise exceptions.CosmosHttpResponseError(status_code=status, message="controlled condition failure")
        assert filter_predicate.endswith(" = 3")
        events.append("accepted_patch")
        result = copy.deepcopy(state)
        result.pop("prop")
        result.update(company="CosmosDB", number=10, favorite_color="yellow")
        result["address"]["new_city"] = "Atlanta"
        if scenario != "accepted_not_stored":
            state.clear()
            state.update(copy.deepcopy(result))
        if scenario == "accepted_id_changed":
            result["id"] = "wrong"
        if scenario == "accepted_address_changed":
            state["address"]["city"] = "wrong"
        if scenario == "accepted_removed_field_retained":
            state["prop"] = "prop1"
        return result

    def read(item, partition_key):
        assert item == state["id"]
        assert partition_key == state["pk"]
        events.append("read_after_accept" if "accepted_patch" in events else "read_after_reject")
        return copy.deepcopy(state)

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
        result = namespace[name](case)
        if asynchronous:
            asyncio.run(result)

    if scenario == "correct":
        invoke()
        assert events == ["create", "rejected_patch", "read_after_reject", "accepted_patch", "read_after_accept"]
    else:
        error = {
            "unsupported": NotImplementedError,
            "accepted_not_stored": KeyError,
        }.get(scenario, AssertionError)
        with pytest.raises(error):
            invoke()
        if scenario.startswith("rejected_") or scenario in ("unexpected_success", "wrong_status", "unsupported"):
            assert "accepted_patch" not in events
