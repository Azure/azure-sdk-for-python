# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The explicit core-python (legacy) backend for the async single-item path.

Async twin of :mod:`azure.cosmos._backend.legacy`. See that module for the full
rationale: the core-python engine is a first-class
:class:`~azure.cosmos.aio._backend.base.AsyncCosmosBackend` so every async
family coordinator always holds one backend by interface and never interprets
``None`` from selection or ``execute``.

Like the sync backend, the legacy engine is not ``PreparedRequest``-driven, so
this backend does not implement the wire primitive ``execute``; it awaits the
:class:`~azure.cosmos._backend.base.LegacyOperation` the coordinator hands to
``run_operation``. That typed port already closes over the connection and the
per-call arguments, so this backend holds no per-client state and a single
shared instance (:data:`ASYNC_LEGACY_BACKEND`) serves every core-python async
client.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from azure.cosmos._backend.base import LegacyOperation, PreparedQuery, QueryPage
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest


class AsyncLegacyBackend(AsyncCosmosBackend):
    """Core-python async backend: awaits the legacy ``client_connection`` call.

    Stateless -- it only forwards to the :class:`~azure.cosmos._backend.base.LegacyOperation`
    the async coordinator supplies -- so :data:`ASYNC_LEGACY_BACKEND` is shared by
    every core-python async client.
    """

    name = BACKEND_NAME_CORE_PYTHON

    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Not supported: the legacy engine is not ``PreparedRequest``-driven.

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
        build_prepared: Callable[[], Any],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
        allow_legacy_fallback: bool = True,
        unsupported_message: Optional[str] = None,
    ) -> Any:
        """Run the operation on the legacy core-python path.

        Always awaits ``legacy_operation.invoke()`` and returns its
        already-parsed result; ``build_prepared`` / ``parse_response`` /
        ``rust_eligible`` are ignored because this backend never builds a wire
        request.
        """
        return await legacy_operation.invoke()

    async def run_page_operation(  # pylint: disable=too-many-arguments
        self,
        *,
        build_prepared: Callable[[], Awaitable[PreparedQuery]],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[QueryPage], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
    ) -> Any:
        """Run the paged operation on the legacy core-python path.

        Mirrors :meth:`run_operation` for feeds: ``build_prepared`` /
        ``parse_response`` / ``rust_eligible`` / ``fallback_exceptions`` are
        ignored because this backend never builds a wire request, so
        ``execute_pages`` is never reached.
        """
        return await legacy_operation.invoke()


#: Process-wide shared core-python async backend. ``AsyncLegacyBackend`` holds no
#: per-client state, so one instance is enough.
ASYNC_LEGACY_BACKEND = AsyncLegacyBackend()


def coerce_async_backend(
    backend: Optional[AsyncCosmosBackend],
) -> AsyncCosmosBackend:
    """Map an async family coordinator's backend selection to a never-``None`` backend.

    Async twin of :func:`azure.cosmos._backend.legacy.coerce_backend`:
    ``None`` (core-python) or an already-chosen legacy backend becomes
    :data:`ASYNC_LEGACY_BACKEND`; a rust backend passes through unchanged. The
    stored ``client_connection._backend`` stays ``Optional`` for ``pick_backend``;
    this is the single boundary where a coordinator coerces it. Current
    coordinators include ``AsyncDatabaseHelper``, ``AsyncItemHelper``,
    ``AsyncThroughputHelper``, and ``AsyncFeedRangeHelper``.

    :param backend: The selected async backend, or ``None`` for core-python.
    :returns: A concrete async backend (never ``None``).
    :rtype: ~azure.cosmos.aio._backend.base.AsyncCosmosBackend
    """
    if backend is None:
        return ASYNC_LEGACY_BACKEND
    return backend
