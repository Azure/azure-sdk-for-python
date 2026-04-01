# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for S-047 (Response ID Resolution) and S-048 (Session ID Resolution)."""

from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from azure.ai.agentserver.responses.hosting._request_parsing import (
    _resolve_identity_fields,
    _resolve_session_id,
)
from azure.ai.agentserver.responses.streaming._internals import (
    apply_common_defaults,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator


# ---------------------------------------------------------------------------
# Minimal stub for parsed CreateResponse
# ---------------------------------------------------------------------------

class _FakeParsed:
    """Minimal stub matching the CreateResponse model interface."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, "agent_reference"):
            self.agent_reference = None
        if not hasattr(self, "conversation"):
            self.conversation = None
        if not hasattr(self, "previous_response_id"):
            self.previous_response_id = None

    def as_dict(self):
        d = {}
        for key in ("response_id", "agent_reference", "conversation",
                     "previous_response_id", "agent_session_id"):
            if hasattr(self, key):
                d[key] = getattr(self, key)
        return d


# ===================================================================
# S-047: Response ID Resolution
# ===================================================================

class TestResponseIdResolution:
    """Tests for S-047 — x-agent-response-id header override."""

    def test_header_overrides_generated_id(self):
        """S-047: header value is used as response_id when present."""
        # Generate a valid response_id to use as header value
        valid_id = IdGenerator.new_response_id()
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed, request_headers={"x-agent-response-id": valid_id},
        )
        assert response_id == valid_id

    def test_header_overrides_payload_response_id(self):
        """S-047: header takes precedence over payload response_id."""
        header_id = IdGenerator.new_response_id()
        payload_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(response_id=payload_id)
        response_id, _ = _resolve_identity_fields(
            parsed, request_headers={"x-agent-response-id": header_id},
        )
        assert response_id == header_id

    def test_empty_header_falls_back_to_generated(self):
        """S-047: empty header causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed, request_headers={"x-agent-response-id": ""},
        )
        assert response_id.startswith("caresp_")

    def test_absent_header_falls_back_to_generated(self):
        """S-047: absent header causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed, request_headers={},
        )
        assert response_id.startswith("caresp_")

    def test_no_headers_arg_falls_back_to_generated(self):
        """S-047: no headers kwarg causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(parsed)
        assert response_id.startswith("caresp_")

    def test_payload_response_id_used_when_no_header(self):
        """S-047: payload response_id is used when header is absent."""
        payload_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(response_id=payload_id)
        response_id, _ = _resolve_identity_fields(
            parsed, request_headers={},
        )
        assert response_id == payload_id

    def test_invalid_header_format_raises(self):
        """S-047: malformed header value is rejected by response ID validation."""
        parsed = _FakeParsed()
        with pytest.raises(Exception):
            # "bad-id" doesn't conform to the caresp_ prefix + partition key + entropy format
            _resolve_identity_fields(
                parsed, request_headers={"x-agent-response-id": "bad-id"},
            )


# ===================================================================
# S-048: Session ID Resolution
# ===================================================================

class TestSessionIdResolution:
    """Tests for S-048 — agent_session_id priority chain."""

    def test_payload_field_highest_priority(self):
        """S-048 P1: request.agent_session_id payload field wins."""
        parsed = _FakeParsed(agent_session_id="session-from-payload")
        result = _resolve_session_id(parsed, {"agent_session_id": "session-from-raw-payload"})
        assert result == "session-from-payload"

    def test_raw_payload_used_when_model_missing_field(self):
        """S-048 P1: raw payload dict is used if parsed model lacks the field."""
        parsed = _FakeParsed()  # no agent_session_id attr
        result = _resolve_session_id(parsed, {"agent_session_id": "session-from-raw"})
        assert result == "session-from-raw"

    def test_env_var_second_priority(self):
        """S-048 P2: FOUNDRY_AGENT_SESSION_ID env var when no payload field."""
        parsed = _FakeParsed()
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "env-session-123"}):
            result = _resolve_session_id(parsed, {})
        assert result == "env-session-123"

    def test_generated_uuid_third_priority(self):
        """S-048 P3: generated UUID when no payload field or env var."""
        parsed = _FakeParsed()
        with patch.dict(os.environ, {}, clear=True):
            result = _resolve_session_id(parsed, {})
        # Should be a valid UUID
        uuid.UUID(result)  # raises ValueError if invalid

    def test_payload_overrides_env_var(self):
        """S-048: payload field takes precedence over env var."""
        parsed = _FakeParsed(agent_session_id="payload-session")
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "env-session"}):
            result = _resolve_session_id(parsed, {})
        assert result == "payload-session"

    def test_empty_payload_falls_to_env(self):
        """S-048: empty/whitespace payload field falls through to env var."""
        parsed = _FakeParsed(agent_session_id="  ")
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "env-fallback"}):
            result = _resolve_session_id(parsed, {})
        assert result == "env-fallback"

    def test_empty_env_falls_to_uuid(self):
        """S-048: empty env var falls through to generated UUID."""
        parsed = _FakeParsed()
        with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "  "}):
            result = _resolve_session_id(parsed, {})
        uuid.UUID(result)


# ===================================================================
# S-048: Session ID stamping on response.* events
# ===================================================================

class TestSessionIdStamping:
    """Tests for S-048 — agent_session_id auto-stamping on response events."""

    def test_session_id_stamped_on_response_created(self):
        """S-048: agent_session_id is stamped on response.created payload."""
        events = [
            {"type": "response.created", "payload": {"id": "resp_1", "status": "in_progress"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="test-session",
        )
        assert events[0]["payload"]["agent_session_id"] == "test-session"

    def test_session_id_stamped_on_response_completed(self):
        """S-048: agent_session_id is stamped on response.completed payload."""
        events = [
            {"type": "response.completed", "payload": {"id": "resp_1", "status": "completed"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="completed-session",
        )
        assert events[0]["payload"]["agent_session_id"] == "completed-session"

    def test_session_id_forcibly_stamped_overrides_handler(self):
        """S-048: agent_session_id is forcibly set, even if handler sets it."""
        events = [
            {
                "type": "response.created",
                "payload": {"id": "resp_1", "agent_session_id": "handler-set"},
            },
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="library-resolved",
        )
        # Library-resolved session ID overrides handler-set value
        assert events[0]["payload"]["agent_session_id"] == "library-resolved"

    def test_no_session_id_when_none(self):
        """S-048: no stamping when agent_session_id is None."""
        events = [
            {"type": "response.created", "payload": {"id": "resp_1"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id=None,
        )
        assert "agent_session_id" not in events[0]["payload"]

    def test_non_lifecycle_events_not_stamped(self):
        """S-048: non-response.* events are not stamped."""
        events = [
            {"type": "response.output_text.delta", "payload": {"text": "hello"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="should-not-appear",
        )
        assert "agent_session_id" not in events[0]["payload"]

    def test_session_id_stamped_on_all_lifecycle_types(self):
        """S-048: stamped on all response.* lifecycle event types."""
        lifecycle_types = [
            "response.queued",
            "response.created",
            "response.in_progress",
            "response.completed",
            "response.failed",
            "response.incomplete",
        ]
        for event_type in lifecycle_types:
            events = [{"type": event_type, "payload": {"id": "resp_1"}}]
            apply_common_defaults(
                events,
                response_id="resp_1",
                agent_reference=None,
                model=None,
                agent_session_id="all-types-session",
            )
            assert events[0]["payload"]["agent_session_id"] == "all-types-session", (
                f"Missing agent_session_id on {event_type}"
            )
