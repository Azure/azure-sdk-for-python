# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Temporary legacy database-read checks, retained until legacy removal.

Run explicitly with --include-legacy-tests. Maintained Rust coverage lives in
test_read_database_backend_unit.py and does not import this module.
"""

import asyncio
import warnings
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from common.database_backend_stubs import _call_database_read, make_database_read_case
from azure.core import MatchConditions
from azure.core.utils import CaseInsensitiveDict
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._cosmos_client_connection import (
    CosmosClientConnection as SyncClientConnection,
)
from azure.cosmos._cosmos_responses import CosmosDict
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos.aio._cosmos_client_connection_async import (
    CosmosClientConnection as AsyncClientConnection,
)


@pytest.fixture(params=["sync", "async"])
def database_read_case(request):
    """Configure only the temporary legacy cases to use the old backend."""
    is_async = request.param == "async"
    case = make_database_read_case(is_async)
    connection = case.connection
    connection._backend = ASYNC_LEGACY_BACKEND if is_async else LEGACY_BACKEND

    def legacy_read(*args, **kwargs):
        headers = CaseInsensitiveDict(
            {"x-ms-activity-id": "read-one", "x-ms-request-charge": "1.5"}
        )
        body = {"id": "db1", "_etag": "v1"}
        connection.last_response_headers = headers
        result = CosmosDict(body, response_headers=headers)
        hook = kwargs.get("response_hook")
        if hook:
            hook(headers, body)
        return result

    connection.ReadDatabase = (AsyncMock if is_async else MagicMock)(
        side_effect=legacy_read
    )
    return case


def test_sync_connection_read_database_forwards_initial_headers_legacy():
    """Prove sync database reads preserve caller-supplied initial headers."""
    connection = SimpleNamespace(
        Read=MagicMock(return_value={"id": "db1"}),
        default_headers={
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
        },
    )
    options = {"initialHeaders": {"x-custom": "value"}}

    result = SyncClientConnection.ReadDatabase(
        connection,
        "dbs/db1",
        options=options,
    )

    assert result == {"id": "db1"}
    connection.Read.assert_called_once_with(
        "/dbs/db1/",
        "dbs",
        "dbs/db1",
        {
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
            "x-custom": "value",
        },
        options,
    )


@pytest.mark.parametrize(
    "option,key",
    [
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
    ],
)
@pytest.mark.parametrize(
    "source,other_source",
    [
        ("keyword", None),
        ("request_options", None),
        ("feed_options", None),
        ("request_options", "feed_options"),
        ("feed_options", "request_options"),
    ],
)
@pytest.mark.parametrize("value", [None, False, True, "unused"])
def test_database_read_rejects_obsolete_and_socket_options_legacy(
    database_read_case, option, key, source, other_source, value
):
    """Reject retired options before dispatch without changing caller dictionaries or cached properties."""
    case = database_read_case
    hook = MagicMock()
    kwargs = {option: value} if source == "keyword" else {source: {key: value}}
    if other_source is not None:
        kwargs[other_source] = {}
    original = deepcopy(kwargs)
    with pytest.raises(TypeError, match=option):
        _call_database_read(case, response_hook=hook, **kwargs)
    assert kwargs == original
    hook.assert_not_called()
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()
    assert case.proxy._properties["_etag"] == "old"


def test_database_read_hook_snapshot_is_isolated_and_falsey_callable_runs_legacy(
    database_read_case,
):
    """Run even a falsey callable once and isolate its header snapshot from later changes."""
    case = database_read_case
    calls = []

    class Hook:

        def __bool__(self):
            return False

        def __call__(self, headers, body):
            assert headers["X-MS-ACTIVITY-ID"] == "read-one"
            assert body == {"id": "db1", "_etag": "v1"}
            assert type(body) is dict
            calls.append(headers)
            headers["x-ms-request-charge"] = "modified"
            assert case.connection.last_response_headers["x-ms-request-charge"] == "1.5"

    result = _call_database_read(case, response_hook=Hook())
    assert len(calls) == 1
    assert result.get_response_headers()["x-ms-request-charge"] == "1.5"
    assert calls[0] is not result.get_response_headers()
    assert calls[0] is not case.connection.last_response_headers
    case.connection.last_response_headers["x-ms-activity-id"] = "later"
    assert calls[0]["x-ms-activity-id"] == "read-one"
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_called_once()


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {}),
        (
            {"etag": "v1", "match_condition": MatchConditions.IfNotModified},
            {"If-Match": "v1"},
        ),
        (
            {"etag": "v1", "match_condition": MatchConditions.IfModified},
            {"If-None-Match": "v1"},
        ),
        ({"match_condition": MatchConditions.IfPresent}, {"If-Match": "*"}),
        ({"match_condition": MatchConditions.IfMissing}, {"If-None-Match": "*"}),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfPresent},
            {"If-Match": "*"},
        ),
        (
            {"etag": "unused", "match_condition": MatchConditions.IfMissing},
            {"If-None-Match": "*"},
        ),
        ({"if_match": "v1"}, {"If-Match": "v1"}),
        ({"if_none_match": "v1"}, {"If-None-Match": "v1"}),
    ],
)
def test_database_read_preserves_conditional_headers_legacy(
    database_read_case, kwargs, expected
):
    """Preserve conditional headers, ignoring an unnecessary ETag for wildcard conditions."""
    from common.typed_requests import flatten_options_to_headers

    case = database_read_case
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _call_database_read(case, **kwargs)
    assert caught == []
    call = case.connection.ReadDatabase.call_args
    headers = flatten_options_to_headers(call.kwargs["options"])
    assert "etag" not in call.kwargs
    case.backend.execute.assert_not_called()
    assert {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() in ("if-match", "if-none-match")
    } == {key.lower(): value for key, value in expected.items()}


@pytest.mark.parametrize(
    "kwargs, error_type",
    [
        ({"etag": "v1"}, ValueError),
        ({"match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"match_condition": MatchConditions.IfModified}, ValueError),
        ({"etag": "", "match_condition": MatchConditions.IfNotModified}, ValueError),
        ({"etag": "v1", "match_condition": "invalid"}, TypeError),
    ],
)
def test_database_read_invalid_guards_fail_before_dispatch_legacy(
    database_read_case, kwargs, error_type
):
    """Reject incomplete or malformed conditions before sending a request."""
    case = database_read_case
    with pytest.raises(error_type):
        _call_database_read(case, **kwargs)
    case.backend.execute.assert_not_called()
    case.connection.ReadDatabase.assert_not_called()


def test_async_connection_read_database_forwards_initial_headers_legacy():
    """Prove async database reads preserve caller-supplied initial headers."""

    async def run():
        """Call ``AsyncClientConnection.ReadDatabase`` and verify caller headers are merged into the upstream call."""
        connection = SimpleNamespace(Read=AsyncMock(return_value={"id": "db1"}))
        connection.default_headers = {
            "x-ms-version": "2020-07-15",
            "Cache-Control": "no-cache",
        }
        options = {"initialHeaders": {"x-custom": "value"}}

        result = await AsyncClientConnection.ReadDatabase(
            connection,
            "dbs/db1",
            options=options,
        )

        assert result == {"id": "db1"}
        connection.Read.assert_awaited_once_with(
            "/dbs/db1/",
            "dbs",
            "dbs/db1",
            {
                "x-ms-version": "2020-07-15",
                "Cache-Control": "no-cache",
                "x-custom": "value",
            },
            options,
        )

    asyncio.run(run())
