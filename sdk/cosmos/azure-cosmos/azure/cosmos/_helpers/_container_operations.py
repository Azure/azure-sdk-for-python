# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Run container operations through the selected Python backend.

On the Rust path, builders create prepared requests and response helpers parse
backend responses. The legacy path keeps its connection calls for migration.
An execution failure never causes this helper to try the other path.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Mapping, Optional

from .._backend.capabilities import OperationRouting
from .._backend.contracts import BackendResponse, PreparedRequest
from .._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_READ_CONTAINER,
    OP_DELETE_CONTAINER,
    OP_REPLACE_CONTAINER,
)
from .._backend.cosmos_backend import CosmosBackend
from .._cosmos_responses import CosmosDict
from ..exceptions import CosmosResourceNotFoundError
from ..http_constants import StatusCodes, SubStatusCodes
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout
from .._helpers._request_container import (
    build_create_container_prepared,
    build_delete_container_prepared,
    build_read_container_prepared,
    build_replace_container_prepared,
    is_create_container_rust_eligible,
    is_delete_container_rust_eligible,
    is_read_container_rust_eligible,
    is_replace_container_rust_eligible,
)
from .._helpers._response_parse import (
    process_backend_response,
    process_create_response,
    process_delete_response,
    with_response_header_snapshot,
)
from .._helpers._wire_encoding import serialize_body_to_bytes


def container_creation_retry_delay(
    error: CosmosResourceNotFoundError, retry_count: int, deadline: Optional[float]
) -> Optional[float]:
    """Bound follow-up reads while a concurrent container creation finishes.

    Only 404/1013 after a create conflict permits up to nine additional reads.
    Waits grow from 100 ms to one second and never exceed the remaining budget.

    :param error: Failure from reading the concurrently created container.
    :type error: ~azure.cosmos.exceptions.CosmosResourceNotFoundError
    :param int retry_count: Number of additional reads already attempted.
    :param float or None deadline: Original operation deadline, if supplied.
    :return: Delay in seconds, or None to propagate the read failure.
    :rtype: float or None
    """
    if (
        error.status_code != StatusCodes.NOT_FOUND
        or error.sub_status != SubStatusCodes.CONTAINER_CREATE_IN_PROGRESS
    ):
        return None
    remaining = remaining_timeout(deadline)
    if retry_count >= 9:
        return None
    delay = min(0.1 * 2 ** retry_count, 1.0)
    return min(delay, remaining) if remaining is not None else delay


class ContainerHelper:
    """Prepare and run synchronous container operations."""

    def __init__(self, client_connection: Any, backend: CosmosBackend) -> None:
        """Store the legacy connection and the already-selected Python backend."""
        self._client_connection = client_connection
        self._backend = backend

    def create_container(
        self,
        database_link: Any,
        container_definition: Mapping[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        deadline: Optional[float] = None,
        prepared: Optional[PreparedRequest] = None,
    ) -> CosmosDict:
        """Create a container and return its properties.

        Unsupported Rust-path calls fail rather than falling back.
        Explicit legacy-path selection remains available for migration.

        :param Any database_link: Parent database resource link.
        :param Mapping[str, Any] container_definition: Container properties to create.
        :param Mapping[str, Any] request_options: Internal creation options.
        :keyword callable or None response_hook: Synchronous callback receiving copied headers and properties.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :keyword float or None deadline: Monotonic deadline shared by preparation and execution.
        :keyword PreparedRequest or None prepared: Preflighted request whose body is refreshed before execution.
        :return: Created container properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)

        def build_request() -> PreparedRequest:
            if prepared is not None:
                # GSI resolution changes the body, not the preflighted settings.
                return replace(prepared, body_bytes=serialize_body_to_bytes(container_definition))
            return build_create_container_prepared(
                database_link, container_definition, request_options, kwargs=operation_kwargs
            )

        remaining_timeout(deadline)
        result = self._backend.run_operation(
            build_request=build_request,
            routing=OperationRouting(
                OP_CREATE_CONTAINER,
                is_create_container_rust_eligible(
                    request_options,
                    operation_kwargs,
                ),
            ),
            legacy_call=lambda: self._client_connection.CreateContainer(
                database_link=database_link,
                collection=container_definition,
                options=legacy_deadline_options(request_options, deadline),
                **legacy_deadline_kwargs(operation_kwargs, deadline),
            ),
            process_response=lambda response: process_create_response(
                response,
                client_connection=self._client_connection,
            ),
            deadline=deadline,
        )
        remaining_timeout(deadline)
        # Headers come off the result, not off ``client_connection``. The
        # connection's ``last_response_headers`` is shared mutable state that any
        # concurrent call on the same client overwrites, so reading it here could
        # hand the hook another thread's headers alongside this call's body.
        on_response = with_response_header_snapshot(response_hook, copy_body=True)
        if on_response is not None:
            on_response(result.get_response_headers(), result)
        return result

    def read_container(
        self,
        container_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], Optional[CosmosDict]], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        routing: Optional[OperationRouting] = None,
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Read a container and return its properties.

        :param Any container_link: Container resource link.
        :param Mapping[str, Any] request_options: Internal read options.
        :keyword callable or None response_hook: Synchronous callback receiving copied headers and properties.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :keyword OperationRouting or None routing: Optional routing policy combined with read eligibility.
        :keyword float or None deadline: Monotonic deadline shared by preparation and execution.
        :return: Container properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        not_modified = False

        def process_response(response: BackendResponse) -> CosmosDict:
            nonlocal not_modified
            not_modified = response.status_code == 304
            return process_backend_response(response, client_connection=self._client_connection)

        supported = is_read_container_rust_eligible(request_options, operation_kwargs)
        routing = (
            OperationRouting(OP_READ_CONTAINER, supported)
            if routing is None
            else replace(routing, supported=routing.supported and supported)
        )
        # Reject an expired budget before starting the read.
        remaining_timeout(deadline)
        result = self._backend.run_operation(
            build_request=lambda: build_read_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            ),
            routing=routing,
            legacy_call=lambda: self._client_connection.ReadContainer(
                container_link,
                options=legacy_deadline_options(request_options, deadline),
                **legacy_deadline_kwargs(operation_kwargs, deadline),
            ),
            process_response=process_response,
            deadline=deadline,
        )
        # Reject late completion before invoking the response hook or returning success.
        remaining_timeout(deadline)
        on_response = with_response_header_snapshot(response_hook, copy_body=True)
        if on_response is not None:
            on_response(result.get_response_headers(), None if not_modified else result)
        return result

    def delete_container(
        self,
        container_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], None], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete through the selected Python backend without legacy replay.

        :param Any container_link: Container resource link.
        :param Mapping[str, Any] request_options: Internal deletion options.
        :keyword callable or None response_hook: Synchronous callback receiving copied headers and a None body.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :return: None.
        :rtype: None
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        on_response = with_response_header_snapshot(response_hook)
        if on_response is not None:
            operation_kwargs["response_hook"] = on_response
        self._backend.run_operation(
            build_request=lambda: build_delete_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            ),
            routing=OperationRouting(
                OP_DELETE_CONTAINER,
                is_delete_container_rust_eligible(request_options, operation_kwargs),
            ),
            legacy_call=lambda: self._client_connection.DeleteContainer(
                container_link,
                options=request_options,
                **operation_kwargs,
            ),
            process_response=lambda response: process_delete_response(
                response,
                client_connection=self._client_connection,
                response_hook=on_response,
            ),
        )

    def replace_container(
        self,
        container_link: Any,
        container_definition: Mapping[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Replace properties without legacy replay or callback mutation of the result.

        :param Any container_link: Container resource link.
        :param Mapping[str, Any] container_definition: Replacement container properties.
        :param Mapping[str, Any] request_options: Internal replacement options.
        :keyword callable or None response_hook: Synchronous callback receiving copied headers and properties.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :return: Replaced container properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        result = self._backend.run_operation(
            build_request=lambda: build_replace_container_prepared(
                container_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            ),
            routing=OperationRouting(
                OP_REPLACE_CONTAINER,
                is_replace_container_rust_eligible(request_options, operation_kwargs),
            ),
            legacy_call=lambda: self._client_connection.ReplaceContainer(
                container_link,
                collection=container_definition,
                options=request_options,
                **operation_kwargs,
            ),
            process_response=lambda response: process_backend_response(
                response,
                client_connection=self._client_connection,
            ),
        )
        on_response = with_response_header_snapshot(response_hook, copy_body=True)
        if on_response is not None:
            on_response(result.get_response_headers(), result)
        return result
