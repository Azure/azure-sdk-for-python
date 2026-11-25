# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""List or query databases with stateless paging through the selected Python backend.

Each page iterator keeps its own continuation token. On the Rust path it builds
a prepared page request without a feed cursor, then parses a backend page.
The customer app receives an ItemPaged pager, not the page iterator itself.
"""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import replace
from typing import Any, Mapping, Optional

from azure.core.paging import ItemPaged
from azure.core.utils import CaseInsensitiveDict

from .. import http_constants
from .._backend.constants import is_rust_backend
from .._backend.contracts import PreparedPageRequest
from .._constants import _Constants, TimeoutScope
from .._operation_deadline import (
    legacy_deadline_kwargs,
    legacy_deadline_options,
    remaining_timeout,
)
from .._query_rust_routing import (
    build_list_databases_page,
    build_query_databases_page,
    can_use_rust_list_databases,
    can_use_rust_query_databases,
)
from ._request_settings import (
    HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE,
    compose_item_options,
    is_supported_operation_timeout,
    normalize_metadata_page_size,
    normalize_query_specification,
    reject_unsupported_feed_options,
)
from ._metadata_feed import MetadataFeedPageIterator, RecordingOptions


class _MetadataFeedTiming:
    """Retain the per-page timeout and optional whole-operation deadline.

    :param float or None timeout: Validated per-page timeout in seconds.
    :param float or None operation_deadline: Shared monotonic deadline for operation-scoped timing.
    """

    def __init__(self, timeout: Optional[float], operation_deadline: Optional[float]) -> None:
        self.timeout = timeout
        self.operation_deadline = operation_deadline

    def deadline(self) -> Optional[float]:
        if self.operation_deadline is not None:
            return self.operation_deadline
        return None if self.timeout is None else time.monotonic() + self.timeout


class ListDatabasesConfig(_MetadataFeedTiming):
    operation = "list_databases"
    response_key = "Databases"
    owner_name = "CosmosClient"
    query_payload: Optional[dict[str, Any]] = None
    unsupported_options: tuple[tuple[str, str], ...] = (
        ("session_token", "sessionToken"),
        ("populate_query_metrics", "populateQueryMetrics"),
        ("availability_strategy", "availabilityStrategy"),
        ("no_response", "responsePayloadOnWriteDisabled"),
    )

    def __init__(self, client: Any, kwargs: dict[str, Any]) -> None:
        started = time.monotonic()
        self.hook = kwargs.pop("response_hook", None)
        if self.hook is not None and not callable(self.hook):
            raise TypeError(f"{self.operation} response_hook must be callable or None.")
        self.options = deepcopy(compose_item_options(kwargs))
        for name, key in self.unsupported_options:
            if name in kwargs or key in self.options:
                raise TypeError(f"{self.operation}() does not support the '{name}' option")
        kwargs.pop("timeout", None)
        timeout = self.options.get("timeout")
        if not is_supported_operation_timeout(timeout):
            raise ValueError(f"{self.operation} timeout must be None or finite seconds >= 1 and < 2**64.")
        self.options.pop(_Constants.OperationStartTime, None)
        operation_deadline = (
            started + timeout
            if timeout is not None and self.options.get(_Constants.TimeoutScope) == TimeoutScope.OPERATION
            else None
        )
        super().__init__(timeout, operation_deadline)
        self.default_headers = dict(client.client_connection.default_headers)
        normalize_metadata_page_size(self.options, self.default_headers, operation=self.operation)
        self.kwargs = kwargs
        self.recording_options = RecordingOptions.snapshot(kwargs)
        self.telemetry_owner = client
        self.backend = client._adapter
        self.rust = is_rust_backend(self.backend)
        self.response_state = client._client_context.response_state
        self.connection = None if self.rust else client.client_connection

    @property
    def binding_operation(self) -> str:
        return "list_databases" if self.query_payload is None else "query_databases"

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        remaining_kwargs = self.kwargs.keys() - self.recording_options.kwargs.keys() - {_Constants.OperationStartTime}
        reject_unsupported_feed_options(self.operation, remaining_kwargs, self.options)
        eligible = (
            can_use_rust_list_databases(
                options=self.options,
                kwargs=self.kwargs,
                is_query_plan=False,
                resource_type=http_constants.ResourceType.Database,
            )
            if self.query_payload is None
            else can_use_rust_query_databases(
                query_payload=self.query_payload,
                options=self.options,
                kwargs=self.kwargs,
                is_query_plan=False,
                resource_type=http_constants.ResourceType.Database,
            )
        )
        if not eligible:
            if self.options.get("changeFeedState") is not None:
                raise TypeError(
                    f"{self.operation}() does not support 'changeFeedState'; "
                    "database feeds do not support change feed state."
                )
            headers = self.options.get("initialHeaders")
            if isinstance(headers, Mapping):
                overridden = sorted(
                    name for name in headers
                    if isinstance(name, str) and name.lower() in HEADERS_THE_DRIVER_WOULD_SILENTLY_OVERWRITE
                )
                if overridden:
                    hint = (
                        " To add an application label, set user_agent_suffix on CosmosClient."
                        if any(name.lower() == "user-agent" for name in overridden) else ""
                    )
                    raise TypeError(
                        f"{self.operation}() does not support 'initial_headers' overrides for "
                        f"{', '.join(repr(name) for name in overridden)}; remove these headers.{hint}"
                    )
            raise TypeError(
                f"{self.operation}() does not support the supplied request_options on Rust: "
                f"{', '.join(repr(name) for name in sorted(self.options))}."
            )
        options = dict(self.options)
        if token is not None:
            options["continuation"] = token
        else:
            options.pop("continuation", None)
        prepared = (
            build_list_databases_page(options=options, req_headers=self.default_headers)
            if self.query_payload is None
            else build_query_databases_page(
                query_payload=self.query_payload,
                options=options,
                req_headers=self.default_headers,
            )
        )
        return replace(
            prepared,
            settings=replace(prepared.settings, timeout_seconds=remaining_timeout(deadline)),
        )

    def legacy_page(
        self,
        token: Optional[str],
        deadline: Optional[float],
        response_headers: Optional[CaseInsensitiveDict] = None,
    ) -> Any:
        if self.connection is None:
            raise RuntimeError("A legacy database listing requires its selected connection.")
        options = legacy_deadline_options(self.options, deadline)
        options["continuation"] = token
        # The legacy path retries the request, never the customer app's success hook.
        # Explicit legacy execution must invoke the connection's internal feed coordinator.
        return self.connection._CosmosClientConnection__QueryFeed(  # pylint: disable=protected-access
            "/dbs",
            http_constants.ResourceType.Database,
            "",
            lambda body: body["Databases"],
            lambda _, body: body,
            self.query_payload,
            options,
            _feed_backend=self.backend,
            response_headers=response_headers,
            **legacy_deadline_kwargs(self.kwargs, deadline),
        )


class QueryDatabasesConfig(ListDatabasesConfig):
    operation = "query_databases"
    unsupported_options = ListDatabasesConfig.unsupported_options + (
        ("enable_cross_partition_query", "enableCrossPartitionQuery"),
        ("content_type", "contentType"),
    )

    def __init__(
        self,
        client: Any,
        query: Any,
        parameters: Any,
        kwargs: dict[str, Any],
    ) -> None:
        if query is not None:
            text, values = normalize_query_specification(query, parameters, operation=self.operation)
            self.query_payload = {"query": text, "parameters": list(values)}
        modes = client.client_connection._QueryCompatibilityMode
        self.query_mode_supported = client.client_connection._query_compatibility_mode in (
            modes.Default,
            modes.Query,
        )
        super().__init__(client, kwargs)

    def prepared(self, token: Optional[str], deadline: Optional[float]) -> PreparedPageRequest:
        if self.query_payload is not None and not self.query_mode_supported:
            raise SystemError("Unexpected query compatibility mode.")
        return super().prepared(token, deadline)


def list_databases(client: Any, kwargs: dict[str, Any]) -> ItemPaged[dict[str, Any]]:
    return ItemPaged(
        ListDatabasesConfig(client, kwargs),
        page_iterator_class=MetadataFeedPageIterator,
    )


def query_databases(client: Any, query: Any, parameters: Any, kwargs: dict[str, Any]) -> ItemPaged[Any]:
    return ItemPaged(
        QueryDatabasesConfig(client, query, parameters, kwargs),
        page_iterator_class=MetadataFeedPageIterator,
    )
