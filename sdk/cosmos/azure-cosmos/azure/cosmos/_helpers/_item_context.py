# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Client-owned item defaults and response headers, independent of transport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from azure.core.utils import CaseInsensitiveDict

if TYPE_CHECKING:
    from .._backend.cosmos_backend import CosmosBackend
    from ..aio._backend.cosmos_backend import AsyncCosmosBackend

_BackendT = TypeVar("_BackendT", "CosmosBackend", "AsyncCosmosBackend")


@dataclass(frozen=True)
class ItemClientDefaults:
    """Client defaults used by items and, for priority/bucket, database creation."""

    no_response_on_write: bool = False
    enable_compact_utf8_item_writes: bool = False
    priority: Optional[str] = None
    throughput_bucket: Optional[int] = None

    def apply_to_options(self, options: dict[str, Any]) -> None:
        """Fill request defaults without overriding per-call options or headers."""
        initial = options.get("initialHeaders") or {}
        headers = {name.lower() for name in initial}
        for key, header, value in (
            ("priorityLevel", "x-ms-cosmos-priority-level", self.priority),
            ("throughputBucket", "x-ms-cosmos-throughput-bucket", self.throughput_bucket),
        ):
            if value and not options.get(key) and header not in headers:
                options[key] = value


@dataclass
class ClientLastResponseHeaders:
    """Latest headers recorded for a client, replaced as responses are parsed.

    This is not a response history or per-operation storage. Concurrent calls
    share this state; use a result's headers or response hook for a specific call.
    Response publication copies headers so diagnostic mutations cannot alter
    the operation's result. It owns no transport or service metadata cache.
    """

    last_response_headers: CaseInsensitiveDict = field(default_factory=CaseInsensitiveDict)


@dataclass(frozen=True)
class ItemClientContext(Generic[_BackendT]):
    """Carry the sync or async backend type from client to database to container.

    Dependencies are passed directly, never recovered through a connection.
    """

    backend: _BackendT
    defaults: ItemClientDefaults = field(default_factory=ItemClientDefaults)
    response_state: ClientLastResponseHeaders = field(default_factory=ClientLastResponseHeaders)
