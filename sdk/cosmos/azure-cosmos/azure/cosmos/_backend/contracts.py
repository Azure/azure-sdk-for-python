# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Hold the Python wrapper's inputs to and results from the Python/Rust binding.

Both client types use PreparedRequest for binding inputs and BackendResponse
for converted binding results. Page fetches start with PreparedPageRequest,
which the Python wrapper converts to PreparedRequest, and return BackendPage.
PreparedClientConfig holds per-client settings. Absolute deadlines and
legacy-path functions are passed separately.

Fields cannot be reassigned after construction. Request headers and nested
query values are also copied into read-only objects, so caller edits cannot
change a pending request. Response headers can still be edited. A feed cursor
also changes as more pages are fetched; freezing its containing record does not
freeze the cursor's progress.
"""

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
    """Container ID and partition-key definition returned by the binding.

    No paths and partition_key_kind=None mean no partition-key definition was
    supplied. system_key=None means the flag is unknown, not False. This object
    has no service response headers and does not cache container properties.
    """

    rid: str
    partition_key_paths: tuple[str, ...] = ()
    partition_key_kind: Optional[str] = None
    system_key: Optional[bool] = None


@dataclass(frozen=True)
class PreparedRequest:
    """Prepared inputs for an operation or page binding function.

    The binding may still validate values or fetch container properties before
    sending the request. This is not an HTTP request already sent to the service.

    The legacy path uses a separate function with the original call
    arguments; those cannot always be reconstructed from this object.
    """

    protocol_version: ClassVar[int] = 3

    #: One of the ``OP_*`` constants in :mod:`~azure.cosmos._backend.operations`.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"``.
    container_link: str

    #: Request body, already turned into JSON bytes. Empty for operations that
    #: send no body, such as ``delete_item``.
    body_bytes: bytes

    #: Supplied partition-key values, or an instruction such as extracting the
    #: key from the item. BindingPartitionKey keeps those cases distinct.
    partition_key: BindingPartitionKey

    #: Actual HTTP request headers only, including customer headers.
    headers: Mapping[str, str] = field(default_factory=dict)

    #: Named operation settings, separate from raw header overrides.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: Target identifier used by the binding function, such as an item
    #: id or a database name. Create and upsert also carry the id already read out
    #: of the body when it is a non-empty string, which saves the binding
    #: parsing the JSON a second time. Callers that have not been updated may
    #: leave it unset, in which case the binding reads the body itself.
    item_id: Optional[str] = None

    #: Limits on which partition keys a retained item query may search,
    #: separate from the SQL and parameters sent in the JSON body.
    query_scope: Optional[QueryScope] = None

    #: Returned resource address for a dictionary replacement target. It selects
    #: the original resource, not a recreated item with the same user ID.
    item_self_link: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.body_bytes, bytes):
            raise TypeError("PreparedRequest.body_bytes must be immutable bytes")
        if not isinstance(self.settings, RequestSettings):
            raise TypeError("PreparedRequest requires typed RequestSettings")
        if not isinstance(self.op, str) or not isinstance(self.container_link, str):
            raise TypeError("PreparedRequest operation and container_link must be strings")
        if self.item_id is not None and not isinstance(self.item_id, str):
            raise TypeError("PreparedRequest.item_id must be a string or None")
        if self.item_self_link is not None and not isinstance(self.item_self_link, str):
            raise TypeError("PreparedRequest.item_self_link must be a string or None")
        if not isinstance(self.partition_key, BindingPartitionKey):
            raise TypeError("PreparedRequest requires a typed BindingPartitionKey")
        if self.query_scope is not None and not isinstance(self.query_scope, QueryScope):
            raise TypeError("PreparedRequest requires a typed QueryScope")
        object.__setattr__(self, "headers", freeze_headers(self.headers))


@dataclass(frozen=True)
class PreparedFaultInjectionRule(_ValidatedSettings):
    """Test settings for making selected requests fail or wait.

    The builder checks allowed operations and value ranges. This object checks
    field types and keeps the resulting rule from being edited.
    """

    id: str
    #: Rust driver test-rule label, such as "ReadItem", not Python's "read_item".
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
    """Client settings passed to the binding when acquiring a driver handle.

    build_client_config checks the options and converts them to these fields.
    The binding uses them with the endpoint and credential to choose a shared
    CosmosDriver or create one. Proxy and connection/read timeout settings apply
    to CosmosDriverRuntime, even when clients use different CosmosDriver objects.
    """

    #: Regions in the customer's preferred order, such as ("West US", "East US").
    #: An empty tuple leaves the order to the driver.
    preferred_locations: tuple[str, ...] = ()

    #: Regions excluded from this client's operations, such as ("Central US",).
    #: An empty tuple excludes none through this setting.
    excluded_locations: tuple[str, ...] = ()

    #: Maximum retries after HTTP 429, when the service asks the client to slow
    #: down. Comes from retry_throttle_total or retry_total. None uses the driver default.
    throttling_max_retry_count: Optional[int] = None

    #: Maximum total seconds spent waiting between HTTP 429 retries. Comes from
    #: retry_throttle_backoff_max or retry_backoff_max. None uses the driver default.
    throttling_max_retry_wait_time_seconds: Optional[float] = None

    #: Delay before the driver may send another request to a different region
    #: while the first is still pending. This is called cross-region hedging.
    #: None disables it, including when the whole config is absent. The Python
    #: threshold_steps_ms setting is not passed because the driver has one threshold.
    hedging_threshold_ms: Optional[int] = None

    #: Optional label added to the User-Agent header, such as "orders-westus".
    #: The builder turns an empty string into None. The binding checks the
    #: driver's limit of 25 characters: letters, digits, "-", "_", ".", or "~".
    user_agent_suffix: Optional[str] = None

    #: Requested read consistency: Eventual, Session, or Strong. The binding
    #: maps Strong to the driver's GlobalStrong. None keeps the account default.
    #: The builder rejects BoundedStaleness and ConsistentPrefix.
    consistency_level: Optional[str] = None

    #: Whether CosmosDriverRuntime may use environment proxy settings:
    #: True allows them, False requires a direct connection, and None requests no change.
    proxy_allowed: Optional[bool] = None

    #: Requested seconds allowed to establish a connection. Applies to the
    #: shared CosmosDriverRuntime; None requests no override.
    connection_timeout_seconds: Optional[float] = None

    #: Python's read_timeout, in seconds. It limits a complete HTTP
    #: attempt: connecting, sending, and receiving, not just waiting for more
    #: response data. Applies to both item and account/container-property
    #: requests across the process. None requests no override.
    read_timeout_seconds: Optional[float] = None

    #: Internal test rules for failures and delays. Different rules prevent two
    #: clients from sharing the same driver.
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
    """Python wrapper representation of a binding response tuple.

    A supplied legacy-path function can return its public result directly,
    without creating this object.
    """

    #: HTTP status code.
    status_code: int

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Headers supplied by the binding, not necessarily the original service
    #: header map. Headers discarded by the driver cannot be recovered here.
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. May be empty for 204 / no-content.
    body: bytes = b""

    #: Driver request diagnostics. Response helpers expose a supplied value as
    #: text in the public diagnostics header.
    diagnostics: Any = None


@dataclass(frozen=True)
class QueryScope:
    """Define which partition-key range a query may search.

    feed_range contains lower and upper key-range bounds, or None for no such
    restriction. allow_cross_partition records whether the query may search
    across partitions. as_dict supplies these values for requests and
    continuation tokens.
    """

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
class PreparedPageRequest:
    """Inputs for fetching one page of query, listing, or change-feed results.

    The driver may still validate the request, decide how to run the query,
    or fetch container properties. Returning pages does not promise immediate
    results: some queries need to collect results before returning the first page.
    """

    protocol_version: ClassVar[int] = 3

    #: An operation name supported by the page-function tables for this cursor mode.
    op: str

    #: e.g. ``"dbs/{db}/colls/{coll}"`` -- the resource being queried. Empty for
    #: paged operations that cover a whole account (``list_databases``) and so
    #: have no container; the binding ignores the field for those.
    container_link: str

    #: Query text (``"SELECT * FROM c WHERE c.k = @k"``), or ``None`` for the
    #: operations without SQL, such as read_all_items and list_databases.
    query: Optional[str] = None

    #: Query parameters, such as {"name": "@customer", "value": "customer-17"}, in order.
    parameters: tuple = ()

    #: Partition-key selection. The default does not restrict the query to one key.
    partition_key: BindingPartitionKey = field(
        default_factory=lambda: BindingPartitionKey("cross_partition")
    )

    #: Page-size hint (``x-ms-max-item-count``); ``None`` keeps the default.
    max_item_count: Optional[int] = None

    #: Continuation token for this page, or None for no supplied token.
    #: A feed cursor can still carry progress from an earlier fetch.
    continuation: Optional[str] = None

    #: Actual HTTP request headers only.
    headers: Mapping[str, str] = field(default_factory=dict)
    #: Operation settings passed to the binding with the page request.
    settings: RequestSettings = field(default_factory=RequestSettings)

    #: Feed cursor retained by this Python page iterator. None selects stateless
    #: paging; a continuation token may still be supplied.
    cursor: Optional[_ItemFeedCursor] = None
    #: Change-feed settings: which changes to read, where to start, and which
    #: partition-key range to search. This is not SQL.
    change_feed: Optional[Mapping[str, Any]] = None
    #: Partition-key restrictions for retained item queries, including whether
    #: multiple partitions may be searched.
    query_scope: Optional[QueryScope] = None

    #: SQL and parameters already converted to JSON bytes for reuse across pages.
    #: For SQL requests, these bytes take precedence over query and parameters.
    query_body: Optional[bytes] = None

    def __post_init__(self) -> None:
        if not isinstance(self.settings, RequestSettings):
            raise TypeError("PreparedPageRequest requires typed RequestSettings")
        for name in ("op", "container_link"):
            if not isinstance(getattr(self, name), str):
                raise TypeError(f"PreparedPageRequest.{name} must be a string")
        for name in ("query", "continuation"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"PreparedPageRequest.{name} must be a string or None")
        if self.max_item_count is not None and type(self.max_item_count) is not int:
            raise TypeError("PreparedPageRequest.max_item_count must be an integer or None")
        if not isinstance(self.parameters, (tuple, list)):
            raise TypeError("PreparedPageRequest.parameters must be a list or tuple")
        if self.change_feed is not None and not isinstance(self.change_feed, Mapping):
            raise TypeError("PreparedPageRequest.change_feed must be a mapping or None")
        if not isinstance(self.partition_key, BindingPartitionKey):
            raise TypeError("PreparedPageRequest requires a typed BindingPartitionKey")
        if self.query_body is not None and not isinstance(self.query_body, bytes):
            raise TypeError("PreparedPageRequest.query_body must be immutable bytes")
        if self.query_scope is not None and not isinstance(
            self.query_scope, QueryScope
        ):
            raise TypeError("PreparedPageRequest requires a typed QueryScope")
        object.__setattr__(self, "headers", freeze_headers(self.headers))
        object.__setattr__(self, "parameters", freeze_json(self.parameters))
        object.__setattr__(self, "change_feed", freeze_json(self.change_feed))


@dataclass(frozen=True)
class BackendPage:
    """One backend page response, with information for the next fetch.

    Used for queries, listings, and change feeds, not only SQL query results.
    Keep the body as bytes so Python wrapper response helpers can parse the rows
    and turn service failures into the same exceptions used for other operations.
    """

    #: HTTP status code for the page fetch.
    status_code: int

    #: Continuation token returned in ``x-ms-continuation``. A retained item query
    #: may have more results without a resumable token; use its ``has_more`` value.
    continuation: Optional[str] = None

    #: Cosmos sub-status code (``x-ms-substatus``); ``0`` if absent.
    sub_status: int = 0

    #: Headers supplied by the binding for this page. This is not a guarantee
    #: that all original service headers are present.
    headers: Optional[CaseInsensitiveDict] = None

    #: Raw response body bytes. The response parser turns this into the result
    #: type for the resource, and turns failures into errors.
    body: bytes = b""

    #: Driver request diagnostics, exposed by response helpers as header text.
    diagnostics: Any = None
    #: Retained item queries can have more results without a continuation token.
    #: None means this field does not decide completion for this page path.
    has_more: Optional[bool] = None
    continuation_supported: bool = True


#: The reply shapes that are implemented.
BackendReply = Union[BackendResponse, BackendPage]
