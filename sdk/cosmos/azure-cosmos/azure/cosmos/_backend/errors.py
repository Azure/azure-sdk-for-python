# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Report Python wrapper and Python/Rust binding failures without replaying work.

Some migration checks still permit fallback to the legacy path before execution.
This is not a second supported release execution path. A failure after execution
starts must reach the caller without repeating the operation through the legacy
path. Separate exception types keep those cases distinct.
"""
from __future__ import annotations

from typing import Any

from .constants import is_rust_backend


class PagePreflightError(RuntimeError):
    """Report that page preflight cannot find the required binding function.

    The Python wrapper may choose the legacy path only when this error comes from its
    check before execution and the operation allows fallback. The same error
    raised during execution or response processing does not allow a retry.
    """


class UnsupportedQueryError(RuntimeError):
    """Report an unsupported Rust driver query, not permission for legacy fallback."""


class BindingProtocolError(RuntimeError):
    """Report unexpected Python wrapper request data or binding results.

    For example, a prepared operation may not match the requested operation,
    or the binding may return no page. Report the mismatch rather than hiding
    it by repeating the operation through the legacy path.
    """


def raise_account_read_unsupported(backend: Any) -> None:
    """Reject get_database_account on the Rust path instead of silently falling back.

    The binding has no function for this public account read. The retained
    legacy test branch can still perform it, so this check returns without
    raising for that branch. This is not a customer-facing execution-path choice.
    """
    if not is_rust_backend(backend):
        return
    raise NotImplementedError(
        "get_database_account() is not yet available through the Rust binding. "
        "The rust driver reads account metadata internally for "
        "routing but does not yet expose it across the binding."
    )
