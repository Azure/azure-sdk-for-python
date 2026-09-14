# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unified streaming primitive — :class:`EventStream` Protocol +
``streams`` registry.

Pick a backing once at app startup via one of the registry's three
``use_*`` configurators, then obtain stream instances anywhere in
your process via ``await streams.get_or_create(id)`` and program
against the :class:`EventStream` Protocol.

See ``docs/streaming-guide.md`` for the developer guide (registry
API, backings, per-turn id convention, exception/wire mapping,
third-party-impl peer-registry pattern).
"""

from ._protocol import (
    EventStream,
    EventStreamClosedError,
    EventStreamError,
    EventStreamNotFoundError,
)
from ._registry import streams


__all__ = [
    "streams",
    "EventStream",
    "EventStreamError",
    "EventStreamClosedError",
    "EventStreamNotFoundError",
]
