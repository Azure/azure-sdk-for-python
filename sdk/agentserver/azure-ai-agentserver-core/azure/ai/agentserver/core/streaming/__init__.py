# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unified streaming primitive — :class:`EventStream` Protocol +
``streams`` registry.

This subpackage is the SDK's unified streaming surface. The public
``__all__`` is **six** entries: the registry, the Protocol, and the
four exception types. The three SDK-bundled concrete classes
(``BroadcastEventStream``, ``ReplayEventStream``,
``FileBackedReplayEventStream``) live in the private
``_concrete`` submodule and are constructed exclusively by the
registry's three ``use_*`` configurators — external callers MUST
obtain instances via ``await streams.get_or_create(id)``.

See ``sdk/agentserver/specs/streaming.md`` for the authoritative
reference. See spec 017 for the executable spec.
"""

from __future__ import annotations

from ._protocol import (
    EventStream,
    EventStreamClosedError,
    EventStreamError,
    EventStreamGoneError,
    EventStreamNotFoundError,
)
from ._registry import streams


__all__ = [
    "streams",
    "EventStream",
    "EventStreamError",
    "EventStreamClosedError",
    "EventStreamGoneError",
    "EventStreamNotFoundError",
]
