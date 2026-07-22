# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The async database family coordinator: creates account-level databases.

Async twin of :mod:`azure.cosmos._helpers.database_helper`. The public method
``CosmosClient.create_database`` (async) gathers its arguments and calls
:meth:`AsyncDatabaseHelper.create_database`; this module runs the create through
the selected engine and hands back the created database.

A "database" is the top-level container-of-containers a customer makes once per
tenant or app. Creating one is an account-level write, so there is no container
and no partition key involved.

Why this module exists (public methods must not know which engine runs): the
public ``create_database`` coerces the client's backend selection to a concrete
backend (``coerce_async_backend`` -> the rust backend or the explicit async
``LegacyBackend``, never ``None``) and drives the create through
:meth:`~azure.cosmos.aio._backend.base.AsyncCosmosBackend.run_operation`, so the
public method names no engine. Without this module that branching would live in
the public ``create_database`` method.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from ..._backend.base import OP_CREATE_DATABASE, LegacyOperation
from ..._constants import _Constants as Constants
from ..._cosmos_responses import CosmosDict
from ..._helpers._request_prep import build_create_database_prepared
from ..._helpers._response_parse import parse_backend_response
from .._backend.base import AsyncCosmosBackend
from .._backend.legacy import coerce_async_backend


class AsyncDatabaseHelper:
    """Route async database operations through the selected backend boundary."""

    def __init__(self, client_connection: Any, backend: Optional[AsyncCosmosBackend]) -> None:
        self._client_connection = client_connection
        self._backend = coerce_async_backend(backend)

    async def create_database(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any]], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Async twin of :meth:`azure.cosmos._helpers.database_helper.DatabaseHelper.create_database`.

        Same engine-selection and ``read_timeout`` fallback behavior. One difference
        matches the async ``create_database`` contract: ``response_hook`` is invoked
        once on success with the response headers only, not the created database.
        """
        operation_kwargs = dict(kwargs or {})
        read_timeout = request_options.get(Constants.Kwargs.READ_TIMEOUT)
        if read_timeout is None:
            read_timeout = operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT)

        async def build_prepared():
            return build_create_database_prepared(
                database,
                request_options,
                kwargs=operation_kwargs,
            )

        result = await self._backend.run_operation(
            build_prepared=build_prepared,
            legacy_operation=LegacyOperation(
                op=OP_CREATE_DATABASE,
                invoke=lambda: self._client_connection.CreateDatabase(
                    database=database,
                    options=request_options,
                    **operation_kwargs,
                ),
            ),
            parse_response=lambda response: parse_backend_response(
                response,
                client_connection=self._client_connection,
            ),
            rust_eligible=read_timeout is None,
        )
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers)
        return result
