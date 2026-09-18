# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Coordinate account-level database operations through the selected backend.

Public clients delegate execution and response handling here. Builders prepare
Rust requests without transport state; unsupported Rust settings fail before
dispatch rather than switching to legacy Python. Explicit legacy selection
retains its connection calls. Creation accepts client-owned response state and
gives its success hook independent copies of that operation's result.
"""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting

from typing import Any, Callable, Mapping, Optional

from .. import exceptions
from .._backend.cosmos_backend import CosmosBackend

from .._backend.operations import (
    OP_CREATE_DATABASE,
    OP_DELETE_DATABASE,
    OP_READ_DATABASE,
)
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._operation_deadline import legacy_deadline_options, remaining_timeout
from ._item_context import ClientLastResponseHeaders
from .._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    is_delete_database_rust_eligible,
    is_read_database_rust_eligible,
    is_create_database_rust_eligible,
)
from .._helpers._response_parse import (
    process_backend_response,
    process_database_read_response,
    with_response_header_snapshot,
)


class DatabaseHelper:
    """Route database operations through the selected backend boundary."""

    def __init__(
        self, client_connection: Any, backend: CosmosBackend, *,
        response_state: Optional[ClientLastResponseHeaders] = None,
    ) -> None:
        """Store the client connection and selected implementation."""
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
        backend. ``create_database`` does not support a per-call ``read_timeout``;
        callers configure the read timeout when constructing ``CosmosClient``.
        ``response_hook`` is invoked once on success with the response headers and
        the created database.
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
                **operation_kwargs,
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
    ) -> CosmosDict:
        """Read one database's properties, without exposing backend selection.

        Unsupported Rust calls fail rather than borrowing legacy transport.
        Explicit legacy selection remains available. The two-argument hook gets
        a separate header snapshot on either backend.
        """
        response_hook = with_response_header_snapshot(response_hook)
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None:
            operation_kwargs["response_hook"] = response_hook
        result = self._backend.run_operation(
            build_request=lambda: build_read_database_prepared(
                database_id,
                request_options,
                kwargs=operation_kwargs,
            ),
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

    def delete_database(
        self,
        database_link: Any,
        request_options: Mapping[str, Any],
        *,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Delete a database.

        The response is still parsed so service errors and response headers are
        handled before this method returns ``None``.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
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
            process_response=lambda response: process_backend_response(
                response,
                client_connection=self._client_connection,
            ),
        )

    def create_database_if_not_exists(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Return the database, creating it only if it isn't already there.

        This is the retry-safe create: it reads the named database first and
        creates it only when the read comes back "not found" (404). So
        re-running an onboarding job for a name that already exists returns
        that database instead of failing with "already exists". Provisioning
        options (``offerThroughput``, ``autoUpgradePolicy``) are dropped from
        the read so they ride only the create -- the existence check must not
        try to set throughput. The Python coordinator owns this compound
        workflow because the public Rust driver exposes the individual
        primitives, but not a database get-or-create primitive. Each primitive
        still runs through the selected backend, so Rust-backed clients do not
        invoke the legacy transport. Both legs share one eligibility answer
        (``is_read_database_rust_eligible``): a per-call option the Rust path
        cannot honor fails the whole call with a readable message instead of
        being silently dropped or routed through legacy Python halfway.
        ``response_hook`` is invoked once on success with the response headers
        and the resulting database. If creation conflicts with another caller,
        read the database once more. A failed follow-up read propagates without
        another creation attempt.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        # Strip provisioning options from the existence read so throughput is
        # applied only when the database is actually created.
        read_options = dict(request_options)
        read_options.pop("offerThroughput", None)
        read_options.pop("autoUpgradePolicy", None)
        # One definition of "Rust can honor this read", shared with
        # DatabaseProxy.read, so the same call never runs on Rust here and on
        # legacy Python there. Both legs use it: reaching the create means the
        # read already ran on Rust, and the workflow must not switch backends
        # halfway through.
        rust_eligible = is_read_database_rust_eligible(read_options, operation_kwargs)

        def read_database() -> CosmosDict:
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
                    options=read_options,
                    **operation_kwargs,
                ),
                process_response=lambda response: process_backend_response(
                    response,
                    client_connection=self._client_connection,
                ),
            )

        try:
            result = read_database()
        except exceptions.CosmosResourceNotFoundError:
            try:
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
                        options=request_options,
                        **operation_kwargs,
                    ),
                    process_response=lambda response: process_backend_response(
                        response,
                        client_connection=self._client_connection,
                    ),
                )
            except exceptions.CosmosResourceExistsError:
                result = read_database()
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
        return result
