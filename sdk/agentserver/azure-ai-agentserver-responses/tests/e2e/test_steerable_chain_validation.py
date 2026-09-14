# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 013 US2 — Steerable chain validation E2E test (T-039).

Verifies the HTTP layer translation: when the resilient orchestrator raises
:class:`LastInputIdPreconditionFailed` (the framework's input-precondition
primitive at the core layer), the responses endpoint surfaces HTTP 409 with
the documented wire shape:
``{message, type: "conflict", code: "conversation_fork_not_supported",
param: "previous_response_id"}``.

The deep end-to-end (turn 1 → turn 2 valid → turn 3 stale → 409) is
covered by the core-layer unit tests in
:mod:`tests.tasks.test_input_precondition`. This file proves the wire
contract specifically.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import LastInputIdPreconditionFailed
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator


def _make_steerable_app(handler) -> TestClient:
    options = ResponsesServerOptions(
        resilient_background=True,
        steerable_conversations=True,
    )
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(handler)
    return TestClient(app)


def _base_payload(input_text: str = "hello", **overrides) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "test-model",
        "input": input_text,
        "store": True,
        "background": True,
    }
    payload.update(overrides)
    return payload


class TestSteerableChainValidationWireFormat:
    """Spec 013 US2 — HTTP 409 wire format on conversation fork."""

    def test_stale_predecessor_returns_409_with_documented_body(self) -> None:
        """When framework raises LastInputIdPreconditionFailed, endpoint returns 409 with the documented body."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="OK")

        client = _make_steerable_app(handler)

        # Patch `run_background` on the orchestrator to raise the precondition
        # failure on the second call. The exception path through the endpoint
        # handler is what we want to verify.
        from azure.ai.agentserver.responses.hosting._orchestrator import (
            _ResponseOrchestrator,
        )

        original_run_background = _ResponseOrchestrator.run_background
        call_count = {"n": 0}

        async def fake_run_background(self, ctx):  # type: ignore[no-untyped-def]
            call_count["n"] += 1
            if call_count["n"] == 2:
                raise LastInputIdPreconditionFailed(
                    "fake-task-id",
                    expected_last_input_id="resp-stale",
                    actual_last_input_id="resp-current",
                )
            return await original_run_background(self, ctx)

        with patch.object(
            _ResponseOrchestrator,
            "run_background",
            new=fake_run_background,
        ):
            # First call succeeds normally.
            r1 = client.post("/responses", json=_base_payload("turn 1"))
            assert r1.status_code == 200, r1.text

            # Second call triggers the patched exception path -> 409 with the
            # documented body shape.
            stale_id = IdGenerator.new_response_id()
            r2 = client.post(
                "/responses",
                json=_base_payload("turn 2", previous_response_id=stale_id),
            )

        assert r2.status_code == 409, (r2.status_code, r2.text)
        body = r2.json()
        err = body.get("error", body)
        assert err["type"] == "conflict"
        assert err["code"] == "conversation_fork_not_supported"
        assert err["param"] == "previous_response_id"
        assert isinstance(err["message"], str)
        # The message communicates that forks are not supported.
        msg = err["message"].lower()
        assert "fork" in msg or "not support" in msg or "most recent" in msg
