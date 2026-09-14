# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The explicit core-python backend for migration coordinators.

This stateless backend runs the ``LegacyOperation`` supplied by families still
using migration dispatch. It does not execute wire-shaped prepared requests.
The shared ``LEGACY_BACKEND`` also identifies explicit core-python selection.

Point operations select ``LegacyItemHelper`` separately for parity; their Rust
``ItemHelper`` has no legacy operation or fallback port. The item adapter retains
the original Python method signatures rather than reconstructing legacy calls
from a ``PreparedRequest``. Other families' migration dispatch is unchanged.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from .cosmos_backend import CosmosBackend
from .contracts import BackendResponse, LegacyOperation, PreparedQuery, PreparedRequest, QueryPage
from .constants import BACKEND_NAME_CORE_PYTHON


class LegacyBackend(CosmosBackend):
    """Core-python backend: runs the legacy ``client_connection`` call.

    Stateless -- it only forwards to the :class:`~azure.cosmos._backend.cosmos_backend.LegacyOperation`
    the coordinator supplies -- so :data:`LEGACY_BACKEND` is shared by every
    core-python client instead of one instance per client.
    """

    name = BACKEND_NAME_CORE_PYTHON

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Not supported: the legacy engine is not ``PreparedRequest``-driven.

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
        prepare_request: Callable[[], PreparedRequest],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
        allow_legacy_fallback: bool = True,
        unsupported_message: Optional[str] = None,
    ) -> Any:
        """Run the operation on the legacy core-python path.

        Always runs ``legacy_operation.invoke()`` and returns its already-parsed
        result; ``prepare_request`` / ``parse_response`` / ``rust_eligible`` are
        ignored because this backend never builds a wire request. Reading only
        ``legacy_operation`` (never ``prepare_request`` / ``rust_eligible``) is
        this backend's whole "always fall back to legacy" behavior -- no ``None``
        or backend-type check anywhere in this method.
        """
        return legacy_operation.invoke()

    def run_page_operation(  # pylint: disable=too-many-arguments
        self,
        *,
        prepare_request: Callable[[], PreparedQuery],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[QueryPage], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
        allow_legacy_fallback: bool = True,
        unsupported_message: Optional[str] = None,
    ) -> Any:
        """Run the paged operation on the legacy core-python path.

        Mirrors :meth:`run_operation` for feeds: ``prepare_request`` /
        ``parse_response`` / ``rust_eligible`` / ``fallback_exceptions`` are
        ignored because this backend never builds a wire request, so
        ``execute_pages`` is never reached.
        """
        return legacy_operation.invoke()


#: Process-wide shared core-python backend. ``LegacyBackend`` holds no per-client
#: state (the legacy call is supplied per operation), so one instance is enough.
LEGACY_BACKEND = LegacyBackend()
