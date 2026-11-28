# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Coordinate database creation, property reads, deletion, and get-or-create.

This module is Python wrapper code. Its scope is the database resource, such
as "sales", not the complete database API or operations on its containers and
items. Get-or-create means obtaining the database, creating it if it does not
exist.

For example, DatabaseProxy.read() asks DatabaseHelper for the properties of
"sales". DatabaseHelper prepares the read and passes it to BindingAdapter.

BindingAdapter calls the binding, which translates the prepared inputs into
a Rust driver call. The Rust driver requests the properties from the service
backend.

The result returns through the binding and BindingAdapter. DatabaseHelper
uses the Python response-handling code to turn the returned body bytes into
the database properties given to the customer app.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from .. import exceptions
from .._backend.capabilities import OperationRouting
from .._backend.cosmos_backend import CosmosBackend

from .._backend.operations import (
    OP_CREATE_DATABASE,
    OP_DELETE_DATABASE,
    OP_READ_DATABASE,
)
from .._cosmos_responses import CosmosDict
from .._operation_deadline import legacy_deadline_kwargs, legacy_deadline_options, remaining_timeout
from ._client_context import ClientLastResponseHeaders
from ._resource_validation import validate_resource
from .._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    database_existence_read_options,
    is_delete_database_rust_eligible,
    read_database_routing,
    is_create_database_rust_eligible,
)
from .._helpers._response_parse import (
    process_backend_response,
    process_database_read_response,
    process_delete_response,
    validate_response_hook_is_synchronous,
    with_response_header_snapshot,
)


class DatabaseHelper:
    """Prepare and execute database operations through the selected Python backend."""

    def __init__(
        self, client_connection: Any, backend: CosmosBackend, *,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        """Store the legacy connection and the selected Python backend."""
        self._client_connection = client_connection
        self._backend = backend
        self._response_state = response_state

    def create_database(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Create one database, without exposing backend selection to the public method.

        Builds the account-level create request and drives it through the selected
        backend.
        ``response_hook`` is invoked once on success with the response headers and
        the created database.

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
        remaining_timeout(deadline)
        result = self._backend.run_operation(
            build_request=lambda: build_create_database_prepared(
                database,
                request_options,
                kwargs=operation_kwargs,
            ),
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
        )
        remaining_timeout(deadline)
        if hook is not None:
            hook(result.get_response_headers(), result)
        return result

    def read_database(
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
        """Read one database's properties, without exposing backend selection.

        Unsupported Rust-path calls fail rather than falling back.
        Explicit legacy-path selection remains available for migration. The
        two-argument hook gets a separate header snapshot on either path.

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
        remaining_timeout(deadline)
        result = self._backend.run_operation(
            build_request=lambda: build_read_database_prepared(
                database_id,
                request_options,
                kwargs=operation_kwargs,
            ),
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
        )
        remaining_timeout(deadline)
        return result

    def delete_database(
        self,
        database_link: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete a database.

        The response is still parsed so service errors and response headers are
        handled before this method returns ``None``.

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
        self._backend.run_operation(
            build_request=lambda: build_delete_database_prepared(
                database_link,
                request_options,
                kwargs=operation_kwargs,
            ),
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

    def create_database_if_not_exists(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        deadline: Optional[float] = None,
    ) -> CosmosDict:
        """Return the database, creating it only if it isn't already there.

        This reads the named database first and
        creates it only when the read comes back "not found" (404). So
        re-running an onboarding job for a name that already exists returns
        that database instead of failing with "already exists". Provisioning
        options (``offerThroughput``, ``autoUpgradePolicy``) are dropped from
        the read so they ride only the create -- the existence check must not
        try to set throughput. The Python coordinator owns this compound
        workflow because the driver exposes separate read and create operations.
        Both steps must support the supplied options before the first request.
        One deadline covers the workflow, without changing execution paths midway.
        ``response_hook`` receives isolated copies of the final response outside
        recovery and timeout handling. If creation conflicts with another caller,
        read the database once more. A failed follow-up read propagates without
        another creation attempt.

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

        def read_database() -> CosmosDict:
            remaining_timeout(deadline)
            return self._backend.run_operation(
                build_request=lambda: build_read_database_prepared(
                    database["id"],
                    read_options,
                    kwargs=operation_kwargs,
                ),
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

        try:
            result = read_database()
        except exceptions.CosmosResourceNotFoundError:
            try:
                remaining_timeout(deadline)
                result = self._backend.run_operation(
                    build_request=lambda: build_create_database_prepared(
                        database,
                        request_options,
                        kwargs=operation_kwargs,
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
                result = read_database()
        remaining_timeout(deadline)
        if hook is not None:
            hook(result.get_response_headers(), result)
        return result
