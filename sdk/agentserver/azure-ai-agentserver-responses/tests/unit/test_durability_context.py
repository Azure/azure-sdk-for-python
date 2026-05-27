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
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert ctx.entry_mode == "fresh"

    def test_entry_mode_recovered(self) -> None:
        ctx = DurabilityContext(
            entry_mode="recovered",
            run_attempt=1,
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
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        # Verify the type annotation (can't assign "resumed")
        valid_modes: set[Literal["fresh", "recovered"]] = {"fresh", "recovered"}
        assert ctx.entry_mode in valid_modes

    def test_run_attempt_property(self) -> None:
        ctx = DurabilityContext(
            entry_mode="recovered",
            run_attempt=3,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert ctx.run_attempt == 3

    def test_was_steered_property(self) -> None:
        ctx = DurabilityContext(
            entry_mode="fresh",
            run_attempt=0,
            was_steered=True,
            pending_inputs=2,
            metadata={},
        )
        assert ctx.was_steered is True

    def test_pending_inputs_is_int(self) -> None:
        ctx = DurabilityContext(
            entry_mode="fresh",
            run_attempt=0,
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
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata=metadata,
        )
        # Can read
        assert ctx.metadata["step"] == 3
        # Can write
        ctx.metadata["new_key"] = "value"
        assert ctx.metadata["new_key"] == "value"

    def test_metadata_hides_framework_keys(self) -> None:
        """Developer-facing metadata must NOT expose _framework.* keys."""
        raw_metadata = {
            "user_key": "visible",
            "_framework.last_sequence_number": 42,
            "_framework.background": True,
        }
        ctx = DurabilityContext(
            entry_mode="fresh",
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata=raw_metadata,
        )
        # User keys visible
        assert "user_key" in ctx.metadata
        assert ctx.metadata["user_key"] == "visible"
        # Framework keys hidden
        assert "_framework.last_sequence_number" not in ctx.metadata
        assert "_framework.background" not in ctx.metadata
        # Iteration excludes framework keys
        keys = list(ctx.metadata.keys())
        assert all(not k.startswith("_framework.") for k in keys)

    def test_metadata_write_does_not_pollute_framework_namespace(self) -> None:
        """Writing _framework.* keys via metadata should be blocked or ignored."""
        ctx = DurabilityContext(
            entry_mode="fresh",
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        with pytest.raises((KeyError, ValueError)):
            ctx.metadata["_framework.hack"] = "bad"

    def test_last_snapshot_property_was_removed_per_spec_012(self) -> None:
        """Spec 012: `last_snapshot` is removed. Property should not exist.

        The library only persists the response object at `response.created`
        and at terminal events; a between-states snapshot would never carry
        useful in-flight state. Handlers build resumption responses from
        upstream framework state instead.
        """
        ctx = DurabilityContext(
            entry_mode="recovered",
            run_attempt=1,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        assert not hasattr(ctx, "last_snapshot")

    def test_properties_are_read_only(self) -> None:
        """All properties except metadata should be read-only."""
        ctx = DurabilityContext(
            entry_mode="fresh",
            run_attempt=0,
            was_steered=False,
            pending_inputs=0,
            metadata={},
        )
        with pytest.raises(AttributeError):
            ctx.entry_mode = "recovered"  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.run_attempt = 5  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.was_steered = True  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.pending_inputs = 10  # type: ignore[misc]
