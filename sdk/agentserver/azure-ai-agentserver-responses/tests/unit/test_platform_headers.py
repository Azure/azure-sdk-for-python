# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for PlatformHeaders constants."""

from __future__ import annotations

from azure.ai.agentserver.core._platform_headers import (
    APIM_REQUEST_ID,
    CLIENT_HEADER_PREFIX,
    CLIENT_REQUEST_ID,
    FOUNDRY_CALL_ID,
    REQUEST_ID,
    SERVER_VERSION,
    SESSION_ID,
    TRACEPARENT,
    USER_ID,
)
from azure.ai.agentserver.core._request_id import REQUEST_ID_STATE_KEY


class TestPlatformHeaderConstants:
    """Ensure header constants match expected wire values."""

    def test_request_id(self) -> None:
        assert REQUEST_ID == "x-request-id"

    def test_server_version(self) -> None:
        assert SERVER_VERSION == "x-platform-server"

    def test_session_id(self) -> None:
        assert SESSION_ID == "x-agent-session-id"

    def test_user_id(self) -> None:
        assert USER_ID == "x-agent-user-id"

    def test_foundry_call_id(self) -> None:
        assert FOUNDRY_CALL_ID == "x-agent-foundry-call-id"

    def test_client_header_prefix(self) -> None:
        assert CLIENT_HEADER_PREFIX == "x-client-"

    def test_traceparent(self) -> None:
        assert TRACEPARENT == "traceparent"

    def test_client_request_id(self) -> None:
        assert CLIENT_REQUEST_ID == "x-ms-client-request-id"

    def test_apim_request_id(self) -> None:
        assert APIM_REQUEST_ID == "apim-request-id"

    def test_request_id_state_key(self) -> None:
        assert REQUEST_ID_STATE_KEY == "agentserver.request_id"
