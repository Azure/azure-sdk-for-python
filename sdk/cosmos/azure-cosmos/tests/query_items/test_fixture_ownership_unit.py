# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async query fixtures must release owned resources even when setup or cleanup fails."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import exceptions


@pytest.mark.parametrize("failure,expected", [
    ("key-enter", ["key-close"]),
    ("data-factory", ["key-close"]),
    ("data-enter", ["data-close", "key-close"]),
    ("database-conflict", ["data-close", "key-close"]),
    ("database-proxy", ["database-delete", "data-close", "key-close"]),
    ("database-delete", ["body", "database-delete", "data-close", "key-close"]),
    ("data-close", ["body", "database-delete", "data-close", "key-close"]),
])
def test_async_subpartition_fixture_releases_owned_resources_rust(monkeypatch, failure, expected):
    path = Path(__file__).parent / "aio" / "test_crud_subpartition_async.py"
    spec = importlib.util.spec_from_file_location("query_subpartition_fixture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    key_client = MagicMock()
    data_client = MagicMock()
    events = []

    def cleanup(stage):
        def run(*_args):
            events.append(stage)
            if failure == stage:
                raise RuntimeError(stage)
        return run

    key_client.__aenter__ = AsyncMock(
        side_effect=RuntimeError(failure) if failure == "key-enter" else None,
    )
    key_client.create_database = AsyncMock(return_value=MagicMock())
    key_client.delete_database = AsyncMock(side_effect=cleanup("database-delete"))
    key_client.close = AsyncMock(side_effect=cleanup("key-close"))
    data_client.__aenter__ = AsyncMock(
        side_effect=RuntimeError(failure) if failure == "data-enter" else None,
    )
    data_client.close = AsyncMock(side_effect=cleanup("data-close"))
    if failure == "database-conflict":
        key_client.create_database.side_effect = exceptions.CosmosResourceExistsError(status_code=409)
    if failure == "database-proxy":
        data_client.get_database_client.side_effect = RuntimeError(failure)
    monkeypatch.setattr(module, "create_setup_client_async", MagicMock(return_value=key_client))
    monkeypatch.setattr(module, "create_data_client_async", MagicMock(
        return_value=data_client,
        side_effect=RuntimeError(failure) if failure == "data-factory" else None,
    ))
    method = "test_partitioned_collection_document_crud_and_query_subpartition_async_rust"
    case = module.TestSubpartitionCrudAsync(method)

    async def body():
        events.append("body")

    setattr(case, method, body)
    result = unittest.TestResult()
    case.run(result)

    assert len(result.errors) == 1
    assert not result.failures
    assert events == expected
    if "database-delete" in expected:
        key_client.delete_database.assert_awaited_once_with(case._db_id)
    else:
        key_client.delete_database.assert_not_awaited()
