# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the request-scoped platform context."""
from __future__ import annotations

import asyncio

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import FOUNDRY_CALL_ID, USER_ID


class TestRequestContext:
    def test_default_is_empty(self) -> None:
        ctx = get_request_context()
        assert ctx.call_id is None
        assert ctx.user_id is None
        assert ctx.session_id is None

    def test_set_and_reset(self) -> None:
        token = set_request_context(
            FoundryAgentRequestContext(call_id="c1", user_id="u1", session_id="s1")
        )
        try:
            ctx = get_request_context()
            assert ctx.call_id == "c1"
            assert ctx.user_id == "u1"
            assert ctx.session_id == "s1"
        finally:
            reset_request_context(token)
        assert get_request_context().call_id is None

    def test_platform_headers_includes_call_id(self) -> None:
        ctx = FoundryAgentRequestContext(call_id="cid", user_id="uid")
        headers = ctx.platform_headers()
        # Only the call ID is forwarded to 1P services; user_id is not.
        assert headers == {FOUNDRY_CALL_ID: "cid"}
        assert USER_ID not in headers

    def test_platform_headers_omits_absent_values(self) -> None:
        assert FoundryAgentRequestContext().platform_headers() == {}
        # user_id alone never produces an outbound header.
        assert FoundryAgentRequestContext(user_id="uid").platform_headers() == {}
        assert FoundryAgentRequestContext(call_id="cid").platform_headers() == {FOUNDRY_CALL_ID: "cid"}

    def test_context_propagates_into_child_task(self) -> None:
        async def _run() -> FoundryAgentRequestContext:
            set_request_context(FoundryAgentRequestContext(call_id="task-cid", user_id="task-uid"))

            async def _child() -> FoundryAgentRequestContext:
                return get_request_context()

            # Child task created in this scope inherits the current context.
            return await asyncio.create_task(_child())

        ctx = asyncio.run(_run())
        assert ctx.call_id == "task-cid"
        assert ctx.user_id == "task-uid"
