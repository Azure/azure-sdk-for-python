# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the request-scoped platform context."""
from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError

import httpx
import pytest
from starlette.datastructures import Headers

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    FoundryOriginalSubject,
    get_request_context,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import FOUNDRY_CALL_ID, USER_ID

SUBJECT_HEADERS = {
    "x-ms-original-subject-oid": "original-oid",
    "x-ms-original-subject-tid": "original-tid",
    "x-ms-original-subject-idtype": "user",
}


class TestOriginalSubject:
    def test_absent_subject_does_not_infer_from_state_or_call_id(self) -> None:
        context = FoundryAgentRequestContext(user_id="raw-state-user", call_id="opaque-call")
        assert context.original_subject is None
        assert context.model_attribution_headers() == {}
        assert FoundryOriginalSubject.from_headers(Headers({USER_ID: "raw-state-user"})) is None

    @pytest.mark.parametrize("idtype", ["user", "app", "unknown"])
    def test_model_headers_preserve_tuple_and_platform_headers_are_unchanged(self, idtype: str) -> None:
        expected = {**SUBJECT_HEADERS, "x-ms-original-subject-idtype": idtype}
        context = FoundryAgentRequestContext(
            original_subject=FoundryOriginalSubject.from_headers(Headers(expected)),
            call_id="opaque-call",
            user_id="different-state-key",
        )
        assert context.model_attribution_headers() == {**expected, FOUNDRY_CALL_ID: "opaque-call"}
        assert context.platform_headers() == {FOUNDRY_CALL_ID: "opaque-call"}
        copied = context.model_attribution_headers()
        copied["x-ms-original-subject-oid"] = "changed"
        assert context.model_attribution_headers()["x-ms-original-subject-oid"] == "original-oid"

    @pytest.mark.parametrize("invalid", [None, "", " ", "oid\r\ninjected", "\x00", "\N{SNOWMAN}"])
    def test_partial_or_unsafe_subject_is_preserved_but_cannot_be_forwarded(self, invalid: str | None) -> None:
        headers = dict(SUBJECT_HEADERS)
        if invalid is None:
            del headers["x-ms-original-subject-oid"]
        else:
            headers["x-ms-original-subject-oid"] = invalid
        subject = FoundryOriginalSubject.from_headers(headers)
        assert subject is not None
        assert subject.oid == invalid
        with pytest.raises(ValueError, match="complete, HTTP-safe tuple"):
            FoundryAgentRequestContext(original_subject=subject).model_attribution_headers()

    def test_snapshot_is_immutable_and_does_not_print_identifiers(self) -> None:
        subject = FoundryOriginalSubject(oid="private-original-oid", tid="tenant", idtype="user")
        with pytest.raises(FrozenInstanceError):
            setattr(subject, "oid", "different")
        assert "private-original-oid" not in repr(subject)

    @pytest.mark.asyncio
    async def test_shared_client_parallel_users_and_retries_keep_per_call_headers(self) -> None:
        both_bound = asyncio.Event()
        bound = 0
        attempts: dict[str, int] = {}
        observed: list[httpx.Headers] = []

        def receive(request: httpx.Request) -> httpx.Response:
            observed.append(request.headers.copy())
            oid = request.headers["x-ms-original-subject-oid"]
            attempts[oid] = attempts.get(oid, 0) + 1
            return httpx.Response(503 if attempts[oid] == 1 else 200)

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(receive),
            headers={"Authorization": "Bearer model-agent-token"},
        ) as client:
            async def invoke(user: str) -> None:
                nonlocal bound
                token = set_request_context(FoundryAgentRequestContext(
                    original_subject=FoundryOriginalSubject(oid=user, tid=f"tenant-{user}", idtype="user"),
                    call_id=f"call-{user}",
                ))
                try:
                    bound += 1
                    if bound == 2:
                        both_bound.set()
                    await both_bound.wait()
                    for _ in range(2):
                        response = await client.post(
                            "https://model.test/responses",
                            headers=get_request_context().model_attribution_headers(),
                            json={"input": "test"},
                        )
                    assert response.status_code == 200
                finally:
                    reset_request_context(token)
                assert get_request_context().original_subject is None

            await asyncio.gather(invoke("alice"), invoke("bob"))
            assert "x-ms-original-subject-oid" not in client.headers

        assert attempts == {"alice": 2, "bob": 2}
        for headers in observed:
            user = headers["x-ms-original-subject-oid"]
            assert headers["x-ms-original-subject-tid"] == f"tenant-{user}"
            assert headers[FOUNDRY_CALL_ID] == f"call-{user}"
            assert headers["authorization"] == "Bearer model-agent-token"
            assert USER_ID not in headers
        assert get_request_context().original_subject is None


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
