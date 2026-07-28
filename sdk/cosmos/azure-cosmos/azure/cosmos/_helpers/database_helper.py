# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-neutral coordination for account-level database operations.

This is the database counterpart to
:class:`~azure.cosmos._helpers.item_helper.ItemHelper`. The public method
``CosmosClient.create_database`` and ``create_database_if_not_exists`` gather
their arguments and delegate here. This module runs each operation through the
selected engine and returns the final database properties.

What a "database" is, in customer terms: the top-level container-of-containers a
customer makes once per tenant or app. Creating one is an account-level write, so
unlike an item write there is no container and no partition key involved.

Why this module exists (public methods must not know which engine runs):
without it, that engine branching would live in the public client methods. Here
it coerces the client's backend selection to a concrete backend
(``coerce_backend`` -> the rust backend or the explicit ``LegacyBackend``, never
``None``) and drives the create through
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the public
method is a thin delegate that names no engine. This mirrors ``ItemHelper`` and
the throughput and feed-range coordinators.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from .. import exceptions
from .._backend.base import (
    CosmosBackend,
    LegacyOperation,
    OP_CREATE_DATABASE,
    OP_READ_DATABASE,
)
from .._backend.legacy import coerce_backend
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._helpers._request_prep import (
    build_create_database_prepared,
    build_read_database_prepared,
)
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
        operation_kwargs.pop("response_hook", None)
        read_timeout = request_options.get(Constants.Kwargs.READ_TIMEOUT)
        if read_timeout is None:
            read_timeout = operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT)
        result = self._backend.run_operation(
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
            ),
            rust_eligible=read_timeout is None,
        )
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
        return result

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
        invoke the legacy transport. A per-call ``read_timeout`` is rejected on
        Rust because that socket-level option is not representable there; it is
        not silently dropped or routed through legacy Python.
        ``response_hook`` is invoked once on success with the response headers
        and the resulting database.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        # Strip provisioning options from the existence read so throughput is
        # applied only when the database is actually created.
        read_options = dict(request_options)
        read_options.pop("offerThroughput", None)
        read_options.pop("autoUpgradePolicy", None)
        database_link = "dbs/{}".format(database["id"])
        read_timeout = request_options.get(Constants.Kwargs.READ_TIMEOUT)
        if read_timeout is None:
            read_timeout = operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT)
        rust_eligible = read_timeout is None

        try:
            result = self._backend.run_operation(
                build_prepared=lambda: build_read_database_prepared(
                    database,
                    read_options,
                    kwargs=operation_kwargs,
                ),
                legacy_operation=LegacyOperation(
                    op=OP_READ_DATABASE,
                    invoke=lambda: self._client_connection.ReadDatabase(
                        database_link,
                        options=read_options,
                        **operation_kwargs,
                    ),
                ),
                parse_response=lambda response: parse_backend_response(
                    response,
                    client_connection=self._client_connection,
                ),
                rust_eligible=rust_eligible,
                allow_legacy_fallback=False,
                unsupported_message=(
                    "create_database_if_not_exists with a per-call read_timeout "
                    "is not supported on the Rust backend"
                ),
            )
        except exceptions.CosmosResourceNotFoundError:
            result = self._backend.run_operation(
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
                ),
            )
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
        return result
