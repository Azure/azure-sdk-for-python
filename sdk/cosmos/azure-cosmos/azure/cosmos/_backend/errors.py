# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Errors raised by the backend layer, and the guards that raise them.

These types separate the three ways a backend can decline to produce a normal
reply, which would otherwise be indistinguishable to the caller:

* :class:`PageNotSupportedByBackendError` and its query-specific subclass mean
  "this backend cannot run this operation, hand it to legacy". That is a routing
  signal, not a failure.
* :class:`BackendProtocolError` means a backend broke its own reply-shape
  contract. That is a bug on our side, so it is never retried and never falls
  back.
* :func:`raise_account_read_unsupported` refuses a client-level call the Rust
  path does not implement yet, instead of letting it quietly borrow the
  core-python connection.
"""
from __future__ import annotations

from typing import Any


class PageNotSupportedByBackendError(RuntimeError):
    """Raised before dispatch when a backend cannot execute a paged operation.

    The signal that means "hand this page to legacy instead", as opposed to a
    real failure. Without a distinct type, a backend refusing a page and a
    backend hitting a genuine error would look the same, and one of the two
    would be handled wrongly.
    """


class QueryNotSupportedByBackendError(PageNotSupportedByBackendError):
    """Raised when the selected backend cannot execute a planned query."""


class BackendProtocolError(RuntimeError):
    """Raised when a backend violates the reply-shape contract.

    A bug on our side, not a customer error, so it is never retried or fallen
    back from. Without it a malformed reply would be silently retried on the
    legacy path and the underlying defect would go unnoticed.
    """


# ---------------------------------------------------------------------------
# Client-level operations the Rust path does not implement yet
# ---------------------------------------------------------------------------
#
# A few public methods are *client-level* (not per-item), so they are not routed
# through the backend's ``execute`` dispatch the way point operations are. On a
# Rust-backed client they would otherwise fall straight through to the legacy
# core-python connection. The migration goal is for the Rust path to stand on its
# own, so rather than quietly borrowing core-python we raise.
# ``get_database_account`` is the one such method today.


def raise_account_read_unsupported(backend: Any) -> None:
    """Raise ``NotImplementedError`` for ``get_database_account`` on a Rust-backed
    client; do nothing on the core-python selection.

    :param backend: The client's chosen backend, or ``None`` for core-python.
        A non-``None`` backend means the Rust path is active, and this call has no
        Rust-path implementation yet, so it raises instead of falling back to the
        legacy connection. ``None`` is a no-op, so core-python keeps working unchanged.
    """
    if backend is None:
        return
    raise NotImplementedError(
        "get_database_account() is not yet available on the Rust backend "
        "(_backend='rust'). The rust driver reads account metadata internally for "
        "routing but does not yet expose it across the binding."
    )
