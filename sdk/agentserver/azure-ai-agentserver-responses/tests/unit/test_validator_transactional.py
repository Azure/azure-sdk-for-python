# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""``EventStreamValidator.validate_next`` must be transactional.

A rejected event must not advance any validator state, otherwise the
``_make_failed_event`` fallback (which re-enters the validator with a
``response.failed`` terminal) trips "multiple terminal lifecycle events" and the
intended failure event can never be emitted.
"""
import pytest

from azure.ai.agentserver.responses.streaming._state_machine import EventStreamValidator

# Tests intentionally assert on the validator's internal counters.
# pylint: disable=protected-access


def _created():
    return {"type": "response.created", "response": {"status": "in_progress"}}


def test_rejected_terminal_does_not_poison_validator_and_failed_fallback_succeeds():
    validator = EventStreamValidator()
    validator.validate_next(_created())

    # A terminal whose status contradicts its type is rejected...
    bad_terminal = {"type": "response.completed", "response": {"status": "failed"}}
    with pytest.raises(ValueError):
        validator.validate_next(bad_terminal)

    # ...and leaves NO terminal recorded, so the response.failed fallback is accepted.
    assert validator._terminal_count == 0
    assert validator._terminal_seen is False
    validator.validate_next({"type": "response.failed", "response": {"status": "failed"}})


def test_rejected_event_restores_all_counters():
    validator = EventStreamValidator()
    validator.validate_next(_created())
    before = (
        validator._last_stage,
        validator._terminal_count,
        validator._terminal_seen,
        validator._event_count,
        set(validator._added_indexes),
        set(validator._done_indexes),
    )

    # Out-of-order output-item done (no preceding added) is rejected.
    with pytest.raises(ValueError):
        validator.validate_next({"type": "response.output_item.done", "output_index": 3})

    after = (
        validator._last_stage,
        validator._terminal_count,
        validator._terminal_seen,
        validator._event_count,
        set(validator._added_indexes),
        set(validator._done_indexes),
    )
    assert before == after


def test_success_path_still_advances_state():
    validator = EventStreamValidator()
    validator.validate_next(_created())
    validator.validate_next({"type": "response.output_item.added", "output_index": 0})
    validator.validate_next({"type": "response.output_item.done", "output_index": 0})
    validator.validate_next({"type": "response.completed", "response": {"status": "completed"}})
    assert validator._terminal_seen is True
    assert validator._terminal_count == 1
