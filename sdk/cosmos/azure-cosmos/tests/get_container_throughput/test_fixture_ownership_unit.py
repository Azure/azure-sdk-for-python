# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copied throughput setups must clean up after failures without deleting unowned resources."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import exceptions


def load(path):
    spec = importlib.util.spec_from_file_location("throughput_fixture_" + path.parent.name + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("family", [
    "test_auto_scale", "test_container_properties_cache", "test_crud_subpartition",
    "test_crud_response_payload_on_write_disabled", "test_none_options",
])
@pytest.mark.parametrize("failure", [None, "database-create", "conflict", "container-create", "body", "delete"])
def test_copied_setup_registers_cleanup_before_creation_rust(monkeypatch, asynchronous, family, failure):
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    filename = family + ("_async" if asynchronous and family == "test_auto_scale" else "") + ".py"
    module = load(Path(__file__).parent / ("aio" if asynchronous else "sync") / filename)
    cls, = [
        value for value in vars(module).values()
        if isinstance(value, type) and issubclass(value, unittest.TestCase)
    ]
    method = next(name for name in vars(cls) if name.startswith("test_"))
    mock_type = AsyncMock if asynchronous else MagicMock
    client = MagicMock()
    database = MagicMock()
    attempted = []
    events = []

    def create(*, id, **_kwargs):
        attempted.append(id)
        if failure == "database-create":
            raise RuntimeError("creation failed")
        if failure == "conflict":
            raise exceptions.CosmosResourceExistsError(status_code=409)
        return database

    def delete(database_id):
        events.append(("delete", database_id))
        if failure == "delete":
            raise RuntimeError("cleanup failed")

    client.create_database = mock_type(side_effect=create)
    client.delete_database = mock_type(side_effect=delete)
    client.close = mock_type(side_effect=lambda: events.append(("close", None)))
    creates_container = family in ("test_none_options", "test_crud_response_payload_on_write_disabled")
    database.create_container = mock_type(
        side_effect=RuntimeError("container failed") if failure == "container-create" else None,
    )
    monkeypatch.setattr(module, "CosmosClient", MagicMock(return_value=client))
    case = cls(method)

    def body():
        if failure == "body":
            raise AssertionError("body failed")

    async def async_body():
        body()

    setattr(case, method, async_body if asynchronous else body)
    result = unittest.TestResult()
    case.run(result)
    failed = failure not in (None, "container-create") or failure == "container-create" and creates_container
    assert result.wasSuccessful() is not failed
    assert events == ([] if failure == "conflict" else [("delete", attempted[0])]) + [("close", None)]
    client.close.assert_called_once()
    if asynchronous:
        client.close.assert_awaited_once()
    if failure == "body":
        assert len(result.failures) == 1
    elif failed:
        assert len(result.errors) == 1
