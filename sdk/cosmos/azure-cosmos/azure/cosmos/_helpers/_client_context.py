# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep the Python adapter, operation defaults, response headers and internal
telemetry registrations available to database, container, and operation helpers.

The customer app configures CosmosClient once. Its database and container
objects then retain the same CosmosClientContext, which groups references
to the existing Python adapter, ClientOperationDefaults, and
ClientLastResponseHeaders. The immutable telemetry handler registrations
default to empty; they contain no per-operation state and are not public
client constructor options.

Helpers use these references directly rather than retrieve them through
CosmosClientConnection. Creating the objects defined here does not send
requests. Synchronous and asynchronous clients use the same classes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, Mapping, Optional, TypeVar

from azure.core.utils import CaseInsensitiveDict

from .._availability_strategy_config import CrossRegionHedgingStrategy
from .._diagnostic_logging import DiagnosticLogging

if TYPE_CHECKING:
    from .._backend.cosmos_backend import CosmosBackend
    from ..aio._backend.cosmos_backend import AsyncCosmosBackend
    from .._telemetry import CompletionHandler

_BackendT = TypeVar("_BackendT", "CosmosBackend", "AsyncCosmosBackend")


@dataclass(frozen=True)
class ClientOperationDefaults:
    """Operation defaults, including the overall budget used when a call omits it."""

    no_response_on_write: bool = False
    enable_compact_utf8_item_writes: bool = False
    priority: Optional[str] = None
    throughput_bucket: Optional[int] = None
    hedging_threshold_ms: Optional[int] = None
    operation_timeout_seconds: Optional[float] = None

    def apply_timeout(self, kwargs: dict[str, Any]) -> None:
        """Resolve the default before preparation establishes a call or page deadline.

        :param dict[str, Any] kwargs: Working call keywords receiving the default when no timeout is set.
        :return: None.
        :rtype: None
        """
        if self.operation_timeout_seconds is None:
            return
        options = kwargs.get("request_options", kwargs.get("feed_options")) or {}
        if not isinstance(options, Mapping):
            return  # Argument preparation reports malformed option containers.
        timeout = kwargs.get("timeout", options.get("timeout"))
        if timeout is None:
            kwargs["timeout"] = self.operation_timeout_seconds

    def apply_to_options(self, options: dict[str, Any]) -> None:
        """Apply the saved hedging threshold and fill priority and bucket defaults.

        Truthy per-call priority and bucket values or matching headers prevent
        default insertion. A bucket of zero is treated as absent.

        :param dict[str, Any] options: Working request options updated with applicable client defaults.
        :return: None.
        :rtype: None
        """
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
class CosmosClientContext(Generic[_BackendT]):
    """Group one client's adapter, defaults, header state and telemetry registrations.

    Database and container proxies share this context and the client's existing
    adapter rather than copy settings or create another adapter. The adapter
    manages driver-handle acquisition and release; this context only retains
    its reference. The same ownership applies to sync and async clients.

    Defaults supply omitted operation settings; response_state holds the latest
    published headers, not per-operation response storage.
    """

    adapter: _BackendT
    defaults: ClientOperationDefaults = field(default_factory=ClientOperationDefaults)
    response_state: ClientLastResponseHeaders = field(default_factory=ClientLastResponseHeaders)
    # Test hook: no SDK code sets this. Tests add handlers here to receive each
    # call's completion, including the attempt payload, outcome and reasons.
    telemetry_handlers: tuple[CompletionHandler, ...] = ()
    diagnostic_logging: DiagnosticLogging = field(default_factory=DiagnosticLogging)
    tracing_attributes: Mapping[str, Any] = field(default_factory=dict)
