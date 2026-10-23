# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep asynchronous legacy-path calls available while migration is unfinished.

AsyncLegacyBackend awaits the supplied legacy-path function without building
a prepared request or calling the binding. It holds no per-client resources.
Legacy item operations use a separate helper.
"""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.errors import BindingProtocolError

from typing import Awaitable, Any, Callable, Optional

from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON

from .cosmos_backend import AsyncCosmosBackend


class AsyncLegacyBackend(AsyncCosmosBackend):
    """Await a legacy-path connection call using its original Python arguments.

    The function supplied by the caller retains its own inputs and connection.
    This object holds no per-client state, so ASYNC_LEGACY_BACKEND can be shared.
    That ownership property is unrelated to stateless paging.
    """

    name = BACKEND_NAME_CORE_PYTHON

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Reject prepared requests, which the legacy path does not consume.

        Use run_operation or run_page_operation with a legacy-path function
        that already has the original call arguments.
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
        """Await the selected legacy-path function without building a prepared request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return await legacy_call()

    async def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedPageRequest],
        process_response: Callable[[BackendPage], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Await the legacy-path page function without building a prepared page request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return await legacy_call()


#: Shared Python backend for asynchronous legacy-path calls. ``AsyncLegacyBackend`` holds no
#: per-client state, so one instance is enough.
ASYNC_LEGACY_BACKEND = AsyncLegacyBackend()
