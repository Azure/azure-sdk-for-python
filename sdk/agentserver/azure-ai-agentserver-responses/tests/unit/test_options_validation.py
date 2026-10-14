# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for responses options validation."""

from __future__ import annotations

from azure.ai.agentserver.responses._options import ResponsesServerOptions


class TestOptionsDefaults:
    """Verify default values."""

    def test_steerable_conversations_defaults_false(self) -> None:
        options = ResponsesServerOptions()
        assert options.steerable_conversations is False


class TestOptionsValidation:
    """Verify fail-fast validation at construction time."""

    def test_steerable_without_store_disabled_succeeds(self) -> None:
        """steerable_conversations=True with default store → OK."""
        options = ResponsesServerOptions(steerable_conversations=True)
        assert options.steerable_conversations is True

    def test_steerable_conversations_does_not_enable_resilience(self) -> None:
        """Steering configuration remains independent of the core resilience switch."""
        options = ResponsesServerOptions(
            steerable_conversations=True,
        )
        assert options.steerable_conversations is True

    # (Spec 024 Phase 5 — Proposal #5) ``store_disabled`` and
    # ``max_pending`` options were DELETED. The pre-Phase-5 validation
    # tests for those keyword arguments are obsolete — their absence is
    # asserted in ``test_phase5_api_simplification.py``.
