# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async backend-neutral coordination for account-level database operations.

Async twin of :mod:`azure.cosmos._helpers.database_helper`, which carries the
end-to-end walk-through of what ``DatabaseProxy.read`` does on the rust path and
what breaks without each piece. The async ``create_database``,
``create_database_if_not_exists`` and ``DatabaseProxy.read`` methods delegate
here. This module runs each operation through the selected backend and returns the
final database properties.

A "database" is the top-level container-of-containers a customer makes once per
tenant or app. Creating one is an account-level write, so there is no container
and no partition key involved.

Why this module exists (public methods must not know which backend runs): the
public methods use the concrete backend stored by the client and drive the create through
:meth:`~azure.cosmos.aio._backend.cosmos_backend.AsyncCosmosBackend.run_operation`, so a
public method names no backend. Without this module that branching would live in
the public methods.

One thing is genuinely different here, not just ``async``/``await``: the async
``run_operation`` awaits the request builder, so each operation wraps its builder
in a small ``async def`` instead of passing a lambda. Everything else follows the
sync module line for line, on purpose -- the two paths must not answer the same
question differently.
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
from ..._helpers._request_database import (
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    is_delete_database_rust_eligible,
    is_read_database_rust_eligible,
)
from ..._helpers._response_parse import (
    process_backend_response,
    process_database_read_response,
    with_response_header_snapshot,
)
from .._backend.cosmos_backend import AsyncCosmosBackend


class AsyncDatabaseHelper:
    """Route async database operations through the selected backend boundary."""

    def __init__(self, client_connection: Any, backend: AsyncCosmosBackend) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = backend

    async def create_database(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Async twin of :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.create_database`.

        Per-call ``read_timeout`` is not supported; callers configure the read
        timeout when constructing ``CosmosClient``. ``response_hook`` is invoked
        once on success with the response headers and created database, matching
        the legacy async connection contract.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if (
            request_options.get(Constants.Kwargs.READ_TIMEOUT) is not None
            or operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None
        ):
            raise TypeError(
                "create_database() does not support the 'read_timeout' keyword argument"
            )

        def build_request() -> PreparedRequest:
            return build_create_database_prepared(
                database,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_request=build_request,
            routing=OperationRouting(OP_CREATE_DATABASE, True),
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
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
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
    ) -> CosmosDict:
        """Async twin of
        :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.create_database_if_not_exists`.

        Same retry-safe behavior: read the named database first and create it
        only when the read returns "not found" (404), so re-running setup for a
        name that already exists returns that database instead of failing. Same
        stripping of provisioning options from the read. The Python
        coordinator owns this compound workflow because the public Rust driver
        exposes the individual primitives, but not a database get-or-create
        primitive. Each primitive still runs through the selected backend, so
        Rust-backed clients do not invoke the legacy transport. Both legs share
        one eligibility answer (``is_read_database_rust_eligible``): a per-call
        option the Rust path cannot honor fails the whole call with a readable
        message instead of being silently dropped or routed through legacy
        Python halfway. ``response_hook`` fires once on success. If creation
        conflicts with another caller, read the database once more. A failed
        follow-up read propagates without another creation attempt.
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

        def build_read_prepared() -> PreparedRequest:
            return build_read_database_prepared(
                database["id"],
                read_options,
                kwargs=operation_kwargs,
            )

        async def read_database() -> CosmosDict:
            return await self._backend.run_operation(
                build_request=build_read_prepared,
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
            result = await read_database()
        except exceptions.CosmosResourceNotFoundError:

            def build_create_prepared() -> PreparedRequest:
                return build_create_database_prepared(
                    database,
                    request_options,
                    kwargs=operation_kwargs,
                )

            try:
                result = await self._backend.run_operation(
                    build_request=build_create_prepared,
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
                result = await read_database()
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
        return result
