# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for durability/steering options validation."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._options import ResponsesServerOptions


class TestDurabilityOptionsDefaults:
    """Verify default values for durability options."""

    def test_durable_background_defaults_false(self) -> None:
        """(Spec 024 Phase 4 — work item #3) Default flips to False.

        Pre-Phase-4: defaulted to True (durability assumed-on).
        Post-Phase-4: defaults to False — handler authors must explicitly
        opt into crash recovery via `durable_background=True`. Documented
        breaking change; CHANGELOG entry required.
        """
        options = ResponsesServerOptions()
        assert options.durable_background is False

    def test_steerable_conversations_defaults_false(self) -> None:
        options = ResponsesServerOptions()
        assert options.steerable_conversations is False


class TestDurabilityOptionsValidation:
    """Verify fail-fast validation at construction time."""

    def test_steerable_requires_store_not_disabled(self) -> None:
        """steerable_conversations=True with store explicitly disabled → error."""
        with pytest.raises(ValueError, match="steerable_conversations"):
            ResponsesServerOptions(
                steerable_conversations=True,
                store_disabled=True,
            )

    def test_steerable_without_store_disabled_succeeds(self) -> None:
        """steerable_conversations=True with default store → OK."""
        options = ResponsesServerOptions(steerable_conversations=True)
        assert options.steerable_conversations is True

    def test_durable_background_false_disables_durability(self) -> None:
        """durable_background=False is a valid opt-out."""
        options = ResponsesServerOptions(durable_background=False)
        assert options.durable_background is False

    def test_steerable_with_durable_background_off_does_not_raise(self) -> None:
        """(Spec 024 Phase 4 — Proposal #9 relaxed composition)

        steerable_conversations=True + durable_background=False is now
        a VALID combination. Pre-Phase-4 this raised ValueError because
        the framework assumed steering required durable recovery; per
        spec 024 §A Proposal #9 the two options are independent.
        """
        options = ResponsesServerOptions(
            steerable_conversations=True,
            durable_background=False,
        )
        assert options.steerable_conversations is True
        assert options.durable_background is False

    def test_max_pending_default(self) -> None:
        """max_pending defaults to 10 (matching task primitive)."""
        options = ResponsesServerOptions(steerable_conversations=True)
        assert options.max_pending == 10

    def test_max_pending_custom(self) -> None:
        """max_pending can be set by developer."""
        options = ResponsesServerOptions(
            steerable_conversations=True,
            max_pending=5,
        )
        assert options.max_pending == 5

    def test_max_pending_must_be_positive(self) -> None:
        """max_pending must be > 0."""
        with pytest.raises(ValueError):
            ResponsesServerOptions(
                steerable_conversations=True,
                max_pending=0,
            )
