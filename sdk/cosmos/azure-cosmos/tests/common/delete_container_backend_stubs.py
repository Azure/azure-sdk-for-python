# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Deletion stand-ins with no dependency on the retiring legacy implementation."""

import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from common.async_test_helpers import run_async

from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.database import DatabaseProxy
from common.container_backend_stubs import _AsyncFakeBackend, _FakeBackend


def make_delete_case(is_async):
    mock = AsyncMock if is_async else MagicMock
    response = BackendResponse(
        status_code=204,
        headers=CaseInsensitiveDict(
            {"x-ms-request-charge": "3", "x-ms-activity-id": "delete"}
        ),
        body=b"",
        diagnostics="delete trace",
    )
    backend = (_AsyncFakeBackend if is_async else _FakeBackend)(response)
    backend.execute = mock(wraps=backend.execute)
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={},
        ReadContainer=mock(
            side_effect=AssertionError("Python must not fetch deletion metadata")
        ),
        DeleteContainer=mock(side_effect=AssertionError("Legacy deletion was called")),
        _set_container_properties_cache=MagicMock(),
    )
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    return SimpleNamespace(
        database=proxy_type(connection, "db1"),
        connection=connection,
        backend=backend,
        is_async=is_async,
    )


def _delete(case, *args, **kwargs):
    result = case.database.delete_container(*args, **kwargs)
    return run_async(result) if inspect.isawaitable(result) else result


def _assert_no_dispatch(case):
    case.backend.execute.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
