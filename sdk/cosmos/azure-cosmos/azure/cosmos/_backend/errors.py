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
