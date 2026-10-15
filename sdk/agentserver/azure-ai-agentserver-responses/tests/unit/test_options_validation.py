# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for resilience/steering options validation."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._options import ResponsesServerOptions


class TestResilienceOptionsDefaults:
    """Verify default values for resilience options."""

    def test_resilient_background_defaults_false(self) -> None:
        """(Spec 024 Phase 4 — work item #3) Default flips to False.

        Pre-Phase-4: defaulted to True (resilience assumed-on).
        Post-Phase-4: defaults to False — handler authors must explicitly
        opt into crash recovery via `resilient_background=True`. Documented
        breaking change; CHANGELOG entry required.
        """
        options = ResponsesServerOptions()
        assert options.resilient_background is False

    def test_steerable_conversations_defaults_false(self) -> None:
        options = ResponsesServerOptions()
        assert options.steerable_conversations is False


class TestResilienceOptionsValidation:
    """Verify fail-fast validation at construction time."""

    def test_steerable_without_store_disabled_succeeds(self) -> None:
        """steerable_conversations=True with default store → OK."""
        options = ResponsesServerOptions(steerable_conversations=True)
        assert options.steerable_conversations is True

    def test_resilient_background_false_disables_resilience(self) -> None:
        """resilient_background=False is a valid opt-out."""
        options = ResponsesServerOptions(resilient_background=False)
        assert options.resilient_background is False

    def test_steerable_with_resilient_background_off_does_not_raise(self) -> None:
        """(Spec 024 Phase 4 — Proposal #9 relaxed composition)

        steerable_conversations=True + resilient_background=False is now
        a VALID combination. Pre-Phase-4 this raised ValueError because
        the framework assumed steering required resilient recovery; per
        spec 024 §A Proposal #9 the two options are independent.
        """
        options = ResponsesServerOptions(
            steerable_conversations=True,
            resilient_background=False,
        )
        assert options.steerable_conversations is True
        assert options.resilient_background is False

    # (Spec 024 Phase 5 — Proposal #5) ``store_disabled`` and
    # ``max_pending`` options were DELETED. The pre-Phase-5 validation
    # tests for those keyword arguments are obsolete — their absence is
    # asserted in ``test_phase5_api_simplification.py``.
