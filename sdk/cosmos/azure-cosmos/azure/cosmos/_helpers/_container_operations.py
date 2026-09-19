# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Run container operations with the client's selected Python or Rust implementation."""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting

from dataclasses import replace
from typing import Any, Callable, Mapping, Optional


from .._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_READ_CONTAINER,
    OP_DELETE_CONTAINER,
    OP_REPLACE_CONTAINER,
)
from .._backend.cosmos_backend import CosmosBackend
from .._cosmos_responses import CosmosDict
from .._helpers._request_container import (
    build_create_container_prepared,
    build_delete_container_prepared,
    build_read_container_prepared,
    build_replace_container_prepared,
    is_create_container_rust_eligible,
    is_delete_container_rust_eligible,
    is_read_container_rust_eligible,
)
from .._helpers._response_parse import (
    process_backend_response,
    process_delete_response,
    with_response_header_snapshot,
)


class ContainerHelper:
    """Prepare and run synchronous container operations."""

    def __init__(self, client_connection: Any, backend: CosmosBackend) -> None:
        """Store the client connection and selected implementation."""
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
    ) -> CosmosDict:
        """Create a container and return its properties.

        Unsupported Rust calls fail rather than switching transports.
        Explicit legacy selection remains available.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        result = self._backend.run_operation(
            build_request=lambda: build_create_container_prepared(
                database_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            ),
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
                options=request_options,
                **operation_kwargs,
            ),
            process_response=lambda response: process_backend_response(
                response,
                client_connection=self._client_connection,
            ),
        )
        # Headers come off the result, not off ``client_connection``. The
        # connection's ``last_response_headers`` is shared mutable state that any
        # concurrent call on the same client overwrites, so reading it here could
        # hand the hook another thread's headers alongside this call's body.
        if response_hook is not None:
            response_hook(result.get_response_headers(), result)
        return result

    def read_container(
        self,
        container_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        routing: Optional[OperationRouting] = None,
    ) -> CosmosDict:
        """Read a container and return its properties."""
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        supported = is_read_container_rust_eligible(request_options, operation_kwargs)
        routing = (
            OperationRouting(OP_READ_CONTAINER, supported)
            if routing is None
            else replace(routing, supported=routing.supported and supported)
        )
        result = self._backend.run_operation(
            build_request=lambda: build_read_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            ),
            routing=(routing),
            legacy_call=lambda: self._client_connection.ReadContainer(
                container_link,
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

    def delete_container(
        self,
        container_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], None], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete through the selected backend without Rust-to-legacy replay."""
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
        """Replace properties without legacy replay or callback mutation of the result."""
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
                is_create_container_rust_eligible(request_options, operation_kwargs),
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
