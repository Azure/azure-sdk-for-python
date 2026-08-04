# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-lifetime content markers for the conformance test handler.

This module is imported by both ``_test_handler.py`` (which builds the
strings to emit) and by individual conformance tests (which build the
strings to assert on). Keeping it side-effect-free — no
``ResponsesAgentServerHost`` construction, no env-var reads — means
tests can import from it without pulling in the full subprocess
handler module.

The markers are designed so a test can identify which lifetime emitted
which event by inspecting the event content alone. This is what makes
cross-attempt assertions sensitive: if the framework loses lifetime 0's
events or overwrites them with lifetime 1's, a content-aware test
fails. A test that only checks ``status == "completed"`` cannot tell.
"""

from __future__ import annotations

# Phases of the handler's emission cycle. ``pre`` is before the
# interruptible sleep (so events can land on the wire before a Path B
# or Path C SIGKILL); ``post`` is after the sleep (the natural-
# completion content).
PHASE_PRE = "pre"
PHASE_POST = "post"


def delta_content(lifetime: int, phase: str, index: int) -> str:
    """Build the SSE ``output_text.delta`` payload for one event.

    Format: ``L{lifetime}_{phase}_d{index}``.

    Examples: ``L0_pre_d0``, ``L0_pre_d2``, ``L1_post_d0``.

    :param lifetime: ``0`` for fresh entry, ``1`` for any recovered /
        resumed entry. Note this is NOT ``0`` —
        that counter is per-process and resets on restart, so it
        doesn't distinguish lifetimes across crash + recovery. The
        conformance handler derives ``lifetime`` from
        ``("recovered" if context.is_recovery else "fresh")`` instead.
    :param phase: ``PHASE_PRE`` or ``PHASE_POST``.
    :param index: Zero-based index within the phase.
    :returns: The tagged content string.
    """
    return f"L{lifetime}_{phase}_d{index}"


def final_text(
    *,
    lifetime: int,
    pre_count: int,
    post_count: int,
    chain_id: str,
    visited: list[int] | None = None,
) -> str:
    """Build the SSE ``output_text.done`` final text payload.

    Format:
    ``L{lifetime}_done|pre={N}|post={M}|chain={chain_id}`` plus an
    optional ``|visited=[0, 1, ...]`` segment listing the lifetimes
    that wrote the metadata watermark.

    Tests can parse this back to verify:

    - Which lifetime produced the terminal (``L{lifetime}``).
    - That the delta counts match what the handler was configured to emit.
    - That ``context.conversation_chain_id`` is stable across attempts
      (assert the ``chain=…`` segment is identical pre- and post-recovery).
    - That metadata writes from prior lifetimes are visible to the
      recovered handler (``visited=[0, 1]`` means lifetime 1 saw
      lifetime 0's marker survive the crash).

    :param lifetime: ``context.0`` for the emitting handler.
    :param pre_count: Number of pre-sleep deltas the handler emitted.
    :param post_count: Number of post-sleep deltas the handler emitted.
    :param chain_id: ``context.conversation_chain_id``.
    :param visited: Optional list of lifetimes that wrote the metadata watermark.
    :returns: The composite final-text string.
    """
    parts = [
        f"L{lifetime}_done",
        f"pre={pre_count}",
        f"post={post_count}",
        f"chain={chain_id}",
    ]
    if visited is not None:
        parts.append(f"visited={visited}")
    return "|".join(parts)


# Metadata key used by the optional watermark — single source of truth
# so handler and tests don't drift on the spelling.
WATERMARK_METADATA_KEY = "conformance_lifetimes_visited"
