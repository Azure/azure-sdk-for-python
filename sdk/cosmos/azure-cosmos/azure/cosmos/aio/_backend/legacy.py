# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Explicit core-python selection for remaining migration coordinators.

This stateless backend invokes the supplied plain callable without building or
executing a prepared request. Point parity uses the separate legacy item helper."""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.errors import BindingProtocolError

from typing import Awaitable, Any, Callable, Optional

from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON

from .cosmos_backend import AsyncCosmosBackend


class AsyncLegacyBackend(AsyncCosmosBackend):
    """Core-python async backend: awaits the legacy ``client_connection`` call.

    Stateless -- it only forwards to the legacy callable
    the async coordinator supplies -- so :data:`ASYNC_LEGACY_BACKEND` is shared by
    every core-python async client.
    """

    name = BACKEND_NAME_CORE_PYTHON

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Not supported: the legacy driver is not ``PreparedRequest``-driven.

        See :meth:`azure.cosmos._backend.legacy.LegacyBackend.execute`. Every
        async coordinator drives this backend through :meth:`run_operation` or
        :meth:`run_page_operation`, never a wire primitive; this exists only to
        satisfy the abstract base.
        """
        raise NotImplementedError(
            "AsyncLegacyBackend does not send prepared requests on the wire; the "
            "core-python path is driven by the original call arguments via "
            "run_operation, not execute()."
        )

    async def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Run the explicitly selected legacy callable without building a Rust request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return await legacy_call()

    async def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedQuery],
        process_response: Callable[[QueryPage], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Run the explicitly selected legacy callable without building a Rust request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return await legacy_call()


#: Process-wide shared core-python async backend. ``AsyncLegacyBackend`` holds no
#: per-client state, so one instance is enough.
ASYNC_LEGACY_BACKEND = AsyncLegacyBackend()
