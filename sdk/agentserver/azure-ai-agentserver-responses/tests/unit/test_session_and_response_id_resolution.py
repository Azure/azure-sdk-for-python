# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for B38 (Response ID Resolution) and B39 (Session ID Resolution)."""

from __future__ import annotations

import hashlib
import re

import pytest

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.hosting._request_parsing import (
    _compute_hex_hash,
    _resolve_identity_fields,
    _resolve_session_id,
    derive_session_id,
)
from azure.ai.agentserver.responses.streaming._internals import (
    apply_common_defaults,
)

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
        for key in ("response_id", "agent_reference", "conversation", "previous_response_id", "agent_session_id"):
            if hasattr(self, key):
                d[key] = getattr(self, key)
        return d


# ===================================================================
# B38: Response ID Resolution
# ===================================================================


class TestResponseIdResolution:
    """Tests for B38 — x-agent-response-id header override."""

    def test_header_overrides_generated_id(self):
        """B38: header value is used as response_id when present."""
        # Generate a valid response_id to use as header value
        valid_id = IdGenerator.new_response_id()
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed,
            request_headers={"x-agent-response-id": valid_id},
        )
        assert response_id == valid_id

    def test_header_overrides_payload_response_id(self):
        """B38: header takes precedence over payload response_id."""
        header_id = IdGenerator.new_response_id()
        payload_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(response_id=payload_id)
        response_id, _ = _resolve_identity_fields(
            parsed,
            request_headers={"x-agent-response-id": header_id},
        )
        assert response_id == header_id

    def test_empty_header_falls_back_to_generated(self):
        """B38: empty header causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed,
            request_headers={"x-agent-response-id": ""},
        )
        assert response_id.startswith("caresp_")

    def test_absent_header_falls_back_to_generated(self):
        """B38: absent header causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(
            parsed,
            request_headers={},
        )
        assert response_id.startswith("caresp_")

    def test_no_headers_arg_falls_back_to_generated(self):
        """B38: no headers kwarg causes library to generate a response ID."""
        parsed = _FakeParsed()
        response_id, _ = _resolve_identity_fields(parsed)
        assert response_id.startswith("caresp_")

    def test_payload_response_id_used_when_no_header(self):
        """B38: payload response_id is used when header is absent."""
        payload_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(response_id=payload_id)
        response_id, _ = _resolve_identity_fields(
            parsed,
            request_headers={},
        )
        assert response_id == payload_id

    def test_invalid_header_format_raises(self):
        """B38: malformed header value is rejected by response ID validation."""
        parsed = _FakeParsed()
        with pytest.raises(Exception):
            # "bad-id" doesn't conform to the caresp_ prefix + partition key + entropy format
            _resolve_identity_fields(
                parsed,
                request_headers={"x-agent-response-id": "bad-id"},
            )


# ===================================================================
# B39: Session ID Resolution
# ===================================================================


class TestSessionIdResolution:
    """Tests for B39 — agent_session_id priority chain."""

    def test_payload_field_highest_priority(self):
        """B39 P1: request.agent_session_id payload field wins."""
        parsed = _FakeParsed(agent_session_id="session-from-payload")
        result = _resolve_session_id(parsed, {"agent_session_id": "session-from-raw-payload"})
        assert result == "session-from-payload"

    def test_raw_payload_used_when_model_missing_field(self):
        """B39 P1: raw payload dict is used if parsed model lacks the field."""
        parsed = _FakeParsed()  # no agent_session_id attr
        result = _resolve_session_id(parsed, {"agent_session_id": "session-from-raw"})
        assert result == "session-from-raw"

    def test_env_var_second_priority(self):
        """B39 P2: env_session_id (from AgentConfig) when no payload field."""
        parsed = _FakeParsed()
        result = _resolve_session_id(parsed, {}, env_session_id="env-session-123")
        assert result == "env-session-123"

    def test_generated_uuid_third_priority(self):
        """B39 P3: random hex when no payload, env, or conversational context."""
        parsed = _FakeParsed()
        result = _resolve_session_id(parsed, {})
        # Should be a 63-char lowercase hex string
        assert len(result) == 63
        assert re.fullmatch(r"[0-9a-f]+", result)

    def test_payload_overrides_env_var(self):
        """B39: payload field takes precedence over env_session_id."""
        parsed = _FakeParsed(agent_session_id="payload-session")
        result = _resolve_session_id(parsed, {}, env_session_id="env-session")
        assert result == "payload-session"

    def test_empty_payload_falls_to_env(self):
        """B39: empty/whitespace payload field falls through to env_session_id."""
        parsed = _FakeParsed(agent_session_id="  ")
        result = _resolve_session_id(parsed, {}, env_session_id="env-fallback")
        assert result == "env-fallback"

    def test_empty_env_falls_to_random_hex(self):
        """B39: empty env_session_id falls through to random hex."""
        parsed = _FakeParsed()
        result = _resolve_session_id(parsed, {}, env_session_id="  ")
        assert len(result) == 63
        assert re.fullmatch(r"[0-9a-f]+", result)


# ===================================================================
# B39: Session ID stamping on response.* events
# ===================================================================


class TestSessionIdStamping:
    """Tests for B39 — agent_session_id auto-stamping on response events."""

    def test_session_id_stamped_on_response_created(self):
        """B39: agent_session_id is stamped on response.created event."""
        events = [
            {"type": "response.created", "response": {"id": "resp_1", "status": "in_progress"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="test-session",
        )
        assert events[0]["response"]["agent_session_id"] == "test-session"

    def test_session_id_stamped_on_response_completed(self):
        """B39: agent_session_id is stamped on response.completed event."""
        events = [
            {"type": "response.completed", "response": {"id": "resp_1", "status": "completed"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="completed-session",
        )
        assert events[0]["response"]["agent_session_id"] == "completed-session"

    def test_session_id_forcibly_stamped_overrides_handler(self):
        """B39: agent_session_id is forcibly set, even if handler sets it."""
        events = [
            {
                "type": "response.created",
                "response": {"id": "resp_1", "agent_session_id": "handler-set"},
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
        assert events[0]["response"]["agent_session_id"] == "library-resolved"

    def test_no_session_id_when_none(self):
        """B39: no stamping when agent_session_id is None."""
        events = [
            {"type": "response.created", "response": {"id": "resp_1"}},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id=None,
        )
        assert "agent_session_id" not in events[0]["response"]

    def test_non_lifecycle_events_not_stamped(self):
        """B39: non-response.* events are not stamped."""
        events = [
            {"type": "response.output_text.delta", "delta": "hello"},
        ]
        apply_common_defaults(
            events,
            response_id="resp_1",
            agent_reference=None,
            model=None,
            agent_session_id="should-not-appear",
        )
        assert "agent_session_id" not in events[0]

    def test_session_id_stamped_on_all_lifecycle_types(self):
        """B39: stamped on all response.* lifecycle event types."""
        lifecycle_types = [
            "response.queued",
            "response.created",
            "response.in_progress",
            "response.completed",
            "response.failed",
            "response.incomplete",
        ]
        for event_type in lifecycle_types:
            events = [{"type": event_type, "response": {"id": "resp_1"}}]
            apply_common_defaults(
                events,
                response_id="resp_1",
                agent_reference=None,
                model=None,
                agent_session_id="all-types-session",
            )
            assert events[0]["response"]["agent_session_id"] == "all-types-session", (
                f"Missing agent_session_id on {event_type}"
            )


# ===================================================================
# B39: Deterministic session ID derivation
# ===================================================================


class TestSessionIdDerivation:
    """Tests for deterministic session ID derivation from conversational context."""

    def test_conversation_id_produces_deterministic_hash(self):
        """Same conversation_id + agent identity → same session ID every time."""
        conv_id = IdGenerator.new_response_id()  # valid ID with partition key
        ref = {"name": "my-agent", "version": "1.0"}

        result1 = derive_session_id(conversation_id=conv_id, agent_reference=ref)
        result2 = derive_session_id(conversation_id=conv_id, agent_reference=ref)

        assert result1 == result2
        assert len(result1) == 63
        assert re.fullmatch(r"[0-9a-f]+", result1)

    def test_previous_response_id_produces_deterministic_hash(self):
        """Same previous_response_id + agent identity → same session ID."""
        prev_id = IdGenerator.new_response_id()
        ref = {"name": "agent-x", "version": "2.0"}

        result1 = derive_session_id(previous_response_id=prev_id, agent_reference=ref)
        result2 = derive_session_id(previous_response_id=prev_id, agent_reference=ref)

        assert result1 == result2
        assert len(result1) == 63

    def test_conversation_id_takes_priority_over_previous_response_id(self):
        """conversation_id is used as partition source when both are present."""
        conv_id = IdGenerator.new_response_id()
        prev_id = IdGenerator.new_response_id()
        ref = {"name": "agent", "version": "1"}

        conv_only = derive_session_id(conversation_id=conv_id, agent_reference=ref)
        both = derive_session_id(conversation_id=conv_id, previous_response_id=prev_id, agent_reference=ref)

        assert conv_only == both  # conversation_id wins

    def test_different_agents_produce_different_sessions(self):
        """Same conversation but different agent identity → different session IDs."""
        conv_id = IdGenerator.new_response_id()

        result_a = derive_session_id(
            conversation_id=conv_id,
            agent_reference={"name": "agent-a", "version": "1"},
        )
        result_b = derive_session_id(
            conversation_id=conv_id,
            agent_reference={"name": "agent-b", "version": "1"},
        )

        assert result_a != result_b

    def test_different_versions_produce_different_sessions(self):
        """Same agent name but different version → different session IDs."""
        conv_id = IdGenerator.new_response_id()

        result_v1 = derive_session_id(
            conversation_id=conv_id,
            agent_reference={"name": "agent", "version": "1.0"},
        )
        result_v2 = derive_session_id(
            conversation_id=conv_id,
            agent_reference={"name": "agent", "version": "2.0"},
        )

        assert result_v1 != result_v2

    def test_no_context_produces_random_hex(self):
        """No conversation_id or previous_response_id → random hex."""
        result1 = derive_session_id()
        result2 = derive_session_id()

        # Both are valid 63-char hex
        assert len(result1) == 63
        assert len(result2) == 63
        assert re.fullmatch(r"[0-9a-f]+", result1)
        assert re.fullmatch(r"[0-9a-f]+", result2)
        # Extremely unlikely to collide
        assert result1 != result2

    def test_none_agent_reference_uses_default_name(self):
        """When agent_reference is None, a default name is used in the hash."""
        conv_id = IdGenerator.new_response_id()
        result = derive_session_id(conversation_id=conv_id, agent_reference=None)
        assert len(result) == 63
        assert re.fullmatch(r"[0-9a-f]+", result)

    def test_compute_hex_hash_matches_sha256(self):
        """_compute_hex_hash produces expected SHA-256 output."""
        value = "my-agent:1.0:abc123"
        expected = hashlib.sha256(value.encode("utf-8")).hexdigest()[:63]
        assert _compute_hex_hash(value) == expected

    def test_resolve_session_id_derives_from_conversation_id(self):
        """_resolve_session_id uses conversation_id for deterministic derivation."""
        conv_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(conversation={"id": conv_id})
        ref = {"name": "test-agent", "version": "1.0"}

        result = _resolve_session_id(parsed, {}, agent_reference=ref)

        # Must be deterministic
        result2 = _resolve_session_id(parsed, {}, agent_reference=ref)
        assert result == result2
        assert len(result) == 63

    def test_resolve_session_id_derives_from_previous_response_id(self):
        """_resolve_session_id uses previous_response_id when no conversation."""
        prev_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(previous_response_id=prev_id)
        ref = {"name": "test-agent", "version": "2.0"}

        result = _resolve_session_id(parsed, {}, agent_reference=ref)

        result2 = _resolve_session_id(parsed, {}, agent_reference=ref)
        assert result == result2
        assert len(result) == 63

    def test_resolve_session_id_explicit_beats_derivation(self):
        """Explicit session ID in payload takes precedence over derivation."""
        conv_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(
            agent_session_id="explicit-session",
            conversation={"id": conv_id},
        )
        ref = {"name": "agent", "version": "1"}

        result = _resolve_session_id(parsed, {}, agent_reference=ref)
        assert result == "explicit-session"

    def test_resolve_session_id_env_beats_derivation(self):
        """Platform env session ID takes precedence over derivation."""
        conv_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(conversation={"id": conv_id})
        ref = {"name": "agent", "version": "1"}

        result = _resolve_session_id(parsed, {}, env_session_id="env-session", agent_reference=ref)
        assert result == "env-session"

    def test_string_conversation_id_also_derives(self):
        """String-typed conversation in parsed request is used for derivation."""
        conv_id = IdGenerator.new_response_id()
        parsed = _FakeParsed(conversation=conv_id)
        ref = {"name": "agent", "version": "1"}

        result = _resolve_session_id(parsed, {}, agent_reference=ref)
        assert len(result) == 63
        assert re.fullmatch(r"[0-9a-f]+", result)

    def test_non_id_format_conversation_id_still_derives(self):
        """Conversation ID that isn't a valid IdGenerator format still produces deterministic hash."""
        parsed = _FakeParsed(conversation="plain-conversation-id")
        ref = {"name": "agent", "version": "1"}

        result1 = _resolve_session_id(parsed, {}, agent_reference=ref)
        result2 = _resolve_session_id(parsed, {}, agent_reference=ref)

        assert result1 == result2
        assert len(result1) == 63
