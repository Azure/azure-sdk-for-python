# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Throughput fixtures must clean up after failures without deleting unowned resources."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from common import throughput_fixtures

from azure.cosmos import exceptions


def load(path):
    spec = importlib.util.spec_from_file_location("throughput_fixture_" + path.parent.name + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_fixture_outcome(action, failure):
    expected_error = {
        "database-create": "creation failed", "conflict": "Conflict",
        "container-create": "container failed", "body": "body failed",
        "delete": "cleanup failed", "body-and-delete": "cleanup failed", "close": "close failed",
    }.get(failure)
    if expected_error is None:
        action()
        return
    error_type = exceptions.CosmosResourceExistsError if failure == "conflict" else (
        AssertionError if failure == "body" else RuntimeError
    )
    with pytest.raises(error_type) as caught:
        action()
    if failure != "conflict":
        assert expected_error in str(caught.value)
    if failure == "body-and-delete":
        chain = []
        error = caught.value
        while error is not None:
            chain.append(str(error))
            error = error.__context__
        assert "body failed" in chain


@pytest.mark.parametrize("selection", ["read", "manual", "autoscale", "full-read"])
@pytest.mark.parametrize("failure", [
    None, "database-create", "conflict", "container-create", "body", "delete",
    "body-and-delete", "missing", "close",
])
def test_parity_fixture_owns_resources_and_surfaces_errors_rust(monkeypatch, selection, failure):
    monkeypatch.setenv("ACCOUNT_HOST", "https://unused.invalid")
    monkeypatch.setenv("ACCOUNT_KEY", "unused")
    client = MagicMock()
    client.__enter__.return_value = client
    factory = MagicMock(return_value=client)
    module = throughput_fixtures if selection != "full-read" else load(
        Path(__file__).with_name("test_container_throughput_parity.py"),
    )
    monkeypatch.setattr(module, "CosmosClient", factory)
    attempted = []
    events = []
    database = MagicMock()
    containers = []

    def create_database(*, id, **_kwargs):
        attempted.append(id)
        database.id = id
        if failure == "database-create":
            raise RuntimeError("creation failed")
        if failure == "conflict":
            raise exceptions.CosmosResourceExistsError(status_code=409)
        return database

    def create_container(id, **_kwargs):
        containers.append(id)
        if failure == "container-create" and len(containers) == (1 if selection == "read" else 2):
            raise RuntimeError("container failed")
        return MagicMock(id=id)

    def delete(database_id):
        events.append(("delete", database_id))
        if failure in ("delete", "body-and-delete"):
            raise RuntimeError("cleanup failed")
        if failure == "missing":
            raise exceptions.CosmosResourceNotFoundError(status_code=404)

    def close(*_args):
        events.append(("close", None))
        if failure == "close":
            raise RuntimeError("close failed")
        return False

    client.create_database.side_effect = create_database
    database.create_container.side_effect = create_container
    client.delete_database.side_effect = delete
    client.__exit__.side_effect = close
    fixture = {
        "read": throughput_fixtures.shared_container_for,
        "manual": throughput_fixtures.container_for,
        "autoscale": throughput_fixtures.autoscale_container_for,
        "full-read": getattr(module, "throughput_resources", None),
    }[selection].__wrapped__()

    def use():
        resources = next(fixture)
        expected = {
            "read": (attempted[0], "orders"), "full-read": database,
        }.get(selection, (attempted[0], {"core-python": "corepython", "rust": "rust"}))
        assert resources == expected
        if failure in ("body", "body-and-delete"):
            fixture.throw(AssertionError("body failed"))
        else:
            with pytest.raises(StopIteration):
                next(fixture)

    assert_fixture_outcome(use, failure)
    assert len(attempted) == 1
    assert events == ([] if failure == "conflict" else [("delete", attempted[0])]) + [("close", None)]
    factory.assert_called_once_with("https://unused.invalid", "unused", _backend="rust")
    if not failure:
        assert len(containers) == {"read": 1, "manual": 2, "autoscale": 2, "full-read": 3}[selection]


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
    module = load(Path(__file__).parent / ("aio" if asynchronous else "sync") / "legacy" / filename)
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
