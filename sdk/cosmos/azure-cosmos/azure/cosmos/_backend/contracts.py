# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Frozen request/reply records shared by sync and async backends.

PreparedRequest/BackendResponse describe single replies; PreparedQuery/QueryPage
describe pages. PreparedClientConfig carries construction settings. Invocation
deadlines and legacy callables are deliberately outside these wire records.

Frozen fields cannot be reassigned. Headers and nested query data are owned
immutable snapshots; settings, partition inputs and query scope are immutable.
A cursor field references pager-owned mutable native execution state, not a
mapping the backend may rewrite."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Mapping, Optional, Union

from azure.core.utils import CaseInsensitiveDict
from .request_settings import RequestSettings, _ValidatedSettings
from .partition_key_input import BindingPartitionKey
from ._immutable import freeze_headers, freeze_json

if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor


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
    """Wire-shaped input for a single-response operation.

    Backend/native validation, metadata lookup, and routing may still be needed.

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
    partition_key: BindingPartitionKey

    #: Actual HTTP request headers only, including customer headers.
    headers: Mapping[str, str] = field(default_factory=dict)

    #: Typed settings; headers contain only caller/default header overrides.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: Target identifier consumed by the operation's adapter, such as an item
    #: id or a database name. Create and upsert also carry the id already read out
    #: of the body when it is a non-empty string, which saves the binding
    #: parsing the JSON a second time. Callers that have not been updated may
    #: leave it unset, in which case the binding reads the body itself.
    item_id: Optional[str] = None

    #: Retained SQL-query scope, separate from the service's JSON request body.
    query_scope: Optional[QueryScope] = None

    def __post_init__(self) -> None:
        if not isinstance(self.body_bytes, bytes):
            raise TypeError("PreparedRequest.body_bytes must be immutable bytes")
        if not isinstance(self.settings, RequestSettings):
            raise TypeError("PreparedRequest requires typed RequestSettings")
        if not isinstance(self.op, str) or not isinstance(self.container_link, str):
            raise TypeError("PreparedRequest operation and container_link must be strings")
        if self.item_id is not None and not isinstance(self.item_id, str):
            raise TypeError("PreparedRequest.item_id must be a string or None")
        if not isinstance(self.partition_key, BindingPartitionKey):
            raise TypeError("PreparedRequest requires a typed BindingPartitionKey")
        if self.query_scope is not None and not isinstance(self.query_scope, QueryScope):
            raise TypeError("PreparedRequest requires a typed QueryScope")
        object.__setattr__(self, "headers", freeze_headers(self.headers))


@dataclass(frozen=True)
class PreparedFaultInjectionRule(_ValidatedSettings):
    """Immutable typed fault-rule values; policy validation belongs to the builder."""

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
class PreparedClientConfig(_ValidatedSettings):
    """Client-construction settings carried to the rust driver at
    ``acquire_driver_handle`` time -- the startup-time analog of :class:`PreparedRequest`.

    ``build_client_config`` validates and normalizes these frozen values.
    Routing and operation defaults are distinct from the proxy and transport
    timeout settings, which configure a shared process-wide runtime. Some
    mappings are approximate; field comments describe the relevant limits.

    Config participates in native driver identity together with endpoint and
    credential. A differing identity can select a separate driver, subject to
    binding-owned runtime compatibility checks and successful native initialization.
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
    #: ``"checkout-westus2"``) forwarded for native User-Agent construction.
    #: It does not itself enable a service metric dimension. ``None`` -- and an
    #: empty string, which ``build_client_config`` normalizes to ``None`` -- carries nothing, so
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

    def __post_init__(self) -> None:
        for name in ("preferred_locations", "excluded_locations", "fault_injection_rules"):
            value = getattr(self, name)
            if not isinstance(value, (list, tuple)):
                raise TypeError(f"PreparedClientConfig.{name} must be a list or tuple")
            object.__setattr__(self, name, tuple(value))
        super().__post_init__()


@dataclass(frozen=True)
class BackendResponse:
    """Single-response record consumed by the prepared-request parsers.

    Rust dispatch produces this record. Legacy callable dispatch can return
    its public result directly without constructing one.
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
    """Input for one paged query or read-feed dispatch.

    The backend returns results a page at a time (see ``execute_pages``).
    Native validation, planning, and metadata discovery may still be required.
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
    partition_key: BindingPartitionKey = field(
        default_factory=lambda: BindingPartitionKey("cross_partition")
    )

    #: Page-size hint (``x-ms-max-item-count``); ``None`` keeps the default.
    max_item_count: Optional[int] = None

    #: Continuation token seeding the *first* page, or ``None`` to start fresh.
    continuation: Optional[str] = None

    #: Actual HTTP request headers only.
    headers: Mapping[str, str] = field(default_factory=dict)
    #: Typed settings, preserved by the binding page adapter.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: The cursor the pager owns. ``None`` selects stateless dispatch for
    #: this request; the operation may also support a cursor-based path.
    cursor: Optional[_ItemFeedCursor] = None
    #: Normalized change-feed mode, start marker and scope; never SQL.
    change_feed: Optional[Mapping[str, Any]] = None
    #: Query scope, and whether a cross-partition query is allowed, for paging
    #: a query through a pager that keeps its cursor across pages.
    query_scope: Optional[QueryScope] = None

    #: Immutable service JSON prepared once by a retained pager. When supplied,
    #: these bytes, rather than query/parameters, are the binding's query payload.
    query_body: Optional[bytes] = None

    def __post_init__(self) -> None:
        if not isinstance(self.settings, RequestSettings):
            raise TypeError("PreparedQuery requires typed RequestSettings")
        for name in ("op", "container_link"):
            if not isinstance(getattr(self, name), str):
                raise TypeError(f"PreparedQuery.{name} must be a string")
        for name in ("query", "continuation"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"PreparedQuery.{name} must be a string or None")
        if self.max_item_count is not None and type(self.max_item_count) is not int:
            raise TypeError("PreparedQuery.max_item_count must be an integer or None")
        if not isinstance(self.parameters, (tuple, list)):
            raise TypeError("PreparedQuery.parameters must be a list or tuple")
        if self.change_feed is not None and not isinstance(self.change_feed, Mapping):
            raise TypeError("PreparedQuery.change_feed must be a mapping or None")
        if not isinstance(self.partition_key, BindingPartitionKey):
            raise TypeError("PreparedQuery requires a typed BindingPartitionKey")
        if self.query_body is not None and not isinstance(self.query_body, bytes):
            raise TypeError("PreparedQuery.query_body must be immutable bytes")
        if self.query_scope is not None and not isinstance(
            self.query_scope, QueryScope
        ):
            raise TypeError("PreparedQuery requires a typed QueryScope")
        object.__setattr__(self, "headers", freeze_headers(self.headers))
        object.__setattr__(self, "parameters", freeze_json(self.parameters))
        object.__setattr__(self, "change_feed", freeze_json(self.change_feed))


@dataclass(frozen=True)
class QueryPage:
    """One raw page of a query or read-feed result.

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
