# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The request and reply objects backends exchange with the layer above them.

This is the vocabulary shared by the sync and async backends. A coordinator
builds one of the ``Prepared*`` objects, hands it to whichever backend it holds,
and reads back the matching reply object -- without knowing which backend that
is. Keeping the objects here, rather than beside either backend, is what lets
:mod:`azure.cosmos.aio._backend` share them with the sync package instead of
redefining them.

The three request/reply pairs correspond to the three dispatch methods on
:class:`~azure.cosmos._backend.base.CosmosBackend`:

* :class:`PreparedRequest` / :class:`BackendResponse` -- one request, one reply,
  for every single-reply operation (database create, item CRUD, feed-range,
  offer).
* :class:`PreparedQuery` / :class:`QueryPage` -- one request, one page, for the
  query and read-many operations.
* :class:`PreparedBatch` / :class:`BatchResponse` -- reserved for the
  transactional-batch operation; nothing produces or consumes them yet.

:class:`LegacyOperation` is the matching port for the core-python engine, whose
calls take per-operation argument shapes a wire request cannot carry.
:class:`PreparedClientConfig` is the startup-time analog of
:class:`PreparedRequest`, carried once at client construction rather than per
request.

Every type here is a frozen dataclass, so a backend cannot *reassign* the fields
of the input it received or the output it produced. ``frozen`` guards the
attributes, not the contents: the scalar fields are immutable (``bytes`` /
``str`` / ``tuple``), but ``headers`` is a plain ``dict`` whose entries a backend
could still mutate in place, so backends treat it as read-only by convention.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Union

from azure.core.utils import CaseInsensitiveDict


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    The Rust backend receives this object. The current core-Python backend
    receives a separate :class:`LegacyOperation` built from the original Python
    arguments because those arguments cannot always be reconstructed from this
    wire-shaped record. On a Rust-selected client, that operation is also the
    temporary fallback for request shapes that have not been migrated yet.
    """

    #: One of the ``OP_*`` constants in :mod:`~azure.cosmos._backend.operations`.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: Request body already serialized to JSON bytes. Empty for
    #: bodiless ops (e.g. ``delete_item``).
    body_bytes: bytes

    #: Partition-key header value already serialized to its on-wire
    #: JSON shape (e.g. ``'["customerA"]'``).
    partition_key_header: str

    #: Everything else that needs to ride on the request: triggers,
    #: indexing directive, intended-collection-rid, etc. Values are typically
    #: strings, but not always -- producers may carry a non-str (e.g. the
    #: ``__overall_timeout_seconds`` sentinel is a float), so the value type is
    #: ``Any``. The binding reads the typed sentinels directly and coerces every
    #: other value with ``str()``, so non-str values are tolerated by design.
    headers: Mapping[str, Any] = field(default_factory=dict)

    #: Target document id. Bodiless and target-specific operations require it.
    #: Create and upsert also carry the already-resolved body id when it is a
    #: non-empty string, avoiding another JSON parse in the binding; older
    #: callers may leave it unset and let the binding read the body.
    item_id: Optional[str] = None


@dataclass(frozen=True)
class LegacyOperation:
    """A typed, named port to one legacy core-python call, used in place of a
    bare callable.

    The legacy ``client_connection`` calls a coordinator (``ItemHelper``,
    ``ThroughputHelper``, ...) runs on this engine -- ``CreateItem`` /
    ``DeleteItem`` / ... -- take differently-shaped positional arguments per
    operation (``document`` vs ``new_document``, ``document_link`` vs
    ``database_or_container_link``, a patch's ``operations`` list, a filter
    predicate, ...) that a wire-shaped ``PreparedRequest`` has no fields for and
    cannot carry losslessly. So a backend cannot safely reconstruct the legacy
    call from ``PreparedRequest`` alone, and this is *not* an arbitrary callable
    attached to that request object -- ``PreparedRequest`` never carries one.
    Instead the coordinator builds one of these -- a small, named, typed request
    object -- and hands it to :meth:`CosmosBackend.run_operation` as its own
    argument, separate from ``PreparedRequest``: ``op`` names which operation is
    running (so a backend can branch or log on it exactly as it does on
    ``PreparedRequest.op``) and ``invoke`` is the zero-arg call the coordinator
    already knows how to build for that op. ``LegacyBackend`` reads only ``op``
    and ``invoke``; it never branches on ``None`` to decide whether to run it.
    """

    #: One of the ``OP_*`` constants in :mod:`~azure.cosmos._backend.operations`, naming the
    #: operation ``invoke`` runs.
    op: str

    #: Zero-arg call to the legacy ``client_connection`` method, already bound
    #: to this call's arguments by the coordinator. Returns the already-parsed
    #: final result (a sync coordinator's ``invoke`` returns it directly; an
    #: async coordinator's returns an awaitable of it).
    invoke: Callable[[], Any]


@dataclass(frozen=True)
class PreparedFaultInjectionRule:
    """Validated internal fault rule carried across the Python/Rust boundary."""

    id: str
    operation_type: str
    status_code: int
    sub_status: int = 0
    container_id: Optional[str] = None
    region: Optional[str] = None
    delay_ms: int = 0
    probability: float = 1.0
    hit_limit: Optional[int] = None
    enabled: bool = True


@dataclass(frozen=True)
class PreparedClientConfig:
    """Client-construction settings carried to the rust driver at
    ``init_client`` time -- the startup-time analog of :class:`PreparedRequest`.

    Only settings the rust driver can honor today are carried here; more fields
    are added as the driver gains support, and a backend reads exactly the
    fields it knows. Stored as immutable values so the backend cannot mutate
    what the client passed.

    Every field maps to a driver-side setting the binding applies when it builds
    the per-account rust driver: ``preferred_locations`` reorders endpoints, while
    the rest land on a driver-level ``OperationOptions`` (the driver's "account"
    layer that every request inherits) -- ``excluded_locations`` to
    ``excluded_regions``, the throttling fields to ``ThrottlingRetryOptions``,
    the hedging fields to an ``AvailabilityStrategy``, and ``consistency_level``
    to the ``ReadConsistencyStrategy``.

    The binding keys its rust-driver cache by ``(endpoint, credential, config)``,
    so this config is part of what selects a rust driver: a client whose settings
    match an existing live client's shares that rust driver, and a client whose
    settings differ gets its own rust driver that honors them (nothing is silently
    dropped). Building a separate rust driver per differing config is the default;
    opting into strict isolation (see
    :class:`~azure.cosmos._backend._driver_registry.StrictEngineIsolationError`)
    instead raises when a later client's config differs from the first live client's.
    """

    #: Ordered preferred region names exactly as the customer passed them
    #: (e.g. ``("West US", "East US")``), forwarded to the driver's
    #: preferred-region routing (which normalizes each name). An empty tuple
    #: means "no preference" -- the driver keeps its default endpoint ordering.
    preferred_locations: tuple[str, ...] = ()

    #: Region names to keep out of routing entirely (the ``excluded_locations``
    #: kwarg, e.g. ``("Central US",)``). The counterpart of ``preferred_locations``;
    #: an empty tuple means "no exclusions". Carried to the driver's
    #: ``OperationOptions.excluded_regions`` at the account level.
    excluded_locations: tuple[str, ...] = ()

    #: Max number of service-throttle (HTTP 429) retries -- the customer's
    #: ``retry_throttle_total`` (preferred) or ``retry_total``. ``None`` means
    #: "not tuned", so the driver keeps its own default (9), which matches
    #: Python-core's default. Maps to ``ThrottlingRetryOptions.max_retry_count``.
    throttling_max_retry_count: Optional[int] = None

    #: Cumulative cap, in seconds, on time spent waiting across throttle retries
    #: -- the customer's ``retry_throttle_backoff_max`` (preferred) or
    #: ``retry_backoff_max``. ``None`` keeps the driver default (30 s), which
    #: matches Python-core. Maps to ``ThrottlingRetryOptions.max_retry_wait_time``.
    throttling_max_retry_wait_time_seconds: Optional[float] = None

    #: Cross-region hedging threshold in milliseconds (the ``threshold_ms`` of
    #: the ``availability_strategy`` kwarg) when the customer *enabled* hedging
    #: (``availability_strategy=True`` or a dict). ``Some`` maps to
    #: ``AvailabilityStrategy::Hedging``. ``None`` means the customer did not
    #: enable hedging, so nothing is carried and the driver keeps its own
    #: behavior. (Python's ``threshold_steps_ms`` has no driver equivalent -- the
    #: driver models only a single threshold -- so it is intentionally dropped.)
    hedging_threshold_ms: Optional[int] = None

    #: User-agent suffix label (the ``user_agent_suffix`` kwarg, e.g.
    #: ``"checkout-westus2"``) the driver stamps on the User-Agent of every
    #: request it issues, so account metrics and support tickets can tell one
    #: service's traffic apart from another's. ``None`` -- and an empty string,
    #: which ``build_client_config`` normalizes to ``None`` -- carries nothing, so
    #: the driver keeps its default SDK User-Agent. The driver's suffix type is
    #: stricter than the legacy path: at most 25 header-safe characters
    #: (alphanumeric, ``-``, ``_``, ``.``, ``~``). A value that violates that is
    #: rejected loudly on the Rust path rather than silently dropped.
    user_agent_suffix: Optional[str] = None

    #: Client-level consistency level the customer chose at construction (the
    #: ``consistency_level`` kwarg, e.g. ``"Eventual"``), carried so the chosen
    #: level actually reaches the driver instead of every read falling back to the
    #: account default. ``None`` carries nothing, leaving the driver at the
    #: account default. Only the levels the driver can honor are carried --
    #: ``"Eventual"`` and ``"Session"`` map directly and ``"Strong"`` maps to the
    #: driver's ``GlobalStrong`` in the binding; ``build_client_config`` rejects
    #: ``"BoundedStaleness"`` / ``"ConsistentPrefix"`` (no driver equivalent yet)
    #: rather than silently dropping them.
    consistency_level: Optional[str] = None

    #: Runtime-level proxy switch for the rust driver. ``True`` lets the driver
    #: use proxy settings from environment variables (such as ``HTTPS_PROXY`` /
    #: ``HTTP_PROXY``); ``False`` forces a direct connection (no proxy); ``None``
    #: carries nothing, so the runtime keeps its existing env/default behavior.
    proxy_allowed: Optional[bool] = None

    #: Effective client connection timeout in seconds. The binding applies this
    #: to the Rust driver's process-wide ``max_connect_timeout``. ``None`` leaves
    #: the driver default unchanged.
    connection_timeout_seconds: Optional[float] = None

    #: Effective client socket-read timeout in seconds. The Rust transport has no
    #: read-inactivity timeout, so the binding uses this as the process-wide cap
    #: for one complete HTTP attempt (connect, send, and receive) on both the
    #: data-plane and metadata transports. ``None`` leaves driver defaults unchanged.
    read_timeout_seconds: Optional[float] = None

    #: Internal test-only Rust fault rules. Each rule is immutable so it safely
    #: participates in the binding's driver-cache identity.
    fault_injection_rules: tuple[PreparedFaultInjectionRule, ...] = ()



@dataclass(frozen=True)
class BackendResponse:
    """Normalised shape every backend produces, regardless of which
    backend's HTTP stack sent the request.

    Code above the backend never branches on which backend handled the
    call; it just reads these fields.
    """

    #: HTTP status code.
    status_code: int

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map (long-tail headers preserved).
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. May be empty for 204 / no-content.
    body: bytes = b""

    #: Per-backend diagnostics blob the helper does not introspect.
    diagnostics: Any = None


# ---------------------------------------------------------------------------
# Request/reply objects for the query and read-many operations, and the
# reserved objects for the transactional-batch operation
# ---------------------------------------------------------------------------
#
# ``PreparedQuery`` / ``QueryPage`` describe the request and reply for paged
# operations such as ``query_items``, ``read_all_items``, and ``list_databases``.
# They are frozen like their single-reply siblings.
# ``PreparedBatch`` / ``BatchResponse`` are the same shape for the
# transactional-batch operation, defined now so the contract is fixed before
# that operation is built, but nothing produces or consumes them yet.


@dataclass(frozen=True)
class PreparedQuery:
    """A paged query or read-feed request, fully prepared.

    The backend returns the results a page at a time (see ``execute_pages``),
    so a large result is never held in memory all at once.
    """

    #: A ``QUERY_TO_BINDING_METHOD`` key naming the paged operation.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"`` -- the resource being queried. Empty for
    #: the account-scoped paged ops (``list_databases``), which have no
    #: container; the binding ignores the field for those.
    container_link: str

    #: Query text (``"SELECT * FROM c WHERE c.k = @k"``), or ``None`` for the
    #: parameterless list-many ops (read-all-items, list-databases, …).
    query: Optional[str] = None

    #: Query parameters (``{"name": "@k", "value": …}`` entries), in order.
    parameters: tuple = ()

    #: Partition-key scope serialized to its on-wire JSON shape, or ``None``
    #: for a cross-partition query.
    partition_key_header: Optional[str] = None

    #: Page-size hint (``x-ms-max-item-count``); ``None`` keeps the default.
    max_item_count: Optional[int] = None

    #: Continuation token seeding the *first* page, or ``None`` to start fresh.
    continuation: Optional[str] = None

    #: Everything else that needs to ride on the request (consistency,
    #: session token, triggers, …). Values are usually strings but may be a
    #: non-str sentinel, so the value type is ``Any`` (see ``PreparedRequest``).
    headers: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QueryPage:
    """One raw page of a query (or read-many) result.

    The caller parses ``body`` using the same response parser as other Cosmos
    operations. Keeping the raw body here preserves existing error mapping and
    response-envelope handling while giving paged operations their own backend
    contract and explicit continuation token.
    """

    #: HTTP status code for the page fetch.
    status_code: int

    #: Token for the next page (``x-ms-continuation``); ``None`` when this
    #: is the last page.
    continuation: Optional[str] = None

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map for this page (long-tail headers preserved).
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. The existing response parser turns this into
    #: the resource-specific result envelope and maps non-success responses.
    body: bytes = b""

    #: Per-backend diagnostics blob the helper does not introspect.
    diagnostics: Any = None


@dataclass(frozen=True)
class PreparedBatch:
    """Reserved: an all-or-nothing transactional batch, fully prepared. Every
    operation in it shares one partition key and the service applies them all
    or none. Not produced by any code yet.
    """

    #: A ``BATCH_TO_BINDING_METHOD`` key naming the batch op.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: The shared partition key serialized to its on-wire JSON shape.
    partition_key_header: str

    #: The batch body already serialized to JSON bytes (the array of
    #: operations).
    body_bytes: bytes = b""

    #: Everything else that needs to ride on the request. Values are usually
    #: strings but may be a non-str sentinel, so the value type is ``Any``
    #: (see ``PreparedRequest``).
    headers: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BatchResponse:
    """Reserved: the reply to a batch -- one result per operation, in submit
    order. Not produced by any code yet.
    """

    #: HTTP status code for the batch as a whole.
    status_code: int

    #: One entry per operation in the submitted batch, in submit order.
    results: tuple = ()

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map (long-tail headers preserved).
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes.
    body: bytes = b""

    #: Per-backend diagnostics blob the helper does not introspect.
    diagnostics: Any = None


#: The reply types the three dispatch methods produce: ``execute`` returns a
#: ``BackendResponse``, ``execute_pages`` yields ``QueryPage``, and
#: ``execute_batch`` returns a ``BatchResponse``.
BackendReply = Union[BackendResponse, QueryPage, BatchResponse]
