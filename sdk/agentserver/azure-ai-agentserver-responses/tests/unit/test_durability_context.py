# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for the DurabilityContext shape."""

from __future__ import annotations

from typing import Literal

import pytest

from azure.ai.agentserver.responses._durability_context import DurabilityContext


class TestDurabilityContextShape:
    """Verify the public contract of DurabilityContext."""

    def test_entry_mode_fresh(self) -> None:
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert ctx.entry_mode == "fresh"

    def test_entry_mode_recovered(self) -> None:
        ctx = DurabilityContext(
            entry_mode="recovered",
            retry_attempt=1,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert ctx.entry_mode == "recovered"

    def test_entry_mode_only_two_values(self) -> None:
        """entry_mode only allows 'fresh' and 'recovered' — not 'resumed'."""
        # This is a type-level constraint; at runtime we verify via construction
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        # Verify the type annotation (can't assign "resumed")
        valid_modes: set[Literal["fresh", "recovered"]] = {"fresh", "recovered"}
        assert ctx.entry_mode in valid_modes

    def test_retry_attempt_property(self) -> None:
        ctx = DurabilityContext(
            entry_mode="recovered",
            retry_attempt=3,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert ctx.retry_attempt == 3

    def test_was_steered_property(self) -> None:
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=True,
            pending_inputs=2,
            metadata={},
        )
        assert ctx.was_steered is True

    def test_pending_inputs_is_int(self) -> None:
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=True,
            pending_inputs=5,
            metadata={},
        )
        assert ctx.pending_inputs == 5
        assert isinstance(ctx.pending_inputs, int)

    def test_metadata_is_mutable_mapping(self) -> None:
        metadata = {"step": 3, "cached": True}
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata=metadata,
        )
        # Can read
        assert ctx.metadata["step"] == 3
        # Can write
        ctx.metadata["new_key"] = "value"
        assert ctx.metadata["new_key"] == "value"

    def test_metadata_rejects_underscore_prefixed_keys(self) -> None:
        """Per spec 015 FR-005: handler-facing metadata MUST reject any key
        starting with ``_``. This protects developers from accidentally
        colliding with framework-reserved namespaces (e.g. ``_responses``)
        stored alongside their own data.
        """
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        with pytest.raises(ValueError):
            ctx.metadata["_anything"] = "bad"
        with pytest.raises(ValueError):
            ctx.metadata["_responses"] = "still bad"

    def test_metadata_is_callable_for_named_namespace(self) -> None:
        """Per spec 015 FR-003: ``ctx.metadata(name)`` returns a sibling
        namespace facade with isolated storage."""
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        scoped = ctx.metadata("user_workflow")
        scoped["step"] = 1
        # Isolated from default namespace
        assert "step" not in ctx.metadata
        # And readable back from the same name
        assert ctx.metadata("user_workflow")["step"] == 1

    def test_named_namespace_also_rejects_underscore_prefix(self) -> None:
        """Handler-facing wrapper enforces the convention symmetrically:
        ``ctx.metadata("_responses")`` must raise — handlers cannot reach
        into framework-reserved namespaces via the wrapper. Framework
        layers reach those namespaces via the underlying ``TaskContext``
        directly (asymmetric enforcement)."""
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        with pytest.raises(ValueError):
            ctx.metadata("_responses")
        with pytest.raises(ValueError):
            ctx.metadata("_anything")

    def test_last_snapshot_property_was_removed_per_spec_012(self) -> None:
        """Spec 012: `last_snapshot` is removed. Property should not exist.

        The library only persists the response object at `response.created`
        and at terminal events; a between-states snapshot would never carry
        useful in-flight state. Handlers build resumption responses from
        upstream framework state instead.
        """
        ctx = DurabilityContext(
            entry_mode="recovered",
            retry_attempt=1,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert not hasattr(ctx, "last_snapshot")

    def test_properties_are_read_only(self) -> None:
        """All properties except metadata should be read-only."""
        ctx = DurabilityContext(
            entry_mode="fresh",
            retry_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        with pytest.raises(AttributeError):
            ctx.entry_mode = "recovered"  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.retry_attempt = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.was_steered = True  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.pending_inputs = 10  # type: ignore[misc]
