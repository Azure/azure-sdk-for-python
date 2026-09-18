# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async counterpart of the backend-neutral database coordinator.

Request builders are synchronous; service execution is awaited. Creation uses
one deadline and waits for cancellation to finish before returning. Success
hooks remain ordinary synchronous callables, outside request retries and the
async timeout wrapper.
"""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting

from typing import Any, Callable, Mapping, Optional

from ... import exceptions
from ..._backend.operations import (
    OP_CREATE_DATABASE,
    OP_DELETE_DATABASE,
    OP_READ_DATABASE,
)
from ..._backend.contracts import PreparedRequest
from ..._constants import _Constants as Constants
from ..._cosmos_responses import CosmosDict
from ..._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout, run_with_deadline
from ..._helpers._item_context import ClientLastResponseHeaders
from ..._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    database_existence_read_options,
    is_delete_database_rust_eligible,
    is_read_database_rust_eligible,
    is_create_database_rust_eligible,
)
from ..._helpers._response_parse import (
    process_backend_response,
    process_database_read_response,
    with_response_header_snapshot,
)
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncDatabaseHelper:
    """Route async database operations through the selected backend boundary."""

    def __init__(
        self, client_connection: Any, backend: AsyncCosmosBackend, *,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = backend
        self._response_state = response_state

    async def create_database(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Async twin of :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.create_database`.

        Per-call ``read_timeout`` is not supported; callers configure the read
        timeout when constructing ``CosmosClient``. ``response_hook`` is invoked
        once on success with the response headers and created database, matching
        the legacy async connection contract.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_database response_hook must be callable or None.")
        hook = with_response_header_snapshot(response_hook, copy_body=True)
        if (
            request_options.get(Constants.Kwargs.READ_TIMEOUT) is not None
            or operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None
        ):
            raise TypeError(
                "create_database() does not support the 'read_timeout' keyword argument"
            )
        operation_kwargs.pop("read_timeout", None)
        request_options = dict(request_options)
        request_options.pop("read_timeout", None)

        def build_request() -> PreparedRequest:
            return build_create_database_prepared(
                database,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await run_with_deadline(
            lambda: self._backend.run_operation(
                build_request=build_request,
                routing=OperationRouting(
                    OP_CREATE_DATABASE,
                    is_create_database_rust_eligible(request_options, operation_kwargs),
                ),
                legacy_call=lambda: self._client_connection.CreateDatabase(
                    database=database,
                    options=legacy_deadline_options(request_options, deadline),
                    **legacy_deadline_kwargs(operation_kwargs, deadline),
                ),
                process_response=lambda response: process_backend_response(
                    response,
                    client_connection=self._client_connection if self._response_state is None else None,
                    response_state=self._response_state,
                ),
                deadline=deadline,
            ),
            deadline,
        )
        remaining_timeout(deadline)
        if hook is not None:
            hook(result.get_response_headers(), result)
        return result

    async def read_database(
        self,
        database_id: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[
            Callable[[Mapping[str, Any], Optional[dict[str, Any]]], None]
        ] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Async twin of
        :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.read_database`."""
        response_hook = with_response_header_snapshot(response_hook)
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None:
            operation_kwargs["response_hook"] = response_hook

        def build_request() -> PreparedRequest:
            return build_read_database_prepared(
                database_id,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_request=build_request,
            routing=OperationRouting(
                OP_READ_DATABASE,
                is_read_database_rust_eligible(
                    request_options,
                    operation_kwargs,
                ),
            ),
            legacy_call=lambda: self._client_connection.ReadDatabase(
                "dbs/{}".format(database_id),
                options=request_options,
                **operation_kwargs,
            ),
            process_response=lambda response: process_database_read_response(
                response,
                client_connection=self._client_connection,
                response_hook=response_hook,
            ),
        )
        return result

    async def delete_database(
        self,
        database_link: Any,
        request_options: Mapping[str, Any],
        *,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete a database."""
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)

        def build_request() -> PreparedRequest:
            """Build the prepared delete-database request.

            Construction is synchronous; only backend execution is awaited.
            """
            return build_delete_database_prepared(
                database_link,
                request_options,
                kwargs=operation_kwargs,
            )

        await self._backend.run_operation(
            build_request=build_request,
            routing=OperationRouting(
                OP_DELETE_DATABASE,
                is_delete_database_rust_eligible(
                    request_options,
                    operation_kwargs,
                ),
            ),
            legacy_call=lambda: self._client_connection.DeleteDatabase(
                database_link,
                options=request_options,
                **operation_kwargs,
            ),
            process_response=lambda response: process_backend_response(
                response,
                client_connection=self._client_connection,
            ),
        )

    async def create_database_if_not_exists(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Async twin of
        :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.create_database_if_not_exists`.

        Same retry-safe behavior: read the named database first and create it
        only when the read returns "not found" (404), so re-running setup for a
        name that already exists returns that database instead of failing. Same
        stripping of provisioning options from the read. The Python
        coordinator composes separate driver operations under one deadline,
        validating both steps before dispatch. Cancellation drains the pending
        request work. The synchronous success hook receives isolated final-response
        copies outside recovery and timeout handling. If creation
        conflicts with another caller, read the database once more. A failed
        follow-up read propagates without another creation attempt.
        """
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_database_if_not_exists response_hook must be callable or None.")
        hook = with_response_header_snapshot(response_hook, copy_body=True)
        request_options = dict(request_options)
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        read_options = database_existence_read_options(request_options, operation_kwargs)
        rust_eligible = (
            is_read_database_rust_eligible(read_options, operation_kwargs)
            and is_create_database_rust_eligible(request_options, operation_kwargs)
        )

        def build_read_prepared() -> PreparedRequest:
            return build_read_database_prepared(
                database["id"],
                read_options,
                kwargs=operation_kwargs,
            )

        async def read_database() -> CosmosDict:
            remaining_timeout(deadline)
            return await self._backend.run_operation(
                build_request=build_read_prepared,
                routing=OperationRouting(
                    OP_READ_DATABASE,
                    rust_eligible,
                    capability="create_database_if_not_exists",
                ),
                legacy_call=lambda: self._client_connection.ReadDatabase(
                    "dbs/{}".format(database["id"]),
                    options=legacy_deadline_options(read_options, deadline),
                    **legacy_deadline_kwargs(operation_kwargs, deadline),
                ),
                process_response=lambda response: process_backend_response(
                    response,
                    client_connection=self._client_connection if self._response_state is None else None,
                    response_state=self._response_state,
                ),
                deadline=deadline,
            )

        async def get_or_create() -> CosmosDict:
            try:
                return await read_database()
            except exceptions.CosmosResourceNotFoundError:
                try:
                    remaining_timeout(deadline)
                    return await self._backend.run_operation(
                        build_request=lambda: build_create_database_prepared(
                            database, request_options, kwargs=operation_kwargs,
                        ),
                        routing=OperationRouting(
                            OP_CREATE_DATABASE,
                            rust_eligible,
                            capability="create_database_if_not_exists",
                        ),
                        legacy_call=lambda: self._client_connection.CreateDatabase(
                            database=database,
                            options=legacy_deadline_options(request_options, deadline),
                            **legacy_deadline_kwargs(operation_kwargs, deadline),
                        ),
                        process_response=lambda response: process_backend_response(
                            response,
                            client_connection=self._client_connection if self._response_state is None else None,
                            response_state=self._response_state,
                        ),
                        deadline=deadline,
                    )
                except exceptions.CosmosResourceExistsError:
                    return await read_database()

        result = await run_with_deadline(get_or_create, deadline)
        remaining_timeout(deadline)
        if hook is not None:
            hook(result.get_response_headers(), result)
        return result
