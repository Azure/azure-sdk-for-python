# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Report Python wrapper and Python/Rust binding failures without replaying work.

Unsupported requests and missing binding functions fail before execution.
Failures during execution or response processing also reach the caller.
Neither case permits fallback to legacy Python.
"""
from __future__ import annotations

UNSUPPORTED_AGGREGATE_QUERY_MESSAGE = (
    "This aggregate query is not supported by this SDK for the requested query scope."
)


class PagePreflightError(RuntimeError):
    """Report that page preflight cannot find the required binding function.

    The Python wrapper propagates this error without choosing the legacy path,
    whether it occurs before execution, during execution, or during processing.
    """


class UnsupportedQueryError(RuntimeError):
    """Report an unsupported Rust driver query, not permission for legacy fallback."""


class BindingProtocolError(RuntimeError):
    """Report unexpected Python wrapper request data or binding results.

    For example, a prepared operation may not match the requested operation,
    or the binding may return no page. Report the mismatch rather than hiding
    it by repeating the operation through the legacy path.
    """
