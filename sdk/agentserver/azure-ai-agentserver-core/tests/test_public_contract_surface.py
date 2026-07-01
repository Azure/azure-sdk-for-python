# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public surface for the shared platform wire-contract: the
``azure.ai.agentserver.core.platform_headers`` re-export module and the
``read_request_id`` ASGI-scope helper.

These exist so composed protocol packages (responses, invocations) consume the
platform header constants and the resolved request id through supported public
API instead of reaching into core private modules.
"""
from __future__ import annotations

import azure.ai.agentserver.core as core
from azure.ai.agentserver.core import platform_headers, read_request_id
from azure.ai.agentserver.core import _platform_headers as _canonical


_SHARED_CONSTANTS = [
    "APIM_REQUEST_ID",
    "CLIENT_HEADER_PREFIX",
    "CLIENT_REQUEST_ID",
    "ERROR_DETAIL",
    "ERROR_SOURCE",
    "FOUNDRY_CALL_ID",
    "MAX_ERROR_DETAIL_LENGTH",
    "PLATFORM_ERROR_TAG",
    "REQUEST_ID",
    "SERVER_VERSION",
    "SESSION_ID",
    "TRACEPARENT",
    "USER_ID",
]


class TestPlatformHeadersModule:
    def test_module_exports_shared_constants(self) -> None:
        for name in _SHARED_CONSTANTS:
            assert name in platform_headers.__all__, name
            assert hasattr(platform_headers, name), name

    def test_values_match_canonical(self) -> None:
        for name in _SHARED_CONSTANTS:
            assert getattr(platform_headers, name) == getattr(_canonical, name), name

    def test_known_wire_header_values(self) -> None:
        assert platform_headers.REQUEST_ID == "x-request-id"
        assert platform_headers.CLIENT_REQUEST_ID == "x-ms-client-request-id"
        assert platform_headers.APIM_REQUEST_ID == "apim-request-id"


class TestReadRequestId:
    def test_exported_from_core(self) -> None:
        assert read_request_id is core.read_request_id
        assert "read_request_id" in core.__all__

    def test_reads_resolved_id_from_scope_state(self) -> None:
        from azure.ai.agentserver.core._request_id import REQUEST_ID_STATE_KEY

        scope = {"state": {REQUEST_ID_STATE_KEY: "req-123"}}
        assert read_request_id(scope) == "req-123"

    def test_returns_none_when_state_absent(self) -> None:
        assert read_request_id({}) is None

    def test_returns_none_when_key_absent(self) -> None:
        assert read_request_id({"state": {}}) is None
