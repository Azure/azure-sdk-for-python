# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Stream recovery logic for the durable orchestrator.

Provides:
- check_stream_consistency: validates last known sequence matches persisted state
- hydrate_subject: loads persisted events into a fresh _ResponseEventSubject
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._event_subject import _ResponseEventSubject

if TYPE_CHECKING:
    from .._response_context import IsolationContext
    from ..store._base import DurableStreamProviderProtocol


async def check_stream_consistency(
    stream_provider: DurableStreamProviderProtocol,
    response_id: str,
    last_sequence_number: int,
    *,
    isolation: IsolationContext | None = None,
) -> bool:
    """Check if persisted stream is consistent with the last known sequence.

    Returns True if the provider has events up to (and including) the given
    sequence number. Returns False if the stream is missing, empty, or the
    highest persisted sequence is below expected.

    :param stream_provider: The durable stream provider to check against.
    :param response_id: Response whose stream to validate.
    :param last_sequence_number: The last sequence number the framework knew about.
    :param isolation: Multi-tenant isolation context.
    :returns: True if stream data is consistent and can be resumed.
    """
    events = await stream_provider.get_stream_events(response_id, isolation=isolation)
    if events is None or len(events) == 0:
        return False

    # Find highest persisted sequence number
    max_seq = max(
        (
            e.get("sequence_number", -1)
            if isinstance(e, dict)
            else getattr(e, "sequence_number", -1)
        )
        for e in events
    )
    return max_seq >= last_sequence_number


async def hydrate_subject(
    stream_provider: DurableStreamProviderProtocol,
    response_id: str,
    *,
    isolation: IsolationContext | None = None,
    starting_after: int | None = None,
) -> _ResponseEventSubject | None:
    """Load persisted events into a fresh _ResponseEventSubject for replay.

    Returns None if no events are available from the provider. If events
    exist, publishes them into the subject's replay buffer and marks the
    subject as complete (since recovered streams are always terminal).

    :param stream_provider: The durable stream provider to read from.
    :param response_id: Response whose events to hydrate.
    :param isolation: Multi-tenant isolation context.
    :param starting_after: If set, only load events after this sequence number.
    :returns: A hydrated subject, or None if no events available.
    """
    if starting_after is not None:
        events = await stream_provider.get_stream_events(
            response_id, starting_after=starting_after, isolation=isolation
        )
    else:
        events = await stream_provider.get_stream_events(
            response_id, isolation=isolation
        )

    if events is None or len(events) == 0:
        return None

    subject = _ResponseEventSubject()
    for event in events:
        await subject.publish(event)
    await subject.complete()
    return subject
