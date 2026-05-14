# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Public diagnostics types for the hedging detection API.

This module exposes :class:`RequestedRegion` and :class:`RequestedRegionReason`,
the value types returned by the per-response / per-exception accessors
``is_hedging_started()``, ``get_requested_regions()`` and ``get_responded_regions()``.

``RequestedRegionReason`` is a *non-exhaustive* enumeration: future SDK versions
may emit reasons unknown to older client code. ``RequestedRegionReason._missing_``
returns :attr:`RequestedRegionReason.UNKNOWN` rather than raising
:class:`ValueError`, preserving forward compatibility for callers that pattern
match on enum members.
"""
from dataclasses import dataclass
from enum import Enum


class RequestedRegionReason(Enum):
    """Reason a region appears in :meth:`get_requested_regions`.

    This enum is **non-exhaustive**. Callers must handle the
    :attr:`UNKNOWN` value defensively, and treat any unrecognized value as
    :attr:`UNKNOWN` (``_missing_`` ensures forward compatibility — calling
    ``RequestedRegionReason("future_value_42")`` returns :attr:`UNKNOWN`
    rather than raising :class:`ValueError`).

    Some members are reserved for parity with other Azure Cosmos SDKs and are
    not populated by the Python SDK today:

    * :attr:`TRANSPORT_RETRY` — the Python azure-core transport retry layer is
      invisible to the Cosmos SDK; reserved but never appended.
    * :attr:`CIRCUIT_BREAKER_PROBE` — Python's per-partition circuit breaker
      performs *region exclusion*, not synthetic probe dispatches; re-elected
      regions are tagged as the reason that naturally applied
      (``INITIAL`` / ``OPERATION_RETRY``).
    """

    INITIAL = "initial"
    """Initial dispatch of the operation, before any retry or hedge fan-out."""

    OPERATION_RETRY = "operation_retry"
    """SDK-level retry policy (gone / throttle / session / service-unavailable)
    decided to retry to the **same** region."""

    TRANSPORT_RETRY = "transport_retry"
    """Reserved for parity with other Cosmos SDKs; not populated by the Python
    SDK today (the azure-core transport retry layer is invisible from the
    Cosmos layer)."""

    HEDGING = "hedging"
    """A cross-region hedge arm dispatched this region after the configured
    threshold delay elapsed without the primary winning."""

    REGION_FAILOVER = "region_failover"
    """SDK-level retry policy (timeout failover / endpoint discovery) switched
    the request to a different region."""

    CIRCUIT_BREAKER_PROBE = "circuit_breaker_probe"
    """Reserved for parity with other Cosmos SDKs; not populated by the Python
    SDK today (Python's circuit breaker performs region exclusion, not synthetic
    probe dispatches)."""

    UNKNOWN = "unknown"
    """An unrecognized reason value, including any future reason added in a
    later SDK version. :meth:`_missing_` maps unknown raw values to this
    member to keep deserialization / pattern-matching code forward-compatible.
    """

    @classmethod
    def _missing_(cls, value):  # type: ignore[override]
        # Forward-compatibility: callers receiving a reason from a future SDK
        # version that introduced a new value will get UNKNOWN instead of a
        # ValueError. The cross-SDK contract guarantees this behavior so that
        # log-parsers and pattern matchers do not break on upgrade.
        return cls.UNKNOWN


@dataclass(frozen=True, slots=True)
class RequestedRegion:
    """A single entry in :meth:`get_requested_regions`.

    :ivar region_name: Human-readable region name (e.g., ``"East US"``).
        May be empty if the SDK could not resolve a name for the endpoint at
        dispatch time; never ``None``.
    :vartype region_name: str

    :ivar reason: Why this region was dispatched to. See
        :class:`RequestedRegionReason`. May be :attr:`RequestedRegionReason.UNKNOWN`
        for forward compatibility.
    :vartype reason: RequestedRegionReason
    """

    region_name: str
    reason: RequestedRegionReason
