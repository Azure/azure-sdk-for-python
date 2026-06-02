# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for CancellationReason enum and context integration."""

from __future__ import annotations

import asyncio

import pytest

from azure.ai.agentserver.responses import CancellationReason, ResponseContext
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags


def _make_context(**kwargs) -> ResponseContext:
    """Create a minimal ResponseContext for testing."""
    flags = ResponseModeFlags(stream=True, store=True, background=True)
    return ResponseContext(response_id="test-id", mode_flags=flags, request=None, **kwargs)


class TestCancellationReasonEnum:
    """Tests for the CancellationReason enum itself."""

    def test_enum_values(self):
        assert CancellationReason.STEERED == "steered"
        assert CancellationReason.CLIENT_CANCELLED == "cancelled"
        assert CancellationReason.SHUTTING_DOWN == "shutting_down"

    def test_enum_is_str(self):
        """CancellationReason is str subclass for JSON serialization."""
        assert isinstance(CancellationReason.STEERED, str)

    def test_enum_members_are_mutually_exclusive(self):
        members = list(CancellationReason)
        assert len(members) == 3
        values = [m.value for m in members]
        assert len(set(values)) == 3


class TestCancellationReasonOnContext:
    """Tests for cancellation_reason on ResponseContext."""

    def test_reason_is_none_before_signal(self):
        ctx = _make_context()
        assert ctx.cancellation_reason is None

    def test_reason_set_to_steered(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.STEERED
        assert ctx.cancellation_reason == CancellationReason.STEERED

    def test_reason_set_to_client_cancelled(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
        assert ctx.cancellation_reason == CancellationReason.CLIENT_CANCELLED

    def test_reason_set_to_shutting_down(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
        assert ctx.cancellation_reason == CancellationReason.SHUTTING_DOWN


class TestBackwardCompatIsShutdownRequested:
    """Tests for is_shutdown_requested backward-compat property."""

    def test_is_shutdown_false_when_no_reason(self):
        ctx = _make_context()
        assert ctx.is_shutdown_requested is False

    def test_is_shutdown_true_when_shutting_down(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
        assert ctx.is_shutdown_requested is True

    def test_is_shutdown_false_when_steered(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.STEERED
        assert ctx.is_shutdown_requested is False

    def test_is_shutdown_false_when_client_cancelled(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
        assert ctx.is_shutdown_requested is False

    def test_setter_true_sets_shutting_down(self):
        ctx = _make_context()
        ctx.is_shutdown_requested = True
        assert ctx.cancellation_reason == CancellationReason.SHUTTING_DOWN

    def test_setter_false_clears_shutting_down(self):
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
        ctx.is_shutdown_requested = False
        assert ctx.cancellation_reason is None

    def test_setter_true_does_not_overwrite_existing_reason(self):
        """First-write-wins: if already STEERED, setter True is a no-op."""
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.STEERED
        ctx.is_shutdown_requested = True
        # STEERED was set first — should not be overwritten
        assert ctx.cancellation_reason == CancellationReason.STEERED


class TestFirstWriteWins:
    """Tests for first-write-wins semantics on cancellation_reason."""

    def test_direct_overwrite_is_allowed(self):
        """Direct attribute assignment can overwrite — first-write-wins
        is enforced at the trigger point (endpoint/orchestrator), not
        on the property itself."""
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.STEERED
        ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
        assert ctx.cancellation_reason == CancellationReason.SHUTTING_DOWN

    def test_setter_respects_first_write(self):
        """The backward-compat setter respects first-write-wins."""
        ctx = _make_context()
        ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
        ctx.is_shutdown_requested = True
        # CLIENT_CANCELLED was already set — setter should not overwrite
        assert ctx.cancellation_reason == CancellationReason.CLIENT_CANCELLED
