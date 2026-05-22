# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for lifecycle event state machine normalization."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.streaming._state_machine import (
    _normalize_lifecycle_events,
)


def test_lifecycle_state_machine__requires_response_created_as_first_event() -> None:
    with pytest.raises(ValueError):
        _normalize_lifecycle_events(
            response_id="resp_123",
            events=[
                {
                    "type": "response.in_progress",
                    "response": {"status": "in_progress"},
                }
            ],
        )


def test_lifecycle_state_machine__rejects_multiple_terminal_events() -> None:
    with pytest.raises(ValueError):
        _normalize_lifecycle_events(
            response_id="resp_123",
            events=[
                {"type": "response.created", "response": {"status": "queued"}},
                {"type": "response.completed", "response": {"status": "completed"}},
                {"type": "response.failed", "response": {"status": "failed"}},
            ],
        )


def test_lifecycle_state_machine__auto_appends_failed_when_terminal_missing() -> None:
    normalized = _normalize_lifecycle_events(
        response_id="resp_123",
        events=[
            {"type": "response.created", "response": {"status": "queued"}},
            {"type": "response.in_progress", "response": {"status": "in_progress"}},
        ],
    )

    assert normalized[-1]["type"] == "response.failed"
    assert normalized[-1]["response"]["status"] == "failed"


def test_lifecycle_state_machine__rejects_out_of_order_transitions() -> None:
    with pytest.raises(ValueError):
        _normalize_lifecycle_events(
            response_id="resp_123",
            events=[
                {"type": "response.created", "response": {"status": "queued"}},
                {"type": "response.completed", "response": {"status": "completed"}},
                {"type": "response.in_progress", "response": {"status": "in_progress"}},
            ],
        )


def test_lifecycle_state_machine__returns_deep_copied_response_snapshots() -> None:
    original_events = [
        {
            "type": "response.created",
            "response": {
                "status": "queued",
                "metadata": {"nested": "before"},
            },
        },
        {
            "type": "response.completed",
            "response": {
                "status": "completed",
                "metadata": {"nested": "before"},
            },
        },
    ]

    normalized = _normalize_lifecycle_events(response_id="resp_123", events=original_events)

    original_events[0]["response"]["metadata"]["nested"] = "after"
    assert normalized[0]["response"]["metadata"]["nested"] == "before"
