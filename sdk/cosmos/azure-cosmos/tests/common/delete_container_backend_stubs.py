# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Helpers for container delete tests.

They send ``delete_container`` calls to a fake, so tests can check what would
have been sent, without a network.
"""

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
    """Set up a database object whose ``delete_container`` calls go to a fake.

    Returns the setup for one test case:
    - ``database``: the database to call ``delete_container`` on.
    - ``backend``: the fake. It replies "204 No Content". ``backend.execute`` is a
      mock, so a test can check how many requests were sent and what they contained.
    - ``connection``: ``ReadContainer`` and ``DeleteContainer`` fail the test if
      they are called. ``_set_container_properties_cache`` is a mock.
    - ``is_async``: whether ``database`` is the async version.
    """
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
            side_effect=AssertionError("delete_container should not read the container first")
        ),
        DeleteContainer=mock(side_effect=AssertionError("DeleteContainer should not be called")),
        _set_container_properties_cache=MagicMock(),
    )
    proxy_type = AsyncDatabaseProxy if is_async else DatabaseProxy
    return SimpleNamespace(
        database=proxy_type(connection, "db1"),
        connection=connection,
        backend=backend,
        is_async=is_async,
    )


def _call_container_delete(case, *args, **kwargs):
    """Call ``delete_container`` on the database and wait for it if the client is async."""
    result = case.database.delete_container(*args, **kwargs)
    return run_async(result) if inspect.isawaitable(result) else result


def _assert_no_request_sent(case):
    """Check that nothing was sent and the saved container properties were not touched.

    Tests use this after a call that must fail before any request is made, such as
    a call with an option that is no longer supported.
    """
    case.backend.execute.assert_not_called()
    case.connection.DeleteContainer.assert_not_called()
    case.connection.ReadContainer.assert_not_called()
    case.connection._set_container_properties_cache.assert_not_called()
