# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Format a Cosmos request charge (RUs) the same way the server's wire string does.

The Cosmos service returns the request charge for every operation in
the ``x-ms-request-charge`` HTTP response header. On the wire it is a
text value such as ``"1.0"``, ``"1.43"``, ``"6.29"``. Customer
dashboards, log queries, and tests routinely string-compare or grep
that text to track RU spend.

The two backends produce the charge differently:

* The core-python backend reads the header straight off an
  ``HttpResponse`` and gets the original wire string back unchanged.
  No formatting needed.
* The Rust backend's typed response struct surfaces the charge as a
  ``f64`` (a parsed float). To keep ``last_response_headers
  ["x-ms-request-charge"]`` byte-identical between backends, the
  helper has to render the float back to a string the same way the
  server would have.

This module is the one place that formatting lives. Today it produces
a single deterministic shape (``str(float)``-style, e.g. ``"1.0"``,
``"1.43"``). When we run pre-GA parity comparisons against real
service responses we may discover the server uses a fixed precision
(``"1.00"`` vs ``"1.0"`` vs ``"1"``) for some operations; the test
suite for this module is the one place to update if that happens.
"""
from __future__ import annotations


def format_ru_charge(charge: float) -> str:
    """Render a request charge into the wire-string shape.

    :param charge: The RU charge as a float, typically supplied by the
        Rust backend's typed response struct. Negative values are
        not produced by Cosmos but are passed through if given so the
        helper does not raise on unexpected inputs (the test suite
        pins a negative input as a regression check).
    :type charge: float
    :returns: The canonical wire-string representation of ``charge``.
    :rtype: str
    """
    # ``str(float)`` is intentional, not ``repr`` and not f-string with
    # an explicit precision. Python's ``str(1.0)`` returns ``"1.0"``,
    # which matches what the Cosmos service returns for the most
    # common case (whole-RU operations like a small create_item).
    # If we discover the server uses a fixed-precision form for some
    # operations we will update the format here and add a test row;
    # locking the format in this single module is the whole point.
    return str(float(charge))
