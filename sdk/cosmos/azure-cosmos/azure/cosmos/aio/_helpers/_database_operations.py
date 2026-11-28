# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare database requests and await the selected Python backend.

The request builders and response parsers are shared with the synchronous
database helper. During migration, run_operation selects a permitted path
before execution; a failure does not cause a Rust operation to run again
through the legacy connection.

Each creation method uses one supplied deadline for its steps. On timeout,
run_with_deadline cancels the Python task and waits for it
to finish handling cancellation. This does not undo a database creation already
performed by the service backend. After successful completion and a remaining-time
check, the success hook runs synchronously, outside retries and run_with_deadline.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from ... import exceptions
from ..._backend.capabilities import OperationRouting
from ..._backend.operations import (
    OP_CREATE_DATABASE,
    OP_DELETE_DATABASE,
    OP_READ_DATABASE,
)
from ..._backend.contracts import PreparedRequest
from ..._cosmos_responses import CosmosDict
from ..._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout, run_with_deadline
from ..._helpers._client_context import ClientLastResponseHeaders
from ..._helpers._resource_validation import validate_resource
from ..._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    database_existence_read_options,
    is_delete_database_rust_eligible,
    read_database_routing,
    is_create_database_rust_eligible,
)
from ..._helpers._response_parse import (
    process_backend_response,
    process_database_read_response,
    process_delete_response,
    validate_response_hook_is_synchronous,
    with_response_header_snapshot,
)
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncDatabaseHelper:
    """Build prepared requests, await execution, and return database properties."""

    def __init__(
        self, client_connection: Any, backend: AsyncCosmosBackend, *,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        """Retain the Python backend, legacy connection, and optional response-header state."""
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
        """Create a database, such as {"id": "checkout"}, and return its properties.

        The supplied deadline covers preparation and awaited execution.
        On success, check the remaining time before calling response_hook once
        with copies of the headers and database properties.

        :param dict[str, Any] database: Database properties containing its ID.
        :param Mapping[str, Any] request_options: Internal creation options.
        :keyword callable or None response_hook: Synchronous callback receiving copied headers and properties.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :keyword float or None deadline: Monotonic deadline covering preparation and execution.
        :return: Created database properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_database response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "create_database")
        hook = with_response_header_snapshot(response_hook, copy_body=True)
        request_options = dict(request_options)

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
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Read database properties and preserve the response hook's 304 behavior.

        A 304 response means the database has not changed. The hook receives
        None instead of a body for that response.

        :param Any database_id: Name of the database to read.
        :param Mapping[str, Any] request_options: Internal read options.
        :keyword callable or None response_hook: Synchronous callback receiving headers and body, or None for HTTP 304.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :keyword float or None deadline: Monotonic deadline covering preparation and execution.
        :return: Database properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        if response_hook is not None and not callable(response_hook):
            raise TypeError("read_database response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "read_database")
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

        result = await run_with_deadline(
            lambda: self._backend.run_operation(
                build_request=build_request,
                routing=read_database_routing(request_options, operation_kwargs),
                legacy_call=lambda: self._client_connection.ReadDatabase(
                    "dbs/{}".format(database_id),
                    options=legacy_deadline_options(request_options, deadline),
                    **legacy_deadline_kwargs(operation_kwargs, deadline),
                ),
                process_response=lambda response: process_database_read_response(
                    response,
                    client_connection=self._client_connection,
                    response_hook=response_hook,
                ),
                deadline=deadline,
            ),
            deadline,
        )
        remaining_timeout(deadline)
        return result

    async def delete_database(
        self,
        database_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete a database.

        :param Any database_link: Database resource link to delete.
        :param Mapping[str, Any] request_options: Internal deletion options.
        :keyword callable or None response_hook: Synchronous callback receiving copied response headers.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords forwarded to execution.
        :return: None.
        :rtype: None
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("delete_database response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "delete_database")
        on_response = with_response_header_snapshot(
            (lambda headers, _body: response_hook(headers)) if response_hook is not None else None
        )
        if on_response is not None:
            operation_kwargs["response_hook"] = on_response

        def build_request() -> PreparedRequest:
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
            process_response=lambda response: process_delete_response(
                response,
                client_connection=self._client_connection,
                response_hook=on_response,
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
        """Return an existing database, or create it when the read reports not found.

        Check support for both operations before starting, and leave
        creation-only options off the read. Each step uses the same deadline.
        If another caller creates the database first, read it once more;
        a failed follow-up read is raised without another creation attempt.

        After the awaited work, call the synchronous response hook once with
        copies of the final headers and properties. Changes made by the hook
        do not change the result returned to the customer app.

        :param dict[str, Any] database: Database properties containing the ID to read or create.
        :param Mapping[str, Any] request_options: Creation options, filtered for existence reads.
        :keyword callable or None response_hook: Synchronous callback receiving copied final headers and properties.
        :keyword Mapping[str, Any] or None kwargs: Remaining operation keywords shared by the workflow.
        :keyword float or None deadline: Monotonic deadline shared by all workflow steps.
        :return: Existing or newly created database properties with response headers.
        :rtype: ~azure.cosmos.CosmosDict
        """
        validate_resource(database)
        if response_hook is not None and not callable(response_hook):
            raise TypeError("create_database_if_not_exists response_hook must be callable or None.")
        validate_response_hook_is_synchronous(response_hook, "create_database_if_not_exists")
        hook = with_response_header_snapshot(response_hook, copy_body=True)
        request_options = dict(request_options)
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        read_options = database_existence_read_options(request_options, operation_kwargs)
        # Both steps use the creation contract, including driver-owned header precedence.
        rust_eligible = is_create_database_rust_eligible(request_options, operation_kwargs)

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
