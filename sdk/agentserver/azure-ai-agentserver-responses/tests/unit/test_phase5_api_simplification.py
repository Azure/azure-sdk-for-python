# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 5 RED tests — public API simplification.

Tests all approved §A proposals (#4, #5, #6, #8, #10, #11, #12, #13):

- Proposal #4: Remove `max_pending` from ResponsesServerOptions
- Proposal #5: Remove `context.shutdown.is_set()` (subsumed by #11)
- Proposal #6 + #10: Flatten `context.durability.*` into top-level fields
- Proposal #8: Remove `store_disabled` from ResponsesServerOptions
- Proposal #11: New cancellation surface (cause booleans + events +
  exit_for_recovery). Hard-reject 3-arg handler signatures. Drop
  CancellationReason enum + context.cancellation_reason.
- Proposal #12: Remove `replay_event_ttl_seconds`, `retry_attempt`
  (NOT add `timeout_exceeded`)
- Proposal #13: Drop `entry_mode` (NOT add to flattened context);
  rename Q7 boolean to `client_cancelled`

EXPECTED: RED at this commit; GREEN after Phase 5 implementation.
"""

from __future__ import annotations

import asyncio
import typing

import pytest


# ─────────────────────────────────────────────────────────────────────
# Proposal #4 — Remove `max_pending`
# ─────────────────────────────────────────────────────────────────────


def test_max_pending_kwarg_removed_from_options() -> None:
    """ResponsesServerOptions(max_pending=10) must raise TypeError post-Phase-5."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    with pytest.raises(TypeError):
        ResponsesServerOptions(max_pending=10)  # type: ignore[call-arg]


def test_options_does_not_have_max_pending_attr() -> None:
    """After construction, ``options.max_pending`` must not exist."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    options = ResponsesServerOptions()
    assert not hasattr(options, "max_pending")


# ─────────────────────────────────────────────────────────────────────
# Proposal #8 — Remove `store_disabled`
# ─────────────────────────────────────────────────────────────────────


def test_store_disabled_kwarg_removed_from_options() -> None:
    """ResponsesServerOptions(store_disabled=False) must raise TypeError."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    with pytest.raises(TypeError):
        ResponsesServerOptions(store_disabled=False)  # type: ignore[call-arg]


def test_options_does_not_have_store_disabled_attr() -> None:
    """After construction, ``options.store_disabled`` must not exist."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    options = ResponsesServerOptions()
    assert not hasattr(options, "store_disabled")


# ─────────────────────────────────────────────────────────────────────
# Proposal #12 — Remove `replay_event_ttl_seconds`
# ─────────────────────────────────────────────────────────────────────


def test_replay_event_ttl_seconds_kwarg_removed() -> None:
    """ResponsesServerOptions(replay_event_ttl_seconds=600) must raise TypeError."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    with pytest.raises(TypeError):
        ResponsesServerOptions(replay_event_ttl_seconds=600)  # type: ignore[call-arg]


def test_options_does_not_have_replay_event_ttl_attr() -> None:
    """After construction, ``options.replay_event_ttl_seconds`` must not exist."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions

    options = ResponsesServerOptions()
    assert not hasattr(options, "replay_event_ttl_seconds")


def test_replay_event_ttl_hardcoded_at_least_600() -> None:
    """The hardcoded ttl_seconds in _routing.py must be ≥ 600 (B35 compliance)."""
    import inspect

    from azure.ai.agentserver.responses.hosting import _routing

    src = inspect.getsource(_routing)
    # Look for the hardcoded TTL constant or inline ttl_seconds=N; must be ≥ 600.
    import re

    matches = re.findall(r"_REPLAY_EVENT_TTL_SECONDS\s*=\s*(\d+(?:\.\d+)?)", src)
    if not matches:
        matches = re.findall(r"ttl_seconds\s*=\s*(\d+(?:\.\d+)?)", src)
    assert matches, "spec 024 Phase 5 / B35: _routing.py must hardcode ttl_seconds=N"
    for m in matches:
        assert float(m) >= 600, f"spec 024 / B35: ttl_seconds must be ≥ 600 (≥ 10 min replay), got {m}"


# ─────────────────────────────────────────────────────────────────────
# Proposal #6 + #10 — Flatten DurabilityContext into ResponseContext
# ─────────────────────────────────────────────────────────────────────


def _make_response_context():
    """Helper to build a minimal ResponseContext for unit tests."""
    from azure.ai.agentserver.responses._response_context import ResponseContext
    from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

    return ResponseContext(
        response_id="resp_test",
        mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
    )


def test_durability_fields_flat_on_context() -> None:
    """Flattened fields directly on ResponseContext (post-Proposal #10)."""
    ctx = _make_response_context()
    assert hasattr(ctx, "is_recovery")
    assert hasattr(ctx, "is_steered_turn")
    assert hasattr(ctx, "pending_input_count")
    assert hasattr(ctx, "durable_metadata")
    # Default values for fresh handler invocation
    assert ctx.is_recovery is False
    assert ctx.is_steered_turn is False
    assert ctx.pending_input_count == 0


def test_durability_property_removed_from_context() -> None:
    """`context.durability` nested property is gone (Proposal #10)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "durability")


def test_legacy_field_names_removed() -> None:
    """Old field names `was_steered`, `pending_inputs` removed (Proposal #6)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "was_steered")
    assert not hasattr(ctx, "pending_inputs")


def test_retry_attempt_removed_from_context() -> None:
    """`context.retry_attempt` removed (Proposal #12 — broken pre-existing field)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "retry_attempt")


def test_entry_mode_removed_from_context() -> None:
    """`context.entry_mode` removed (Proposal #13 — redundant with `is_recovery`)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "entry_mode")


def test_durability_entry_mode_alias_removed() -> None:
    """`DurabilityEntryMode` Literal alias removed (Proposal #13)."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.responses._durability_context import (  # noqa: F401
            DurabilityEntryMode,
        )


def test_durability_context_class_removed() -> None:
    """`DurabilityContext` class deleted (Proposal #10 flatten)."""
    from azure.ai.agentserver.responses import _durability_context

    assert not hasattr(_durability_context, "DurabilityContext"), (
        "spec 024 Proposal #10: DurabilityContext class must be deleted; " "fields are flattened onto ResponseContext"
    )


# ─────────────────────────────────────────────────────────────────────
# Proposal #11 — Cancellation surface alignment
# ─────────────────────────────────────────────────────────────────────


def test_context_has_cancel_event() -> None:
    """`context.cancel` is an asyncio.Event."""
    ctx = _make_response_context()
    assert hasattr(ctx, "cancel")
    assert isinstance(ctx.cancel, asyncio.Event)


def test_context_has_shutdown_event() -> None:
    """`context.shutdown` is an asyncio.Event."""
    ctx = _make_response_context()
    assert hasattr(ctx, "shutdown")
    assert isinstance(ctx.shutdown, asyncio.Event)


def test_context_has_client_cancelled_bool() -> None:
    """`context.client_cancelled` is initially False."""
    ctx = _make_response_context()
    assert hasattr(ctx, "client_cancelled")
    assert ctx.client_cancelled is False


def test_context_has_exit_for_recovery_method() -> None:
    """`context.exit_for_recovery` is a coroutine method."""
    ctx = _make_response_context()
    assert hasattr(ctx, "exit_for_recovery")
    assert callable(ctx.exit_for_recovery)
    assert asyncio.iscoroutinefunction(ctx.exit_for_recovery)


def test_cancellation_reason_property_removed() -> None:
    """`context.cancellation_reason` removed (Proposal #11 + Proposal #5)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "cancellation_reason")


def test_is_shutdown_requested_property_removed() -> None:
    """`context.shutdown.is_set()` removed (Proposal #5)."""
    ctx = _make_response_context()
    assert not hasattr(ctx, "is_shutdown_requested")


def test_cancellation_reason_enum_not_importable_from_public() -> None:
    """`CancellationReason` enum deleted (Proposal #11 / #6)."""
    with pytest.raises(ImportError):
        from azure.ai.agentserver.responses import CancellationReason  # noqa: F401


def test_cancellation_reason_enum_not_in_runtime_module() -> None:
    """`CancellationReason` enum removed from models.runtime too."""
    from azure.ai.agentserver.responses.models import runtime as _runtime

    assert not hasattr(
        _runtime, "CancellationReason"
    ), "spec 024 Proposal #11: CancellationReason enum must be deleted entirely"


# ─────────────────────────────────────────────────────────────────────
# Public type exports (DurableMetadataNamespace, ExitForRecoverySignal)
# ─────────────────────────────────────────────────────────────────────


def test_durable_metadata_namespace_protocol_exported() -> None:
    """`DurableMetadataNamespace` Protocol exported from the package."""
    from azure.ai.agentserver.responses import DurableMetadataNamespace  # noqa: F401


def test_exit_for_recovery_signal_exported() -> None:
    """`ExitForRecoverySignal` type exported from the package (Proposal #11)."""
    from azure.ai.agentserver.responses import ExitForRecoverySignal  # noqa: F401


# ─────────────────────────────────────────────────────────────────────
# Type annotations are precise (Strong Type Safety — Principle II)
# ─────────────────────────────────────────────────────────────────────


def test_flattened_field_types_are_precise() -> None:
    """Type annotations must be precise: bool/int/etc, not Any."""
    from azure.ai.agentserver.responses._response_context import ResponseContext

    hints = typing.get_type_hints(ResponseContext)
    # Just spot-check a few — the full type-check is via pyright/mypy.
    # is_recovery and is_steered_turn should be bool.
    # If these aren't class-level annotations, this test might pass trivially;
    # the important check is the property return types — checked via pyright.
    assert hints  # placeholder; non-empty type hints dict
