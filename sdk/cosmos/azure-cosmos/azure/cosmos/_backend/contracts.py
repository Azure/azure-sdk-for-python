# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Frozen request/reply records shared by sync and async backends.

PreparedRequest/BackendResponse describe single replies; PreparedQuery/QueryPage
describe pages. PreparedClientConfig carries construction settings. Invocation
deadlines and legacy callables are deliberately outside these wire records.

Frozen fields cannot be reassigned. Settings, partition inputs and query scope
are immutable; header maps and nested query data remain read-only by convention.
A cursor field references pager-owned mutable native execution state, not a
mapping the backend may rewrite."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Mapping, Optional, Union

from azure.core.utils import CaseInsensitiveDict
from .request_settings import RequestSettings
from .partition_key import PartitionKeyInput

if TYPE_CHECKING:
    from azure.cosmos._rust import ItemFeedCursor


@dataclass(frozen=True)
class ContainerMetadata:
    """Immutable routing facts, not a service response or a Python cache.

    ``partition_key_kind=None`` with no paths means no definition. An unknown
    system-key flag is distinct from False; the current driver does not retain it.
    """

    rid: str
    partition_key_paths: tuple[str, ...] = ()
    partition_key_kind: Optional[str] = None
    system_key: Optional[bool] = None


@dataclass(frozen=True)
class PreparedRequest:
    """A single Cosmos operation, fully prepared and ready to send.

    The Rust backend receives this object. The current core-Python backend
    receives a separate legacy callable built from the original Python
    arguments because those arguments cannot always be reconstructed from this
    wire-shaped record. On a Rust-selected client, that operation is also the
    temporary fallback for request shapes that have not been migrated yet.
    """

    protocol_version: ClassVar[int] = 3

    #: One of the ``OP_*`` constants in :mod:`~azure.cosmos._backend.operations`.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: Request body, already turned into JSON bytes. Empty for operations that
    #: send no body, such as ``delete_item``.
    body_bytes: bytes

    #: The partition key for this request, broken into its parts, along with
    #: where each part came from and how it was worked out.
    partition_key: PartitionKeyInput

    #: Actual HTTP request headers only, including customer headers.
    headers: Mapping[str, str] = field(default_factory=dict)

    #: Typed settings; headers contain only caller/default header overrides.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: Target item id. Operations that send no body, and those aimed at one
    #: item, require it. Create and upsert also carry the id already read out
    #: of the body when it is a non-empty string, which saves the binding
    #: parsing the JSON a second time. Callers that have not been updated may
    #: leave it unset, in which case the binding reads the body itself.
    item_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.partition_key, PartitionKeyInput):
            raise TypeError("PreparedRequest requires a typed PartitionKeyInput")


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
    ``acquire_driver_handle`` time -- the startup-time analog of :class:`PreparedRequest`.

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
    :class:`~azure.cosmos._backend._driver_registry.StrictDriverIsolationError`)
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
    #: the core-python default. Maps to ``ThrottlingRetryOptions.max_retry_count``.
    throttling_max_retry_count: Optional[int] = None

    #: Cumulative cap, in seconds, on time spent waiting across throttle retries
    #: -- the customer's ``retry_throttle_backoff_max`` (preferred) or
    #: ``retry_backoff_max``. ``None`` keeps the driver default (30 s), which
    #: matches core-python. Maps to ``ThrottlingRetryOptions.max_retry_wait_time``.
    throttling_max_retry_wait_time_seconds: Optional[float] = None

    #: Cross-region hedging threshold in milliseconds (the ``threshold_ms`` of
    #: the ``availability_strategy`` kwarg) when the customer *enabled* hedging
    #: (``availability_strategy=True`` or a dict). ``Some`` maps to
    #: ``AvailabilityStrategy::Hedging``. ``None`` means the customer did not
    #: enable hedging, so the binding sets ``AvailabilityStrategy::Disabled``,
    #: including when the complete client config is absent.
    #: (Python's ``threshold_steps_ms`` has no driver equivalent -- the
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

    #: Full response header map. Uncommon headers are kept, not filtered out.
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. May be empty for 204 / no-content.
    body: bytes = b""

    #: Diagnostics from the backend. The helper passes this along without
    #: looking inside it.
    diagnostics: Any = None


@dataclass(frozen=True)
class QueryScope:
    """Normalized query scope with a stable wire/bookmark representation."""

    feed_range: Optional[tuple[str, str]] = None
    allow_cross_partition: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.allow_cross_partition, bool):
            raise TypeError("allow_cross_partition must be bool")
        if self.feed_range is not None and (
            not isinstance(self.feed_range, tuple)
            or len(self.feed_range) != 2
            or any(not isinstance(bound, str) for bound in self.feed_range)
            or self.feed_range[0] >= self.feed_range[1]
        ):
            raise ValueError("feed_range must be a nonempty min/max string tuple")

    def as_dict(self) -> dict[str, object]:
        return {
            "feed_range": (
                list(self.feed_range) if self.feed_range is not None else None
            ),
            "allow_cross_partition": self.allow_cross_partition,
        }


@dataclass(frozen=True)
class PreparedQuery:
    """A paged query or read-feed request, fully prepared.

    The backend returns results a page at a time (see ``execute_pages``).
    Non-streaming ranked plans may buffer their candidate window before emitting.
    """

    protocol_version: ClassVar[int] = 3

    #: An operation that the page-dispatch tables support, whether it keeps a
    #: cursor between pages or not.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"`` -- the resource being queried. Empty for
    #: paged operations that cover a whole account (``list_databases``) and so
    #: have no container; the binding ignores the field for those.
    container_link: str

    #: Query text (``"SELECT * FROM c WHERE c.k = @k"``), or ``None`` for the
    #: parameterless list-many ops (read-all-items, list-databases, …).
    query: Optional[str] = None

    #: Query parameters (``{"name": "@k", "value": …}`` entries), in order.
    parameters: tuple = ()

    #: Typed scope; default is a cross-partition query.
    partition_key: PartitionKeyInput = field(
        default_factory=lambda: PartitionKeyInput("cross_partition")
    )

    #: Page-size hint (``x-ms-max-item-count``); ``None`` keeps the default.
    max_item_count: Optional[int] = None

    #: Continuation token seeding the *first* page, or ``None`` to start fresh.
    continuation: Optional[str] = None

    #: Actual HTTP request headers only.
    headers: Mapping[str, str] = field(default_factory=dict)
    #: Typed settings, preserved by the binding page adapter.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: The cursor the pager owns. ``None`` means this operation does not keep
    #: a cursor between pages.
    cursor: Optional[ItemFeedCursor] = None
    #: Normalized change-feed mode, start marker and scope; never SQL.
    change_feed: Optional[Mapping[str, Any]] = None
    #: Query scope, and whether a cross-partition query is allowed, for paging
    #: a query through a pager that keeps its cursor across pages.
    query_scope: Optional[QueryScope] = None

    def __post_init__(self) -> None:
        if not isinstance(self.partition_key, PartitionKeyInput):
            raise TypeError("PreparedQuery requires a typed PartitionKeyInput")
        if self.query_scope is not None and not isinstance(
            self.query_scope, QueryScope
        ):
            raise TypeError("PreparedQuery requires a typed QueryScope")


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

    #: Token for the next page (``x-ms-continuation``). A pager that keeps its
    #: cursor across pages may have more results without being able to give a
    #: token, so check ``has_more`` as well.
    continuation: Optional[str] = None

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Full response header map for this page. Uncommon headers are kept.
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. The response parser turns this into the result
    #: type for the resource, and turns failures into errors.
    body: bytes = b""

    #: Diagnostics from the backend. The helper passes this along without
    #: looking inside it.
    diagnostics: Any = None
    #: A pager that keeps its cursor across pages may have more results even
    #: when the driver cannot produce a token, so this can still be true.
    has_more: Optional[bool] = None
    continuation_supported: bool = True


#: The reply shapes that are implemented.
BackendReply = Union[BackendResponse, QueryPage]
