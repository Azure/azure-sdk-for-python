# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract backend type and the data classes used to talk to it.

``RustBackend`` is the backend going forward and the only one intended for
production use. The "core-python" selection runs the legacy in-place
implementation through the explicit :class:`~azure.cosmos._backend.legacy.LegacyBackend`
(see that module), kept only for testing and comparison, not as a long-term
alternative. Every concrete backend implements the ``CosmosBackend`` ABC
defined here.

Backends expose three dispatch methods, one per reply shape. ``execute`` and
``execute_pages`` are implemented today (the latter only for ``query_items`` /
``read_all_items``); ``execute_batch`` raises ``NotImplementedError`` until the
batch operation is added. Defining it now means adding that operation does not
change this file.

* ``execute`` -- one request, one reply (``BackendResponse``), for every
  single-reply operation (item CRUD, feed-range, offer).
* ``execute_pages`` -- one request, one page of results (``QueryPage``), for
  the query and read-many operations. One call fetches one page; the caller
  re-invokes it per page, carrying the previous page's continuation forward.
* ``execute_batch`` -- a transactional batch, one result per operation
  (``BatchResponse``). Reserved; not implemented yet.

The operation kind (create_item, read_item, query_items, …) rides on the
``PreparedRequest`` / ``PreparedQuery`` ``op`` field. Adding a single-reply
operation is one new ``op`` value plus one new branch in each backend's
``execute``; adding a query/read-many operation is the same for
``execute_pages``.

``PreparedRequest`` / ``BackendResponse`` and ``PreparedQuery`` / ``QueryPage``
/ the reserved ``PreparedBatch`` / ``BatchResponse`` are frozen dataclasses, so
a backend cannot *reassign* the fields of the input it received or the output
it produced. ``frozen`` guards the attributes, not the contents: the scalar
fields are immutable (``bytes`` / ``str`` / ``tuple``), but ``headers`` is a
plain ``dict`` whose entries a backend could still mutate in place, so backends
treat it as read-only by convention.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Mapping, Optional, Union

from azure.core.utils import CaseInsensitiveDict


# Operation discriminator values for ``PreparedRequest.op``.
OP_CREATE_ITEM = "create_item"
OP_DELETE_ITEM = "delete_item"
OP_READ_ITEM = "read_item"
OP_UPSERT_ITEM = "upsert_item"
OP_REPLACE_ITEM = "replace_item"
OP_PATCH_ITEM = "patch_item"
OP_QUERY_ITEMS = "query_items"
OP_READ_ALL_ITEMS = "read_all_items"
OP_READ_FEED_RANGES = "read_feed_ranges"
OP_FEED_RANGE_FROM_PARTITION_KEY = "feed_range_from_partition_key"
OP_IS_FEED_RANGE_SUBSET = "is_feed_range_subset"
OP_READ_OFFER = "read_offer"
OP_REPLACE_OFFER = "replace_offer"


# ``PreparedRequest.op`` -> binding function name. Shared by the sync and
# async backends so a new operation is wired in one place, not two.
#
# ``query_items`` / ``read_all_items`` are deliberately NOT here: they are
# multi-page feeds, not single-reply operations, so they are registered in
# ``QUERY_TO_BINDING_METHOD`` below and dispatched through ``execute_pages``,
# never through ``execute``.
OP_TO_BINDING_METHOD = {
    OP_CREATE_ITEM: "create_item",
    OP_UPSERT_ITEM: "upsert_item",
    OP_REPLACE_ITEM: "replace_item",
    OP_DELETE_ITEM: "delete_item",
    OP_READ_ITEM: "read_item",
    OP_PATCH_ITEM: "patch_item",
    OP_READ_FEED_RANGES: "read_feed_ranges",
    OP_FEED_RANGE_FROM_PARTITION_KEY: "feed_range_from_partition_key",
    OP_IS_FEED_RANGE_SUBSET: "is_feed_range_subset",  # client-side subset check -> Rust is_feed_range_subset entry point
    OP_READ_OFFER: "read_offer",  # throughput read (get_throughput) -> Rust read_offer entry point
    OP_REPLACE_OFFER: "replace_offer",  # throughput replace (replace_throughput) -> Rust replace_offer entry point
}


# ``PreparedQuery.op`` -> binding function name, mirroring ``OP_TO_BINDING_METHOD``
# for the query and read-many operations. A backend's ``execute_pages`` reads this
# (never ``OP_TO_BINDING_METHOD``) so a query op can never be reached through the
# single-reply ``execute`` path by accident.
QUERY_TO_BINDING_METHOD = {
    OP_QUERY_ITEMS: "query_items",
    OP_READ_ALL_ITEMS: "read_all_items",
}
# Reserved lookup for the batch operation, mirroring ``OP_TO_BINDING_METHOD``.
# Empty until that operation is added; adding a row does not change the
# dispatch code.
BATCH_TO_BINDING_METHOD: dict[str, str] = {}


class QueryNotSupportedByBackendError(RuntimeError):
    """Raised when the selected backend cannot execute a planned query."""


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    Both backends receive the *same* instance so neither re-derives the
    wire format from the original kwargs.
    """

    #: One of the ``OP_*`` constants above.
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

    #: Target document id for ops where the id is not carried in
    #: ``body_bytes`` (``delete_item`` has no body). ``None`` for ops
    #: that derive the id from the body (``create_item``).
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
    smuggled onto that request object -- ``PreparedRequest`` never carries one.
    Instead the coordinator builds one of these -- a small, named, typed request
    object -- and hands it to :meth:`CosmosBackend.run_operation` as its own
    argument, separate from ``PreparedRequest``: ``op`` names which operation is
    running (so a backend can branch or log on it exactly as it does on
    ``PreparedRequest.op``) and ``invoke`` is the zero-arg call the coordinator
    already knows how to build for that op. ``LegacyBackend`` reads only ``op``
    and ``invoke``; it never branches on ``None`` to decide whether to run it.
    """

    #: One of the ``OP_*`` constants above, naming the operation ``invoke`` runs.
    op: str

    #: Zero-arg call to the legacy ``client_connection`` method, already bound
    #: to this call's arguments by the coordinator. Returns the already-parsed
    #: final result (a sync coordinator's ``invoke`` returns it directly; an
    #: async coordinator's returns an awaitable of it).
    invoke: Callable[[], Any]


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
    #: kwarg, e.g. ``("Central US",)``). The mirror of ``preferred_locations``;
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
# ``PreparedQuery`` / ``QueryPage`` describe the request and reply for
# ``query_items`` and ``read_all_items``: a query (or read-many) request, and
# one page of its results. They are frozen like their single-reply siblings.
# ``PreparedBatch`` / ``BatchResponse`` are the same shape for the
# transactional-batch operation, defined now so the contract is fixed before
# that operation is built, but nothing produces or consumes them yet.


@dataclass(frozen=True)
class PreparedQuery:
    """A query (or read-many) request, fully prepared.

    The backend returns the results a page at a time (see ``execute_pages``),
    so a large result is never held in memory all at once.
    """

    #: A ``QUERY_TO_BINDING_METHOD`` key naming the query op.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"`` -- the resource being queried.
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

_RUST_COMPATIBILITY_FALLBACK_COUNT = 0


def rust_compatibility_fallback_count() -> int:
    """Return Rust attempts retried through a legacy compatibility operation."""
    return _RUST_COMPATIBILITY_FALLBACK_COUNT


class CosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (sync).

    A per-family coordinator (:class:`~azure.cosmos._helpers.item_helper.ItemHelper`,
    :class:`~azure.cosmos._helpers.throughput_helper.ThroughputHelper`,
    :class:`~azure.cosmos._helpers.feed_range_helper.FeedRangeHelper`) holds one of
    these by interface and drives its operations through :meth:`run_operation`
    without knowing which concrete backend it has. Engine selection and legacy
    fallback happen behind this interface: a rust-backed client holds a
    :class:`RustBackend` and a core-python client holds a
    :class:`~azure.cosmos._backend.legacy.LegacyBackend`, and every coordinator
    treats both the same -- none of them branch on ``None``, on which concrete
    backend they hold, or on ``execute`` returning ``None``. The operation kind is
    on ``prepared.op``; the backend branches on it.

    ``execute`` is the wire-level primitive (build one prepared request, send
    it, hand back the raw reply) that the rust path uses; the query/feed-range/
    offer routing helpers call it directly. The core-python
    :class:`~azure.cosmos._backend.legacy.LegacyBackend` is **not**
    ``PreparedRequest``-driven -- its work is the original public call arguments,
    not a wire request -- so it does not implement ``execute`` and instead
    overrides :meth:`run_operation` to run the legacy operation.
    """

    #: Short identifier used in the startup INFO log line. Subclasses
    #: set this from ``constants.BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single Cosmos operation on the wire and return the raw reply.

        Dispatch on ``prepared.op`` and return a ``BackendResponse`` for the
        caller to parse. This is the rust wire primitive; a backend that does
        not send prepared requests (the core-python legacy backend) does not
        implement it.
        """
        ...

    def run_operation(
        self,
        *,
        build_prepared: Callable[[], PreparedRequest],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
    ) -> Any:
        """Run one engine-selected operation end to end and return the final result.

        This is the single entry point every family coordinator uses (items,
        throughput, feed-range) so none of them ever has to interpret ``None``
        from selection or from ``execute`` to decide whether to call the legacy
        path -- the chosen backend does that here, behind the interface.

        The default is the engine (rust) flow: when the request is representable
        by this engine (``rust_eligible``), build the ``PreparedRequest`` lazily,
        send it with :meth:`execute`, and parse the reply; otherwise run the
        supplied legacy operation. ``LegacyBackend`` overrides this to always run
        the legacy operation.

        The two callables plus ``legacy_operation`` keep this class free of any
        dependency on the helper layer (it never imports ``parse_backend_response``)
        and keep :class:`PreparedRequest` data-oriented -- the legacy call is a
        separate, typed argument here (see :class:`LegacyOperation`), never
        something smuggled onto the request object:

        * ``build_prepared`` builds the ``PreparedRequest``; it is invoked only
          on the rust path, so a core-python client never does the extra
          partition-key / body work.
        * ``legacy_operation`` names the op and runs the legacy
          ``client_connection.<Op>Item`` call, returning the already-parsed result.
        * ``parse_response`` turns a rust ``BackendResponse`` into the final
          result (it binds the client connection and response hook).

        :keyword build_prepared: Zero-arg builder for the rust ``PreparedRequest``.
        :keyword legacy_operation: Typed port to the legacy call; see
            :class:`LegacyOperation`.
        :keyword parse_response: Parser from ``BackendResponse`` to final result.
        :keyword rust_eligible: ``False`` when this specific request cannot be
            represented on the rust path (e.g. a filtered / guarded patch), which
            forces the legacy operation even on a rust-backed client.
        :keyword fallback_exceptions: Narrow, operation-specific compatibility
            failures that should retry through the supplied legacy operation.
        :returns: The final result the public method returns to the caller.
        :rtype: Any
        """
        if not rust_eligible:
            return legacy_operation.invoke()
        try:
            prepared = build_prepared()
            response = self.execute(prepared)
            assert response is not None  # execute() only returns None for a None prepared request
            return parse_response(response)
        except fallback_exceptions:
            global _RUST_COMPATIBILITY_FALLBACK_COUNT  # pylint: disable=global-statement
            _RUST_COMPATIBILITY_FALLBACK_COUNT += 1
            return legacy_operation.invoke()

    # --- execute_pages is implemented by RustBackend; execute_batch is
    # reserved for the not-yet-built batch operation ----------------------
    #
    # Concrete (not abstract) so today's backends stay valid without
    # implementing them. A backend adds query or batch support by overriding
    # the method; this class does not change.

    def execute_pages(self, prepared: PreparedQuery) -> Iterator[QueryPage]:
        """Return a query (or read-many) result one ``QueryPage`` at a time.

        The default here raises; :class:`~azure.cosmos._backend.rust.RustBackend`
        overrides it (using ``QUERY_TO_BINDING_METHOD``) to dispatch
        ``query_items`` / ``read_all_items``. A backend that does not implement
        this -- ``LegacyBackend`` never reaches it, since its coordinators drive
        it through :meth:`run_operation` / the legacy call directly, not through
        ``execute_pages`` -- keeps this raising default.
        """
        raise NotImplementedError(
            "execute_pages is not implemented by this backend."
        )

    def execute_batch(self, prepared: PreparedBatch) -> BatchResponse:
        """Run a transactional batch and return one result per operation.

        Reserved: the batch operation is not implemented yet, so this raises.
        A backend that supports it overrides it (using
        ``BATCH_TO_BINDING_METHOD``).
        """
        raise NotImplementedError(
            "execute_batch is reserved for the transactional-batch operation "
            "and is not implemented yet."
        )


# ---------------------------------------------------------------------------
# Response-header normalisation (binding dict -> CaseInsensitiveDict)
# ---------------------------------------------------------------------------
#
# The binding hands back a plain dict keyed by the gateway's wire
# header names. The legacy core-python path surfaces azure-core's
# ``CaseInsensitiveDict`` (it just does ``copy.copy(response.headers)`` --
# the raw gateway headers, no renaming or aliasing). To keep
# ``last_response_headers`` lookups case-insensitive and identical across
# both backends, we wrap the binding's dict in the same type. No keys are
# added or renamed: both backends surface exactly the header names the
# gateway emitted (e.g. ``x-ms-cosmos-llsn``, ``x-ms-item-lsn``, ``lsn``).


def normalize_response_headers(
    headers: Optional[Mapping[str, Any]],
) -> Optional[CaseInsensitiveDict]:
    """Wrap the binding's response-header dict in a ``CaseInsensitiveDict``.

    A pure type-normalisation step: every key from the input is copied
    through unchanged so the rust path surfaces the same gateway header
    names the legacy path does. ``None`` or empty input returns ``None``.
    """
    if not headers:
        return None
    result = CaseInsensitiveDict()
    for raw_key, value in headers.items():
        result[raw_key] = value
    return result


def init_client_args(
    endpoint: str,
    master_key: Optional[str],
    client_config: Optional[PreparedClientConfig],
    token_credential: Optional[Any],
) -> tuple[Any, ...]:
    """Build the positional args for the Rust ``init_client`` call.

    A token credential rides as the 4th argument; master-key auth uses the
    3-argument form. ``factory._resolve_credential`` is contracted to set
    exactly one of the two. Shared by both backends so the call shape lives in
    one place.

    The exactly-one invariant is enforced here rather than assumed: if both are
    somehow set, the silent default would pick the token and drop the master
    key with no signal, so instead we raise -- a contract violation upstream is
    a bug, not something to paper over.
    """
    if master_key is not None and token_credential is not None:
        raise ValueError(
            "init_client_args received both master_key and token_credential; "
            "exactly one must be set (factory._resolve_credential is responsible "
            "for this)."
        )
    if token_credential is not None:
        return (endpoint, None, client_config, token_credential)
    return (endpoint, master_key, client_config)


def build_backend_response(
    status_code: Any,
    sub_status: Any,
    headers: Optional[Mapping[str, Any]],
    body: Any,
    diagnostics: Any = None,
) -> BackendResponse:
    """Wrap the binding's response tuple as a ``BackendResponse``.

    The binding currently returns ``(status, sub_status, headers, body)`` plus
    an optional fifth diagnostics payload. The diagnostics element is optional
    so older test doubles (or older bindings) that still return a 4-tuple keep
    working unchanged.
    """
    return BackendResponse(
        status_code=int(status_code),
        sub_status=int(sub_status),
        headers=normalize_response_headers(headers),
        body=bytes(body) if body else b"",
        diagnostics=diagnostics,
    )


# ---------------------------------------------------------------------------
# Client-level operations the Rust path does not implement yet
# ---------------------------------------------------------------------------
#
# A few public methods are *client-level* (not per-item), so they are not routed
# through the backend's ``execute`` dispatch the way point operations are. On a
# Rust-backed client they would otherwise fall straight through to the legacy
# core-python connection. The migration goal is for the Rust path to stand on its
# own, so rather than quietly borrowing core-python we raise.
# ``get_database_account`` is the one such method today.


def raise_account_read_unsupported(backend: Any) -> None:
    """Raise ``NotImplementedError`` for ``get_database_account`` on a Rust-backed
    client; do nothing on the core-python selection.

    :param backend: The client's chosen backend, or ``None`` for core-python.
        A non-``None`` backend means the Rust path is active, and this call has no
        Rust-path implementation yet, so it raises instead of falling back to the
        legacy connection. ``None`` is a no-op, so core-python keeps working unchanged.
    """
    if backend is None:
        return
    raise NotImplementedError(
        "get_database_account() is not yet available on the Rust backend "
        "(_backend='rust'). The rust driver reads account metadata internally for "
        "routing but does not yet expose it across the binding."
    )
