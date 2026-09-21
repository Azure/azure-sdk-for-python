# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Run supplied Python calls for operations still using migration wrappers.

This backend does not build or send Rust requests. Item operations using the
existing Python implementation are handled by the separate legacy item helper.
"""

from __future__ import annotations

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.errors import BindingProtocolError

from typing import Any, Callable, Optional

from .cosmos_backend import CosmosBackend
from .contracts import BackendResponse, PreparedQuery, PreparedRequest, QueryPage
from .constants import BACKEND_NAME_CORE_PYTHON


class LegacyBackend(CosmosBackend):
    """Core-python backend: runs the legacy ``client_connection`` call.

    Each caller supplies the function to run. No client settings or progress
    are stored here, so all core-python clients can share LEGACY_BACKEND.
    """

    name = BACKEND_NAME_CORE_PYTHON

    def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Reject prepared requests, which this backend does not send.

        Use run_operation or run_page_operation with a Python function that
        has the original call arguments. A PreparedRequest does not contain
        everything needed to reconstruct that call.
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
        """Run the supplied Python function without building a Rust request."""
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
        """Run the supplied Python page fetch without building a Rust request."""
        if legacy_call is None:
            raise BindingProtocolError(
                f"No legacy callable supplied for {routing.op!r}"
            )
        return legacy_call()


#: Process-wide shared core-python backend. ``LegacyBackend`` holds no per-client
#: state (the legacy call is supplied per operation), so one instance is enough.
LEGACY_BACKEND = LegacyBackend()
