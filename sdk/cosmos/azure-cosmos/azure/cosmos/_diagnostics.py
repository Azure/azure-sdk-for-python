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

"""Module-private backing state for the hedging-detection API.

A single :class:`_HedgingDetectionState` is constructed per operation by the
synchronous and asynchronous orchestrators (``_synchronized_request`` /
``aio/_asynchronous_request``). The same instance is then:

* threaded into the hedging handler via a **closure argument**
  (NOT through :class:`~azure.cosmos._request_object.RequestObject`; the
  deepcopy at ``_availability_strategy_handler.py:96`` would silently swallow
  child appends — see SE-002),
* threaded into ``_retry_utility.Execute`` via ``**kwargs``,
* attached to successful response wrappers (``CosmosDict``, ``CosmosList``,
  ``CosmosItemPaged``, ``CosmosAsyncItemPaged``) via a private sentinel key
  on the response-headers dict that is popped in each wrapper's ``__init__``,
* attached to exception types (``CosmosHttpResponseError``,
  ``CosmosBatchOperationError``, ``CosmosClientTimeoutError``) via the
  private ``_hedging_state`` attribute before the exception is re-raised.

All mutations are guarded by a ``threading.Lock``. CPython's GIL covers
``list.append`` but the lock is required to make the ``HEDGING`` reason ↔
``_hedging_started`` flag compound update atomic from any reader's perspective
(SE-017). Snapshots returned by the public accessors are taken under the lock
and returned as tuples so callers cannot mutate the internal lists.
"""

import threading
from typing import Tuple

from ._diagnostics_types import RequestedRegion, RequestedRegionReason

# Module-private sentinel key used to stash a ``_HedgingDetectionState`` on a
# response-headers ``CaseInsensitiveDict`` so the value flows from the
# synchronized request back up to the wrapper construction site
# (``CosmosDict``, ``CosmosList``, ``CosmosItemPaged``, etc.) without
# requiring every intermediary signature to change. Each wrapper's
# ``__init__`` pops this key, so customer code that inspects
# ``get_response_headers()`` never sees it.
#
# Double-underscore-bracketed name guarantees no collision with any real HTTP
# header (header field-names per RFC 7230 cannot contain ``_``).
HEDGING_STATE_HEADER_KEY = "__hedging_state__"


class _HedgingDetectionState:
    """Thread-safe backing state for the three public hedging-detection accessors.

    One instance per Cosmos operation. Shared by reference across the
    orchestrator, the hedging handler arms, the retry utility, and ultimately
    the response wrapper or exception that bubbles up to the customer.
    """

    __slots__ = ("_lock", "_requested", "_responded", "_hedging_started")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requested: list = []  # list[RequestedRegion]
        self._responded: list = []  # list[str]
        self._hedging_started = False

    # ------------------------------------------------------------------ writes
    def _record_request(self, region_name: str, reason: RequestedRegionReason) -> None:
        """Append a dispatched-region entry. Sets the hedging-started flag
        atomically when reason is ``HEDGING`` (compound update guarded by lock).
        """
        if region_name is None:
            region_name = ""
        entry = RequestedRegion(region_name=region_name, reason=reason)
        with self._lock:
            self._requested.append(entry)
            if reason is RequestedRegionReason.HEDGING:
                self._hedging_started = True

    def _record_response(self, region_name: str) -> None:
        """Append a responding-region entry. Duplicates are intentional —
        the same region may produce multiple responses (e.g., a late response
        after a hedge winner)."""
        if region_name is None:
            region_name = ""
        with self._lock:
            self._responded.append(region_name)

    # ------------------------------------------------------------------- reads
    def is_hedging_started(self) -> bool:
        with self._lock:
            return self._hedging_started

    def get_requested_regions(self) -> Tuple[RequestedRegion, ...]:
        with self._lock:
            return tuple(self._requested)

    def get_responded_regions(self) -> Tuple[str, ...]:
        with self._lock:
            return tuple(self._responded)


# --------------------------------------------------------------------------- #
# Mixin used by the five public wrapper / exception types to expose the three
# accessor methods without duplicating bodies. The mixin only reads
# ``self._hedging_state`` (or its absence) and returns safe defaults if no
# state has been attached.
# --------------------------------------------------------------------------- #
class _HedgingDetectionAccessorsMixin:
    """Shared implementation of the three public accessors.

    Mixed into ``CosmosDict``, ``CosmosList``, ``CosmosItemPaged``,
    ``CosmosAsyncItemPaged``, ``CosmosHttpResponseError``,
    ``CosmosBatchOperationError``, and ``CosmosClientTimeoutError`` to avoid
    method-body duplication. Each consumer class is responsible for setting
    ``self._hedging_state`` (or leaving it ``None``); the accessors fall back
    to safe defaults when state is unattached.
    """

    # Default attribute slot; consumer types may override via ``__init__``.
    _hedging_state = None  # type: ignore[assignment]

    def is_hedging_started(self) -> bool:
        """Return ``True`` if the SDK actually dispatched the operation to a
        hedge region.

        Returns ``False`` for non-hedged operations, including the case where
        hedging was configured but the primary responded under the hedge
        threshold (hedge-arm tasks created but cancelled before they ran;
        no fan-out occurred).

        ``False`` does NOT mean hedging is disabled or misconfigured. To check
        whether hedging is configured on the client, inspect the client-level
        ``availability_strategy`` configuration.
        """
        state = self._hedging_state
        if state is None:
            return False
        return state.is_hedging_started()

    def get_requested_regions(self) -> Tuple[RequestedRegion, ...]:
        """Return the regions the SDK actually dispatched this operation to,
        tagged with a reason.

        Ordering is observed dispatch order (orchestrator wall-clock). Includes
        the initial attempt. Empty only on pre-flight validation failures or
        when no state was attached (the operation never reached the
        orchestrator).

        Append site is the actual dispatch point (post-threshold delay for
        hedge arms); registered-but-never-dispatched hedge tasks do NOT appear
        here.

        **Contract is "dispatched, not necessarily wire-issued".** An entry
        reflects the SDK's decision to commit to dispatching — for hedge arms,
        this means the per-arm threshold delay elapsed without cancellation,
        so the dispatch hook fired. A cancellation in the small window between
        that dispatch decision and the underlying HTTP send (asyncio task
        scheduling jitter, ThreadPoolExecutor scheduling) still leaves the
        entry in this list. Callers should treat the list as a record of
        intent-to-dispatch, not a record of wire-issued requests.

        :class:`RequestedRegionReason` is non-exhaustive — handle
        :attr:`~RequestedRegionReason.UNKNOWN` and unknown values defensively
        (``_missing_`` returns :attr:`~RequestedRegionReason.UNKNOWN` for
        future enum members).
        """
        state = self._hedging_state
        if state is None:
            return ()
        return state.get_requested_regions()

    def get_responded_regions(self) -> Tuple[str, ...]:
        """Return the regions that returned a response (success or failure),
        in arrival order.

        **Duplicates are allowed and expected.** The same region may appear
        more than once if it produced multiple responses (e.g., a late response
        after a hedge winner). ``len(get_responded_regions()) > 1`` does NOT
        imply that more than one distinct region responded. For unique regions
        in arrival order use ``tuple(dict.fromkeys(resp.get_responded_regions()))``;
        for an unordered set use ``set(resp.get_responded_regions())``.
        """
        state = self._hedging_state
        if state is None:
            return ()
        return state.get_responded_regions()


def _attach_state_to_headers(headers, state):
    """Helper: stash a ``_HedgingDetectionState`` on a response-headers dict
    under the module-private sentinel key. The wrapper-type ``__init__`` pops
    this key so customers never see it on ``get_response_headers()``.

    No-op if either argument is falsy."""
    if headers is None or state is None:
        return
    try:
        headers[HEDGING_STATE_HEADER_KEY] = state
    except (TypeError, AttributeError):  # pragma: no cover - defensive
        # If headers is not a dict-like (shouldn't happen on the response
        # path), silently swallow rather than break the request.
        pass


def _pop_state_from_headers(headers):
    """Helper used by every wrapper type's ``__init__``: pop and return the
    private state sentinel from a response-headers dict. Returns ``None`` if
    no state is attached. Also accepts ``None`` headers safely."""
    if headers is None:
        return None
    try:
        return headers.pop(HEDGING_STATE_HEADER_KEY, None)
    except (TypeError, AttributeError):  # pragma: no cover - defensive
        return None
