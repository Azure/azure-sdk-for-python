# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Run async container operations with the selected Python or Rust implementation."""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting

from dataclasses import replace
from typing import Any, Callable, Mapping, Optional

from ..._backend.contracts import PreparedRequest
from ..._backend.operations import (
    OP_CREATE_CONTAINER,
    OP_READ_CONTAINER,
    OP_DELETE_CONTAINER,
    OP_REPLACE_CONTAINER,
)
from ..._cosmos_responses import CosmosDict
from ..._helpers._request_container import (
    build_create_container_prepared,
    build_delete_container_prepared,
    build_read_container_prepared,
    build_replace_container_prepared,
    is_create_container_rust_eligible,
    is_delete_container_rust_eligible,
    is_read_container_rust_eligible,
)
from ..._helpers._response_parse import (
    process_backend_response,
    process_delete_response,
    with_response_header_snapshot,
)
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncContainerHelper:
    """Prepare and run asynchronous container operations."""

    def __init__(self, client_connection: Any, backend: AsyncCosmosBackend) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = backend

    async def create_container(
        self,
        database_link: Any,
        container_definition: Mapping[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Create a container and return its properties."""
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)

        def build_request() -> PreparedRequest:
            """Build the prepared create-container request.

            Construction is synchronous; only backend execution is awaited.
            """
            return build_create_container_prepared(
                database_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
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
        # other task on the same client overwrites, so reading it here could hand
        # the hook another call's headers alongside this call's body.
        if response_hook is not None:
            response_hook(result.get_response_headers(), result)
        return result

    async def read_container(
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

        def build_request() -> PreparedRequest:
            """Build the prepared read-container request.

            Construction is synchronous; only backend execution is awaited.
            """
            return build_read_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            )

        supported = is_read_container_rust_eligible(request_options, operation_kwargs)
        routing = (
            OperationRouting(OP_READ_CONTAINER, supported)
            if routing is None
            else replace(routing, supported=routing.supported and supported)
        )
        result = await self._backend.run_operation(
            build_request=build_request,
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

    async def delete_container(
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

        def build_request() -> PreparedRequest:
            return build_delete_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            )

        await self._backend.run_operation(
            build_request=build_request,
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

    async def replace_container(
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

        def build_request() -> PreparedRequest:
            return build_replace_container_prepared(
                container_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_request=build_request,
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
