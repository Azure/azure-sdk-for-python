# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for PlatformHeaders constants."""

from __future__ import annotations

from azure.ai.agentserver.responses._platform_headers import (
    APIM_REQUEST_ID,
    CHAT_ISOLATION_KEY,
    CLIENT_HEADER_PREFIX,
    CLIENT_REQUEST_ID,
    REQUEST_ID,
    REQUEST_ID_ITEM_KEY,
    SERVER_VERSION,
    SESSION_ID,
    TRACEPARENT,
    USER_ISOLATION_KEY,
)


class TestPlatformHeaderConstants:
    """Ensure header constants match expected wire values."""

    def test_request_id(self) -> None:
        assert REQUEST_ID == "x-request-id"

    def test_server_version(self) -> None:
        assert SERVER_VERSION == "x-platform-server"

    def test_session_id(self) -> None:
        assert SESSION_ID == "x-agent-session-id"

    def test_user_isolation_key(self) -> None:
        assert USER_ISOLATION_KEY == "x-agent-user-isolation-key"

    def test_chat_isolation_key(self) -> None:
        assert CHAT_ISOLATION_KEY == "x-agent-chat-isolation-key"

    def test_client_header_prefix(self) -> None:
        assert CLIENT_HEADER_PREFIX == "x-client-"

    def test_traceparent(self) -> None:
        assert TRACEPARENT == "traceparent"

    def test_client_request_id(self) -> None:
        assert CLIENT_REQUEST_ID == "x-ms-client-request-id"

    def test_apim_request_id(self) -> None:
        assert APIM_REQUEST_ID == "apim-request-id"

    def test_request_id_item_key(self) -> None:
        assert REQUEST_ID_ITEM_KEY == "agentserver.request_id"
