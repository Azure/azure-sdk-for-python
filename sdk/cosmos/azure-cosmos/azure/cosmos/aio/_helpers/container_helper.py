# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Run async container operations with the selected Python or Rust implementation."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from ..._backend.base import (
    LegacyOperation,
    OP_CREATE_CONTAINER,
    OP_READ_CONTAINER,
)
from ..._cosmos_responses import CosmosDict
from ..._helpers._request_prep import (
    build_create_container_prepared,
    build_read_container_prepared,
    is_create_container_rust_eligible,
    is_read_container_rust_eligible,
)
from ..._helpers._response_parse import parse_backend_response
from .._backend.base import AsyncCosmosBackend
from .._backend.legacy import coerce_async_backend


class AsyncContainerHelper:
    """Prepare and run asynchronous container operations."""

    def __init__(self, client_connection: Any, backend: Optional[AsyncCosmosBackend]) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = coerce_async_backend(backend)

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

        async def build_prepared():
            """Build the prepared create-container request.

            The async backend awaits this callback, so the shared synchronous
            builder is wrapped in a coroutine rather than passed directly.
            """
            return build_create_container_prepared(
                database_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(
                op=OP_CREATE_CONTAINER,
                invoke=lambda: self._client_connection.CreateContainer(
                    database_link=database_link,
                    collection=container_definition,
                    options=request_options,
                    **operation_kwargs,
                ),
            ),
            parse_response=lambda response: parse_backend_response(
                response,
                client_connection=self._client_connection,
            ),
            rust_eligible=is_create_container_rust_eligible(
                request_options,
                operation_kwargs,
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
    ) -> CosmosDict:
        """Read a container and return its properties."""
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)

        async def build_prepared():
            """Build the prepared read-container request.

            The async backend awaits this callback, so the shared synchronous
            builder is wrapped in a coroutine rather than passed directly.
            """
            return build_read_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(
                op=OP_READ_CONTAINER,
                invoke=lambda: self._client_connection.ReadContainer(
                    container_link,
                    options=request_options,
                    **operation_kwargs,
                ),
            ),
            parse_response=lambda response: parse_backend_response(
                response,
                client_connection=self._client_connection,
            ),
            rust_eligible=is_read_container_rust_eligible(
                request_options,
                operation_kwargs,
            ),
        )
        # Headers come off the result, not off ``client_connection`` -- see the
        # note in ``create_container`` for why the shared field is unsafe here.
        if response_hook is not None:
            response_hook(result.get_response_headers(), result)
        return result
