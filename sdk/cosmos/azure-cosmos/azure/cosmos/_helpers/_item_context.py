# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep the Python adapter, operation defaults, and response headers available
to database, container, and operation helpers.

The customer app configures CosmosClient once. Its database and container
objects then retain the same ItemClientContext, which groups references
to the existing Python adapter, ItemClientDefaults, and
ClientLastResponseHeaders.

Helpers use these references directly rather than retrieve them through
CosmosClientConnection. Creating the objects defined here does not send
requests. Synchronous and asynchronous clients use the same classes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

from azure.core.utils import CaseInsensitiveDict

from .._availability_strategy_config import CrossRegionHedgingStrategy

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
    hedging_threshold_ms: Optional[int] = None

    def apply_to_options(self, options: dict[str, Any]) -> None:
        """Fill request defaults without overriding per-call options or headers."""
        if options.get("availabilityStrategy") is True and self.hedging_threshold_ms is not None:
            options["availabilityStrategy"] = CrossRegionHedgingStrategy(
                {"threshold_ms": self.hedging_threshold_ms}
            )
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
    """Group references to one client's Python adapter, defaults, and header state.

    Client state means the information retained for a client, not the
    CosmosClient object itself. For a synchronous Rust-backed client with
    priority="High", the Python wrapper retains these references::

        CosmosClient object
            |
            +-- _adapter -----------------------> BindingAdapter object
            |                                         ^
            +-- _item_context -> ItemClientContext    |
                                     |                |
                                     +-- adapter -----+
                                     |
                                     +-- defaults -> ItemClientDefaults
                                     |                   priority = "High"
                                     |
                                     +-- response_state -> ClientLastResponseHeaders
                                                               latest headers

    There is one BindingAdapter object in this illustration, reached through
    two references. ItemClientContext is a separate object, not another
    CosmosClient. DatabaseProxy for "sales" and ContainerProxy for "orders"
    retain this same context rather than copy the adapter or prepare client
    settings again.

    Sharing the adapter keeps the client's saved settings, acquired driver
    handle, and closing state together. Operations on "sales" and "orders"
    therefore use the adapter managed by their parent CosmosClient.

    Creating another Python adapter would not necessarily create another
    CosmosDriver: the binding may reuse a driver. However, that adapter
    would manage its own acquisition and release of a driver handle.
    Passing the existing adapter through this context avoids introducing
    that separate ownership for each database or container object.

    ItemClientContext carries the reference; it does not acquire or release
    the driver handle itself.

    The defaults hold values used when operations omit their own, and the
    response_state holds the latest published headers. For an asynchronous
    Rust-backed client, adapter refers to AsyncBindingAdapter instead.
    """

    adapter: _BackendT
    defaults: ItemClientDefaults = field(default_factory=ItemClientDefaults)
    response_state: ClientLastResponseHeaders = field(default_factory=ClientLastResponseHeaders)
