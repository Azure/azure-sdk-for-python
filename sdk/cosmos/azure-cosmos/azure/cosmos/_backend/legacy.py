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

from typing import Any, Callable, Optional

from .cosmos_backend import CosmosBackend
from .contracts import BackendResponse, PreparedQuery, PreparedRequest, QueryPage
from .constants import BACKEND_NAME_CORE_PYTHON


class LegacyBackend(CosmosBackend):
    """Core-python backend: runs the legacy ``client_connection`` call.

    Stateless -- it only forwards to the legacy callable
    the coordinator supplies -- so :data:`LEGACY_BACKEND` is shared by every
    core-python client instead of one instance per client.
    """

    name = BACKEND_NAME_CORE_PYTHON

    def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Not supported: the legacy backend is not ``PreparedRequest``-driven.

        ``execute`` is the rust wire primitive (send a prepared request, return
        the raw reply). The legacy path reconstructs its call from the original
        public arguments, which a ``PreparedRequest`` does not carry, so there is
        nothing meaningful to do here. Every coordinator drives this backend
        through :meth:`run_operation` or :meth:`run_page_operation`, never
        a wire primitive; this method exists
        only to satisfy the abstract base and guards against a wrong call site.
        """
        raise NotImplementedError(
            "LegacyBackend does not send prepared requests on the wire; the "
            "core-python path is driven by the original call arguments via "
            "run_operation, not execute()."
        )

    def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Any]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Run the explicitly selected legacy callable without building a Rust request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return legacy_call()

    def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedQuery],
        process_response: Callable[[QueryPage], Any],
        legacy_call: Optional[Callable[[], Any]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Run the explicitly selected legacy callable without building a Rust request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return legacy_call()


#: Process-wide shared core-python backend. ``LegacyBackend`` holds no per-client
#: state (the legacy call is supplied per operation), so one instance is enough.
LEGACY_BACKEND = LegacyBackend()
