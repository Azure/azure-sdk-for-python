# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Run container operations with the client's selected Python or Rust implementation."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from .._backend.contracts import LegacyOperation
from .._backend.operations import OP_CREATE_CONTAINER, OP_READ_CONTAINER
from .._backend.legacy import coerce_backend
from .._cosmos_responses import CosmosDict
from .._helpers._request_container import (
    build_create_container_prepared,
    build_read_container_prepared,
    is_create_container_rust_eligible,
    is_read_container_rust_eligible,
)
from .._helpers._response_parse import parse_backend_response


class ContainerHelper:
    """Prepare and run synchronous container operations."""

    def __init__(self, client_connection: Any, backend: Optional[Any]) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = coerce_backend(backend)

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

        The Python implementation is used when a request option is not supported
        by the Rust implementation.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        result = self._backend.run_operation(
            build_prepared=lambda: build_create_container_prepared(
                database_link,
                container_definition,
                request_options,
                kwargs=operation_kwargs,
            ),
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
    ) -> CosmosDict:
        """Read a container and return its properties."""
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        result = self._backend.run_operation(
            build_prepared=lambda: build_read_container_prepared(
                container_link,
                request_options,
                kwargs=operation_kwargs,
            ),
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
