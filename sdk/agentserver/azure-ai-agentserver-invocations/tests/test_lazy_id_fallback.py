# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""UUID generation occurs only when an invocation/session ID needs a fallback."""

import asyncio
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from azure.ai.agentserver.invocations import _invocation


@pytest.mark.parametrize("value", ["valid-id", "a" * _invocation._MAX_ID_LENGTH])
def test_valid_identifier_never_generates_uuid(value):
    with patch.object(_invocation.uuid, "uuid4") as generate:
        assert _invocation._sanitize_id(value) == value
        assert _invocation._sanitize_id(value, "fallback") == value
    generate.assert_not_called()


@pytest.mark.parametrize("value", ["", "bad id!", "a" * (_invocation._MAX_ID_LENGTH + 1)])
def test_invalid_identifier_generates_one_uuid_when_no_fallback_supplied(value):
    generated = uuid.UUID("11111111-1111-4111-8111-111111111111")
    with patch.object(_invocation.uuid, "uuid4", return_value=generated) as generate:
        assert _invocation._sanitize_id(value) == str(generated)
    generate.assert_called_once_with()


@pytest.mark.parametrize("fallback", ["", "literal-invalid fallback"])
def test_explicit_fallback_retains_existing_get_cancel_behavior(fallback):
    with patch.object(_invocation.uuid, "uuid4") as generate:
        assert _invocation._sanitize_id("bad id!", fallback) == fallback
    generate.assert_not_called()


def _request(invocation_id, query):
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/invocations",
            "headers": [(_invocation.InvocationConstants.INVOCATION_ID_HEADER.encode(), invocation_id.encode())],
            "query_string": query.encode(),
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invocation_id,query,configured,expected_calls,expected_session",
    [
        ("valid-id", "agent_session_id=query-session", "config-session", 0, "query-session"),
        ("", "agent_session_id=query-session", "", 1, "query-session"),
        ("valid-id", "", "config-session", 0, "config-session"),
        ("valid-id", "agent_session_id=", "config-session", 0, "config-session"),
        ("valid-id", "agent_session_id=bad%20id!", "config-session", 1, None),
        ("bad id!", "", "", 2, None),
    ],
)
async def test_post_endpoint_generates_only_needed_fallbacks(
    invocation_id, query, configured, expected_calls, expected_session
):
    request = _request(invocation_id, query)
    host = SimpleNamespace(
        config=SimpleNamespace(session_id=configured),
        _dispatch_invoke=AsyncMock(return_value=JSONResponse({"ok": True})),
    )
    real_uuid = uuid.uuid4
    with patch.object(_invocation.uuid, "uuid4", wraps=real_uuid) as generate:
        result = await _invocation.InvocationAgentServerHost._create_invocation_endpoint(host, request)
    assert result.status_code == 200
    assert generate.call_count == expected_calls
    assert result.headers[_invocation.InvocationConstants.SESSION_ID_HEADER] == request.state.session_id
    if expected_session is not None:
        assert request.state.session_id == expected_session
    else:
        assert str(uuid.UUID(request.state.session_id)) == request.state.session_id
    if invocation_id == "valid-id":
        assert request.state.invocation_id == invocation_id
    else:
        assert str(uuid.UUID(request.state.invocation_id)) == request.state.invocation_id


@pytest.mark.asyncio
async def test_concurrent_requests_receive_distinct_fallback_ids():
    host = SimpleNamespace(
        config=SimpleNamespace(session_id=""),
        _dispatch_invoke=AsyncMock(side_effect=lambda _: JSONResponse({"ok": True})),
    )
    first, second = _request("", ""), _request("", "")

    await asyncio.gather(
        _invocation.InvocationAgentServerHost._create_invocation_endpoint(host, first),
        _invocation.InvocationAgentServerHost._create_invocation_endpoint(host, second),
    )

    assert (
        len({first.state.invocation_id, first.state.session_id, second.state.invocation_id, second.state.session_id})
        == 4
    )
