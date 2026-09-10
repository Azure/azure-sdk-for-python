# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------
"""Spec 033 §3.6 / F6 verification: the streaming wire's ``sequence_number`` is
single-authority (the orchestrator's cursor-seeded ``state.next_seq``).

F6 was originally framed as "three redundant seq sources that must agree." Tracing
the two paths shows they back *different* consumers:

* **Streaming wire** (cursor-replayed, client-visible) — every event flows through
  ``_apply_stream_event_defaults(sequence_number=state.next_seq)``, which
  **overwrites** any builder/SSE seq. So the resilient stream + SSE wire derive seq
  *solely* from the cursor. This is the only surface where a "must-agree"
  divergence could ever reach a client, and it is already single-authority.
* **Non-stream background** path has no cursor and is not cursor-replayed (the
  snapshot is built ``remove_sequence_number=True``); it uses the builder counter
  by design (``sequence_number=None`` leaves the builder value unchanged).

These tests pin the structural mechanism (a fast guard); the strict
monotonic-across-recovery guarantee is additionally proven end-to-end by
``tests/e2e/resilience_contract/test_streaming_recovery_continuity.py``.
"""
from __future__ import annotations

from typing import cast

from azure.ai.agentserver.responses.models import _generated as generated_models
from azure.ai.agentserver.responses.streaming._helpers import _apply_stream_event_defaults


def _delta_event(builder_seq: int) -> generated_models.ResponseStreamEvent:
    return cast(
        generated_models.ResponseStreamEvent,
        {
            "type": "response.output_text.delta",
            "delta": "hi",
            # A deliberately-wrong builder-stamped seq the streaming path must overwrite.
            "sequence_number": builder_seq,
        },
    )


def test_streaming_path_overwrites_builder_seq_with_cursor() -> None:
    """The streaming append (``sequence_number=state.next_seq``) is authoritative:
    it overwrites the builder's per-stream counter value."""
    event = _delta_event(builder_seq=999)
    out = _apply_stream_event_defaults(
        event,
        response_id="caresp_x",
        agent_reference={},
        model="m",
        sequence_number=5,  # the orchestrator's cursor-seeded state.next_seq
    )
    assert out["sequence_number"] == 5, "cursor seq must win over the builder seq"


def test_non_stream_path_keeps_builder_seq() -> None:
    """The non-stream path passes ``sequence_number=None`` (no cursor), so the
    builder's seq is kept as-is — a separate authority for a non-replayed surface."""
    event = _delta_event(builder_seq=7)
    out = _apply_stream_event_defaults(
        event,
        response_id="caresp_x",
        agent_reference={},
        model="m",
        sequence_number=None,
    )
    assert out["sequence_number"] == 7, "non-stream path must keep the builder seq"
