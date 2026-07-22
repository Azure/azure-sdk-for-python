# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The database family coordinator: creates account-level databases.

This is the database counterpart to
:class:`~azure.cosmos._helpers.item_helper.ItemHelper`. The public method
``CosmosClient.create_database`` gathers its arguments and calls
:meth:`DatabaseHelper.create_database`; this module runs the create through the
selected engine and hands back the created database.

What a "database" is, in customer terms: the top-level container-of-containers a
customer makes once per tenant or app. Creating one is an account-level write, so
unlike an item write there is no container and no partition key involved.

Why this module exists (public methods must not know which engine runs):
before this, ``CosmosClient.create_database`` called the legacy client directly.
Here it coerces the client's backend selection to a concrete backend
(``coerce_backend`` -> the rust backend or the explicit ``LegacyBackend``, never
``None``) and drives the create through
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the public
method is a thin delegate that names no engine. This mirrors ``ItemHelper`` and
the throughput and feed-range coordinators. Without this module that engine
branching would live in the public ``create_database`` method.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from .._backend.base import CosmosBackend, LegacyOperation, OP_CREATE_DATABASE
from .._backend.legacy import coerce_backend
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._helpers._request_prep import build_create_database_prepared
from .._helpers._response_parse import parse_backend_response


class DatabaseHelper:
    """Route database operations through the selected backend boundary."""

    def __init__(self, client_connection: Any, backend: Optional[CosmosBackend]) -> None:
        self._client_connection = client_connection
        self._backend = coerce_backend(backend)

    def create_database(
        self,
        database: dict[str, Any],
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Create one database, without exposing engine selection to the public method.

        Builds the account-level create request and drives it through the selected
        backend. If the caller set a per-call ``read_timeout`` (a socket-level
        timeout the rust path can't honor yet), the create runs on the legacy path,
        which does honor it -- so a customer's ``read_timeout`` is never silently
        dropped. ``response_hook`` is invoked once on success with the response
        headers and the created database.
        """
        operation_kwargs = dict(kwargs or {})
        read_timeout = request_options.get(Constants.Kwargs.READ_TIMEOUT)
        if read_timeout is None:
            read_timeout = operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT)
        return self._backend.run_operation(
            build_prepared=lambda: build_create_database_prepared(
                database,
                request_options,
                kwargs=operation_kwargs,
            ),
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
                response_hook=response_hook,
            ),
            rust_eligible=read_timeout is None,
        )
