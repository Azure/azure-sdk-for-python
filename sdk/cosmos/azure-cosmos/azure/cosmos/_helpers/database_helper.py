# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-neutral coordination for account-level database operations.

This is the database counterpart to
:class:`~azure.cosmos._helpers.item_helper.ItemHelper`. The public methods
``CosmosClient.create_database``, ``CosmosClient.create_database_if_not_exists``
and ``DatabaseProxy.read`` gather their arguments and delegate here. This module
runs each operation through the selected engine and returns the final database
properties.

What a "database" is, in customer terms: the top-level container-of-containers a
customer makes once per tenant or app. Creating one is an account-level write, so
unlike an item write there is no container and no partition key involved.

Why this module exists (public methods must not know which engine runs):
without it, that engine branching would live in the public client methods. Here
it uses the concrete backend stored by the client and drives the create through
:meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`, so the public
method is a thin delegate that names no engine. This mirrors ``ItemHelper`` and
the throughput and feed-range coordinators.

The whole of ``DatabaseProxy.read`` on the rust path, end to end
-----------------------------------------------------------------
A customer calls ``db.read()``. Five pieces were added or changed to let that
call run on the rust engine, and each one exists because something concrete
breaks without it:

1. ``DatabaseProxy.read`` (``database.py``) collects the caller's keyword
   arguments and hands them here. It names no engine.
2. :meth:`DatabaseHelper.read_database` (this module) asks
   ``is_read_database_rust_eligible`` one question -- can the rust engine honor
   everything this caller asked for? -- and hands both the rust request and the
   core-python call to ``run_operation``, which runs exactly one of them.
   Without this step the choice would be made twice, in slightly different
   ways, in two different public methods.
3. ``build_read_database_prepared`` (``_request_database``) turns the caller's
   options into the request the binding reads. Without it there was no rust
   request to send, so a database read had no rust path at all.
4. ``base.resolve_initial_headers`` layers a caller's ``initial_headers`` over
   the client's defaults on the core-python path. Without it those headers are
   dropped and never reach the service.
5. ``read_database`` in the binding (``documents/databases.rs``) unpacks that
   request and calls the driver.

What would have happened without all of this: a customer who built a rust-backed
client would still have had ``db.read()`` quietly run on the older python
transport. Same result, but different retry behavior and different diagnostics
from every other call on the same client -- which is the kind of difference that
only shows up during an incident.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from .. import exceptions
from .._backend.base import CosmosBackend
from .._backend.contracts import LegacyOperation
from .._backend.operations import OP_CREATE_DATABASE, OP_DELETE_DATABASE, OP_READ_DATABASE
from .._constants import _Constants as Constants
from .._cosmos_responses import CosmosDict
from .._helpers._request_database import (
    RUST_GET_OR_CREATE_DATABASE_UNSUPPORTED_MESSAGE,
    build_create_database_prepared,
    build_delete_database_prepared,
    build_read_database_prepared,
    is_delete_database_rust_eligible,
    is_read_database_rust_eligible,
)
from .._helpers._response_parse import parse_backend_response


class DatabaseHelper:
    """Route database operations through the selected backend boundary."""

    def __init__(self, client_connection: Any, backend: CosmosBackend) -> None:
        """Store the client connection and selected implementation."""
        self._client_connection = client_connection
        self._backend = backend

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
        backend. ``create_database`` does not support a per-call ``read_timeout``;
        callers configure the read timeout when constructing ``CosmosClient``.
        ``response_hook`` is invoked once on success with the response headers and
        the created database.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if (
            request_options.get(Constants.Kwargs.READ_TIMEOUT) is not None
            or operation_kwargs.get(Constants.Kwargs.READ_TIMEOUT) is not None
        ):
            raise TypeError("create_database() does not support the 'read_timeout' keyword argument")
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

    def read_database(
        self,
        database_id: Any,
        request_options: Mapping[str, Any],
        *,
        response_hook: Optional[Callable[[Mapping[str, Any], CosmosDict], None]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
    ) -> CosmosDict:
        """Read one database's properties, without exposing engine selection.

        Backs ``DatabaseProxy.read``. The read runs on Rust when Rust can honor
        every per-call option (``is_read_database_rust_eligible``) and on the
        legacy path otherwise, so an option the Rust path would drop -- a
        socket-level ``read_timeout``, a sub-second ``timeout`` -- is still
        honored rather than silently ignored. ``response_hook`` is invoked once
        on success with the response headers and the database properties.

        Without this method the same choice would be written out by hand in
        ``DatabaseProxy.read`` and again in the existence check inside
        ``create_database_if_not_exists``, and the two copies would drift: the
        same call would run on one engine in one method and the other engine in
        the other, honoring a different set of the caller's options each time.
        """
        operation_kwargs = dict(kwargs or {})
        operation_kwargs.pop("response_hook", None)
        if response_hook is not None:
            operation_kwargs["response_hook"] = response_hook
        result = self._backend.run_operation(
            build_prepared=lambda: build_read_database_prepared(
                database_id,
                request_options,
                kwargs=operation_kwargs,
            ),
            legacy_operation=LegacyOperation(
                op=OP_READ_DATABASE,
                invoke=lambda: self._client_connection.ReadDatabase(
                    "dbs/{}".format(database_id),
                    options=request_options,
                    **operation_kwargs,
                ),
            ),
            parse_response=lambda response: parse_backend_response(
                response,
                client_connection=self._client_connection,
                response_hook=response_hook,
            ),
            rust_eligible=is_read_database_rust_eligible(
                request_options,
                operation_kwargs,
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
            build_prepared=lambda: build_delete_database_prepared(
                database_link,
                request_options,
                kwargs=operation_kwargs,
            ),
            legacy_operation=LegacyOperation(
                op=OP_DELETE_DATABASE,
                invoke=lambda: self._client_connection.DeleteDatabase(
                    database_link,
                    options=request_options,
                    **operation_kwargs,
                ),
            ),
            parse_response=lambda response: parse_backend_response(
                response,
                client_connection=self._client_connection,
            ),
            rust_eligible=is_delete_database_rust_eligible(
                request_options,
                operation_kwargs,
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
        and the resulting database.
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
        # read already ran on Rust, and the workflow must not switch engines
        # halfway through.
        rust_eligible = is_read_database_rust_eligible(read_options, operation_kwargs)

        try:
            result = self._backend.run_operation(
                build_prepared=lambda: build_read_database_prepared(
                    database["id"],
                    read_options,
                    kwargs=operation_kwargs,
                ),
                legacy_operation=LegacyOperation(
                    op=OP_READ_DATABASE,
                    invoke=lambda: self._client_connection.ReadDatabase(
                        "dbs/{}".format(database["id"]),
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
                unsupported_message=RUST_GET_OR_CREATE_DATABASE_UNSUPPORTED_MESSAGE,
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
                rust_eligible=rust_eligible,
                allow_legacy_fallback=False,
                unsupported_message=RUST_GET_OR_CREATE_DATABASE_UNSUPPORTED_MESSAGE,
            )
        if response_hook is not None:
            response_hook(self._client_connection.last_response_headers, result)
        return result
