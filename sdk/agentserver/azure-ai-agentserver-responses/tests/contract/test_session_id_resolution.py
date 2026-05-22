# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for session ID resolution (B39).

Priority: request payload ``agent_session_id`` → ``FOUNDRY_AGENT_SESSION_ID``
env var → deterministic SHA-256 derivation → random hex.
The resolved session ID MUST be auto-stamped on the
``ResponseObject.agent_session_id``.

Python port of SessionIdResolutionTests.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any
from unittest.mock import patch

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ════════════════════════════════════════════════════════════
# Shared helpers
# ════════════════════════════════════════════════════════════


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler — emits no events (framework auto-completes)."""

    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _simple_text_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created + completed."""

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _build_client(handler: Any | None = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE lines from a streaming response into a list of event dicts."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


def _wait_for_terminal(
    client: TestClient,
    response_id: str,
    *,
    timeout_s: float = 5.0,
) -> dict[str, Any]:
    """Poll GET until the response reaches a terminal status."""
    latest: dict[str, Any] = {}
    terminal_statuses = {"completed", "failed", "incomplete", "cancelled"}

    def _is_terminal() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in terminal_statuses

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=timeout_s,
        interval_s=0.05,
        context_provider=lambda: {"status": latest.get("status")},
        label=f"wait_for_terminal({response_id})",
    )
    assert ok, failure
    return latest


# ════════════════════════════════════════════════════════════
# Tier 1: Payload agent_session_id takes priority
# ════════════════════════════════════════════════════════════


class TestPayloadSessionId:
    """Payload agent_session_id is stamped on the response."""

    def test_default_payload_session_id_stamped_on_response(self) -> None:
        """B39 P1: non-streaming response carries the payload session ID."""
        session_id = "my-session-from-payload"
        client = _build_client()

        response = client.post(
            "/responses",
            json={
                "model": "test",
                "agent_session_id": session_id,
            },
        )

        assert response.status_code == 200
        assert response.json()["agent_session_id"] == session_id
        # §8: x-agent-session-id response header echoes the resolved value
        assert response.headers.get("x-agent-session-id") == session_id

    def test_streaming_payload_session_id_stamped_on_response(self) -> None:
        """B39 P1: streaming response.created and response.completed carry the payload session ID."""
        session_id = "streaming-session-xyz"
        client = _build_client(_simple_text_handler)

        with client.stream(
            "POST",
            "/responses",
            json={
                "model": "test",
                "stream": True,
                "agent_session_id": session_id,
            },
        ) as resp:
            assert resp.status_code == 200
            # §8: x-agent-session-id response header on streaming responses
            assert resp.headers.get("x-agent-session-id") == session_id
            events = _collect_sse_events(resp)

        # Check response.created event
        created_events = [e for e in events if e["type"] == "response.created"]
        assert len(created_events) == 1
        assert created_events[0]["data"]["response"]["agent_session_id"] == session_id

        # Check response.completed event
        completed_events = [e for e in events if e["type"] == "response.completed"]
        assert len(completed_events) == 1
        assert completed_events[0]["data"]["response"]["agent_session_id"] == session_id

    def test_background_payload_session_id_stamped_on_response(self) -> None:
        """B39 P1: background response carries the payload session ID.

        Background POST returns a queued snapshot immediately (before the handler
        runs), so agent_session_id is stamped once the handler processes. We poll
        GET to verify the session ID after completion.
        """
        session_id = "bg-session-abc"
        client = _build_client()

        response = client.post(
            "/responses",
            json={
                "model": "test",
                "background": True,
                "agent_session_id": session_id,
            },
        )
        assert response.status_code == 200
        response_id = response.json()["id"]

        terminal = _wait_for_terminal(client, response_id)
        assert terminal["agent_session_id"] == session_id


# ════════════════════════════════════════════════════════════
# Tier 2: Fallback to FOUNDRY_AGENT_SESSION_ID env var
# ════════════════════════════════════════════════════════════


class TestEnvVarFallback:
    """FOUNDRY_AGENT_SESSION_ID env var is used when no payload field."""

    def test_no_payload_session_id_falls_back_to_env_var(self) -> None:
        """B39 P2: env var used when no payload session ID."""
        env_session_id = "env-session-from-foundry"

        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            response = client.post(
                "/responses",
                json={"model": "test"},
            )

        assert response.status_code == 200
        assert response.json()["agent_session_id"] == env_session_id
        # §8: x-agent-session-id response header echoes the resolved value
        assert response.headers.get("x-agent-session-id") == env_session_id

    def test_payload_session_id_overrides_env_var(self) -> None:
        """B39: payload field takes precedence over env var."""
        payload_session_id = "payload-wins"
        env_session_id = "env-loses"

        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            response = client.post(
                "/responses",
                json={
                    "model": "test",
                    "agent_session_id": payload_session_id,
                },
            )

        assert response.status_code == 200
        assert response.json()["agent_session_id"] == payload_session_id
        # §8: header echoes the resolved value (payload wins over env var)
        assert response.headers.get("x-agent-session-id") == payload_session_id


# ════════════════════════════════════════════════════════════
# Tier 3: Fallback to generated UUID
# ════════════════════════════════════════════════════════════


class TestGeneratedSessionIdFallback:
    """Generated session ID when no payload field or env var."""

    def test_no_payload_or_env_generates_session_id(self) -> None:
        """B39 P3: generated hex when nothing else is available."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove FOUNDRY_AGENT_SESSION_ID if present
            env = os.environ.copy()
            env.pop("FOUNDRY_AGENT_SESSION_ID", None)
            with patch.dict(os.environ, env, clear=True):
                client = _build_client()
                response = client.post(
                    "/responses",
                    json={"model": "test"},
                )

        assert response.status_code == 200
        session_id = response.json()["agent_session_id"]
        assert session_id is not None and session_id != ""
        # Verify it's a valid 63-char lowercase hex string
        assert len(session_id) == 63
        assert re.fullmatch(r"[0-9a-f]+", session_id)
        # §8: x-agent-session-id response header echoes generated value
        assert response.headers.get("x-agent-session-id") == session_id

    def test_generated_session_id_is_different_per_request(self) -> None:
        """B39 P3: generated session IDs are unique per request."""
        with patch.dict(os.environ, {}, clear=False):
            env = os.environ.copy()
            env.pop("FOUNDRY_AGENT_SESSION_ID", None)
            with patch.dict(os.environ, env, clear=True):
                client = _build_client()
                response1 = client.post(
                    "/responses",
                    json={"model": "test"},
                )
                response2 = client.post(
                    "/responses",
                    json={"model": "test"},
                )

        session_id1 = response1.json()["agent_session_id"]
        session_id2 = response2.json()["agent_session_id"]
        assert session_id1 != session_id2, "Generated session IDs should be unique per request"


# ════════════════════════════════════════════════════════════
# Cross-mode consistency
# ════════════════════════════════════════════════════════════


class TestCrossModeConsistency:
    """Session ID stamping works consistently across modes."""

    def test_streaming_no_payload_or_env_stamps_generated_session_id(self) -> None:
        """B39: streaming mode generates and stamps a hex session ID."""
        with patch.dict(os.environ, {}, clear=False):
            env = os.environ.copy()
            env.pop("FOUNDRY_AGENT_SESSION_ID", None)
            with patch.dict(os.environ, env, clear=True):
                client = _build_client(_simple_text_handler)
                with client.stream(
                    "POST",
                    "/responses",
                    json={"model": "test", "stream": True},
                ) as resp:
                    assert resp.status_code == 200
                    # §8: header present even for generated session IDs
                    header_sid = resp.headers.get("x-agent-session-id")
                    assert header_sid is not None and header_sid != ""
                    events = _collect_sse_events(resp)

        completed_events = [e for e in events if e["type"] == "response.completed"]
        assert len(completed_events) == 1
        session_id = completed_events[0]["data"]["response"]["agent_session_id"]
        assert session_id is not None and session_id != ""
        assert len(session_id) == 63
        assert re.fullmatch(r"[0-9a-f]+", session_id)
        # Header must match the body session ID
        assert header_sid == session_id

    def test_background_no_payload_or_env_stamps_generated_session_id(self) -> None:
        """B39: background mode generates and stamps a hex session ID."""
        with patch.dict(os.environ, {}, clear=False):
            env = os.environ.copy()
            env.pop("FOUNDRY_AGENT_SESSION_ID", None)
            with patch.dict(os.environ, env, clear=True):
                client = _build_client()
                response = client.post(
                    "/responses",
                    json={"model": "test", "background": True},
                )
                assert response.status_code == 200
                response_id = response.json()["id"]
                terminal = _wait_for_terminal(client, response_id)

        session_id = terminal["agent_session_id"]
        assert session_id is not None and session_id != ""
        assert len(session_id) == 63
        assert re.fullmatch(r"[0-9a-f]+", session_id)

    def test_background_streaming_payload_session_id_on_all_events(self) -> None:
        """B39: bg+streaming with payload session ID stamps all lifecycle events."""
        session_id = "bg-stream-session-42"
        client = _build_client(_simple_text_handler)

        with client.stream(
            "POST",
            "/responses",
            json={
                "model": "test",
                "stream": True,
                "background": True,
                "agent_session_id": session_id,
            },
        ) as resp:
            assert resp.status_code == 200
            events = _collect_sse_events(resp)

        # All response.* lifecycle events should have the session ID
        lifecycle_types = {
            "response.created",
            "response.in_progress",
            "response.completed",
            "response.failed",
            "response.incomplete",
        }
        lifecycle_events = [e for e in events if e["type"] in lifecycle_types]
        assert len(lifecycle_events) >= 1, "Expected at least one lifecycle event"

        for event in lifecycle_events:
            resp_payload = event["data"].get("response", event["data"])
            assert resp_payload.get("agent_session_id") == session_id, (
                f"Missing/wrong agent_session_id on {event['type']}"
            )

    def test_session_id_consistent_between_create_and_get(self) -> None:
        """B39: session ID on POST matches session ID on subsequent GET."""
        session_id = "consistent-session-check"
        client = _build_client()

        response = client.post(
            "/responses",
            json={
                "model": "test",
                "background": True,
                "agent_session_id": session_id,
            },
        )
        assert response.status_code == 200
        response_id = response.json()["id"]

        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["agent_session_id"] == session_id

    def test_session_id_consistent_between_create_and_sse_replay(self) -> None:
        """B39: session ID on create matches session ID in SSE replay events."""
        session_id = "replay-session-check"
        client = _build_client(_simple_text_handler)

        # Create bg+stream response
        with client.stream(
            "POST",
            "/responses",
            json={
                "model": "test",
                "stream": True,
                "background": True,
                "agent_session_id": session_id,
            },
        ) as resp:
            assert resp.status_code == 200
            create_events = _collect_sse_events(resp)

        # Extract response ID from creation events
        created = [e for e in create_events if e["type"] == "response.created"]
        assert len(created) == 1
        response_id = created[0]["data"]["response"]["id"]

        _wait_for_terminal(client, response_id)

        # SSE replay should carry the same session ID
        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200
            replay_events = _collect_sse_events(replay_resp)

        lifecycle_types = {"response.created", "response.completed"}
        for event in replay_events:
            if event["type"] in lifecycle_types:
                resp_payload = event["data"].get("response", event["data"])
                assert resp_payload.get("agent_session_id") == session_id, (
                    f"SSE replay {event['type']} missing agent_session_id"
                )


# ════════════════════════════════════════════════════════════
# §8: x-agent-session-id header on non-POST endpoints
# ════════════════════════════════════════════════════════════


class TestSessionIdHeaderOnNonPostEndpoints:
    """x-agent-session-id header MUST appear on all protocol endpoint responses (§8).

    Non-POST endpoints resolve the session ID from the
    ``FOUNDRY_AGENT_SESSION_ID`` environment variable.
    """

    def test_get_response_has_session_id_header(self) -> None:
        """GET /responses/{id} includes x-agent-session-id header."""
        env_session_id = "env-session-for-get"
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            create_resp = client.post("/responses", json={"model": "test"})
            assert create_resp.status_code == 200
            response_id = create_resp.json()["id"]

            get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.headers.get("x-agent-session-id") == env_session_id

    def test_delete_response_has_session_id_header(self) -> None:
        """DELETE /responses/{id} includes x-agent-session-id header."""
        env_session_id = "env-session-for-delete"
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            create_resp = client.post("/responses", json={"model": "test"})
            assert create_resp.status_code == 200
            response_id = create_resp.json()["id"]

            delete_resp = client.delete(f"/responses/{response_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.headers.get("x-agent-session-id") == env_session_id

    def test_cancel_response_has_session_id_header(self) -> None:
        """POST /responses/{id}/cancel includes x-agent-session-id header."""
        env_session_id = "env-session-for-cancel"
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            create_resp = client.post(
                "/responses",
                json={"model": "test", "background": True},
            )
            assert create_resp.status_code == 200
            response_id = create_resp.json()["id"]

            cancel_resp = client.post(f"/responses/{response_id}/cancel")
        # Cancel may return 200 (cancelled) or 400 (already completed) —
        # either way the header must be present.
        assert cancel_resp.headers.get("x-agent-session-id") == env_session_id

    def test_input_items_has_session_id_header(self) -> None:
        """GET /responses/{id}/input_items includes x-agent-session-id header."""
        env_session_id = "env-session-for-input-items"
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            create_resp = client.post(
                "/responses",
                json={
                    "model": "test",
                    "input": [{"role": "user", "content": "hi"}],
                },
            )
            assert create_resp.status_code == 200
            response_id = create_resp.json()["id"]

            items_resp = client.get(f"/responses/{response_id}/input_items")
        assert items_resp.status_code == 200
        assert items_resp.headers.get("x-agent-session-id") == env_session_id

    def test_error_response_has_session_id_header(self) -> None:
        """Error responses (e.g. 404) on protocol endpoints include the header."""
        env_session_id = "env-session-for-errors"
        from azure.ai.agentserver.responses._id_generator import IdGenerator

        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": env_session_id}):
            client = _build_client()
            unknown_id = IdGenerator.new_response_id()
            get_resp = client.get(f"/responses/{unknown_id}")
        assert get_resp.status_code == 404
        assert get_resp.headers.get("x-agent-session-id") == env_session_id
