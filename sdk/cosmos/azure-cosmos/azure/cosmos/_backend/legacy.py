# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The explicit core-python (legacy) backend for the single-item path.

``LegacyBackend`` makes the core-python engine a full
:class:`~azure.cosmos._backend.base.CosmosBackend` rather than the *absence* of a
backend. Representing core-python as ``None`` instead would make ``None`` mean two
things at once (no backend / run legacy) and force every coordinator to branch on
it. With an explicit backend, every family coordinator (``ItemHelper``,
``ThroughputHelper``, ``FeedRangeHelper``, ``DatabaseHelper``) always holds one
backend by interface and never interprets ``None``. Selecting rust gives a
:class:`~azure.cosmos._backend.rust.RustBackend`; selecting core-python (or
forcing legacy for a single call) gives this backend. The item family runs
through :meth:`~azure.cosmos._backend.base.CosmosBackend.run_operation`.

The legacy engine is **not** ``PreparedRequest``-driven: its work is the
original public call arguments (``document_link`` / ``options`` / body / kwargs),
which a wire-shaped ``PreparedRequest`` does not carry. So this backend does not
implement the wire primitive ``execute``; it runs the :class:`LegacyOperation`
the coordinator hands to ``run_operation``. ``LegacyOperation`` is a small, named,
typed request/context object (not a bare callable attached to
``PreparedRequest``) -- see its docstring in ``base`` for why a fully generic
reconstruction from wire-shaped fields is not safe here: the six legacy item
calls (``CreateItem`` / ``DeleteItem`` / ...) take differently-shaped positional
arguments that a ``PreparedRequest`` cannot carry losslessly, so the coordinator
still builds the concrete zero-arg call, and this backend just runs it by
``invoke()``. That object already closes over the connection and the per-call
arguments, so this backend holds no per-client state and a single shared
instance (:data:`LEGACY_BACKEND`) serves every core-python client.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from .base import BackendResponse, CosmosBackend, LegacyOperation, PreparedRequest
from .constants import BACKEND_NAME_CORE_PYTHON


class LegacyBackend(CosmosBackend):
    """Core-python backend: runs the legacy ``client_connection`` call.

    Stateless -- it only forwards to the :class:`~azure.cosmos._backend.base.LegacyOperation`
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
        through :meth:`run_operation`, never ``execute``; this method exists
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
        build_prepared: Callable[[], PreparedRequest],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
        allow_legacy_fallback: bool = True,
        unsupported_message: Optional[str] = None,
    ) -> Any:
        """Run the operation on the legacy core-python path.

        Always runs ``legacy_operation.invoke()`` and returns its already-parsed
        result; ``build_prepared`` / ``parse_response`` / ``rust_eligible`` are
        ignored because this backend never builds a wire request. Reading only
        ``legacy_operation`` (never ``build_prepared`` / ``rust_eligible``) is
        this backend's whole "always fall back to legacy" behavior -- no ``None``
        or backend-type check anywhere in this method.
        """
        return legacy_operation.invoke()


#: Process-wide shared core-python backend. ``LegacyBackend`` holds no per-client
#: state (the legacy call is supplied per operation), so one instance is enough.
LEGACY_BACKEND = LegacyBackend()


def coerce_backend(backend: Optional[CosmosBackend]) -> CosmosBackend:
    """Map a family coordinator's backend selection to a never-``None`` backend.

    The stored client selection (``client_connection._backend``) is still
    ``Optional``: ``None`` for core-python, a :class:`RustBackend` for rust. That
    ``Optional`` contract is what ``pick_backend`` returns, so it is preserved at
    the client-connection boundary. Every family coordinator (``DatabaseHelper``,
    ``ItemHelper``, ``ThroughputHelper``, and ``FeedRangeHelper``), however,
    holds one backend by interface, so it coerces the selection here at its own
    boundary -- ``None`` (or an already-chosen legacy backend) becomes
    :data:`LEGACY_BACKEND`, a rust backend passes through unchanged. This is the
    single place a coordinator bridges the legacy ``Optional`` selection to the
    explicit backend it then holds for the rest of its lifetime.

    :param backend: The selected backend, or ``None`` for core-python.
    :returns: A concrete backend (never ``None``).
    :rtype: ~azure.cosmos._backend.base.CosmosBackend
    """
    if backend is None:
        return LEGACY_BACKEND
    return backend
