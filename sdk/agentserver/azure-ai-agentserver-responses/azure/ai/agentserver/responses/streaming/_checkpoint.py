# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Internal checkpoint event for developer-driven persistence.

``ResponseEventStream.checkpoint()`` returns a :class:`ResponseCheckpointEvent`
that the handler yields like any other stream event. The orchestrator intercepts
it (before event coercion/validation), persists the carried response
snapshot via the storage provider, and does NOT forward it to the SSE wire — it
is purely an internal control signal, never part of the response event taxonomy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import _generated as _generated_models

if TYPE_CHECKING:
    pass


class ResponseCheckpointEvent:
    """A yielded request to persist the current response snapshot.

    Carries a reference to the stream's live ``ResponseObject``; the orchestrator
    snapshots and persists it (for resilient background responses only). Never
    serialised to the wire.
    """

    __slots__ = ("response",)

    def __init__(self, response: "_generated_models.ResponseObject") -> None:
        self.response = response
