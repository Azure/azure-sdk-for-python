# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Format a Cosmos request charge (RUs) the same way the wire string does.

The core-python backend reads ``x-ms-request-charge`` straight off the
HTTP response (already a string). The Rust backend exposes the charge
as a ``float``; this helper renders it back to a string so
``last_response_headers["x-ms-request-charge"]`` is byte-identical
across backends.
"""
from __future__ import annotations


def format_ru_charge(charge: float) -> str:
    """Render a request charge as the wire-string shape (``str(float)``).

    :param charge: The RU charge as a float (typically from the Rust
        backend's typed response struct).
    :type charge: float
    :returns: The wire-string representation, e.g. ``"1.0"``, ``"1.43"``.
    :rtype: str
    """
    return str(float(charge))
