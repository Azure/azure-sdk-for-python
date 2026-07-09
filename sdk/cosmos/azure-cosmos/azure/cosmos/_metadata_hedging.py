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

"""Cold-start metadata cache cross-region hedging for Azure Cosmos DB.

This is the synchronous port of the .NET ``MetadataHedgingStrategy`` (PR
Azure/azure-cosmos-dotnet-v3#5999). It provides bounded cross-region hedging for
cold-start metadata cache reads (container/Collection reads and PartitionKeyRange
read-feed reads): the primary request is dispatched immediately and, if it has not
produced an acceptable response within a fixed SDK-derived threshold, a single hedge
request is dispatched to a second region. The first acceptable winner is returned.
"""

import copy
import logging
import os
import time
from concurrent.futures import CancelledError, Future, ThreadPoolExecutor, as_completed
from threading import Event, Semaphore
from typing import Any, Callable, Dict, List, Optional, Tuple

from azure.core.exceptions import ServiceRequestError, ServiceResponseError  # pylint: disable=no-legacy-azure-core-http-response-import
from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from . import exceptions
from ._availability_strategy_config import (
    DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET,
    MetadataCrossRegionHedgingStrategy,
)
from ._availability_strategy_handler_base import AvailabilityStrategyHandlerMixin
from ._global_partition_endpoint_manager_circuit_breaker import _GlobalPartitionEndpointManagerForCircuitBreaker
from ._request_object import RequestObject
from .documents import _OperationType
from .http_constants import ResourceType, StatusCodes, SubStatusCodes

logger = logging.getLogger("azure.cosmos.metadata_hedging")

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]


class MetadataHedgeSkipReason:
    """Reason a cold-start metadata hedge was not dispatched (for diagnostics/logging)."""
    NONE = "None"
    NOT_SUPPORTED_RESOURCE = "ResourceTypeNotSupported"
    ALREADY_HEDGING = "AlreadyHedgedThisOperation"
    SINGLE_REGION = "SingleRegion"
    BUDGET_EXHAUSTED = "BudgetExhausted"


def is_supported_metadata_request(request_params: RequestObject) -> bool:
    """Return True if the request is a metadata read eligible for cold-start hedging.

    Supported reads mirror the .NET design: a Collection read or a PartitionKeyRange
    read-feed. PartitionKeyRange reads issued as a plain ``Read`` are also accepted
    defensively.

    :param request_params: The request parameters.
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :returns: True if the request is a supported metadata read.
    :rtype: bool
    """
    resource_type = request_params.resource_type
    operation_type = request_params.operation_type
    if resource_type == ResourceType.Collection and operation_type == _OperationType.Read:
        return True
    if resource_type == ResourceType.PartitionKeyRange and operation_type in (
        _OperationType.ReadFeed,
        _OperationType.Read,
    ):
        return True
    return False


def is_regional_failure(
    status_code: Optional[int],
    sub_status: Optional[int],
    exception: Optional[BaseException],
) -> bool:
    """Return True if the response/exception is a regional failure for metadata hedging.

    A regional failure is one that should advance a metadata read to a different region
    (so it must not be accepted as a winner). This mirrors the .NET ``IsRegionalFailure``
    classification: transport-level failures and timeouts, ``503``, ``500``,
    ``403`` with sub-status ``DatabaseAccountNotFound``, and ``410`` with sub-status
    ``LeaseNotFound`` (a regional/backend-lease failure, not a request-definitive error).

    :param status_code: HTTP status code from the response, or None for a transport failure.
    :type status_code: Optional[int]
    :param sub_status: Cosmos sub-status code from the response.
    :type sub_status: Optional[int]
    :param exception: Exception observed instead of (or in addition to) the response, or None.
    :type exception: Optional[BaseException]
    :returns: True if the failure is regional.
    :rtype: bool
    """
    if isinstance(exception, (ServiceRequestError, ServiceResponseError)):
        return True

    if status_code is None:
        return False

    if status_code in (StatusCodes.SERVICE_UNAVAILABLE, StatusCodes.INTERNAL_SERVER_ERROR):
        return True
    if status_code == StatusCodes.FORBIDDEN and sub_status == SubStatusCodes.DATABASE_ACCOUNT_NOT_FOUND:
        return True
    if status_code == StatusCodes.GONE and sub_status == SubStatusCodes.LEASE_NOT_FOUND:
        return True
    return False


def _status_codes_from_exception(exception: BaseException) -> Tuple[Optional[int], Optional[int]]:
    if isinstance(exception, exceptions.CosmosHttpResponseError):
        return exception.status_code, exception.sub_status
    return None, None


class _BranchOutcome:
    """Classification of a settled hedging branch (parity with the .NET ``BranchOutcome``).

    Keeping the primary authoritative depends on this split: only a ``REGIONAL_FAILURE`` is
    worth hedging, and a hedge can win *only* by producing a ``SUCCESS`` -- it can never
    override a primary ``SUCCESS`` or ``DEFINITIVE`` outcome.
    """
    SUCCESS = "Success"
    REGIONAL_FAILURE = "RegionalFailure"
    DEFINITIVE = "Definitive"
    CANCELLED = "Cancelled"


def classify_branch_outcome(exception: Optional[BaseException]) -> str:
    """Classify a settled (non-cancelled) branch outcome.

    A missing exception is a ``SUCCESS`` (these metadata reads throw for every status
    ``>= 400``, so an exceptionless return is always a good response). A regional-failure
    exception is ``REGIONAL_FAILURE`` -- the region, not the request, is at fault, so
    another region is worth trying. Any other terminal error -- a non-regional definitive
    error such as ``404`` / ``409`` / ``412`` or an auth failure -- is ``DEFINITIVE`` and
    authoritative; a hedge must never win with it. Internal loser cancellation is handled
    by the caller (which knows its own ``CancelledError`` type) and never reaches here.

    :param exception: The exception raised by the branch, or None on success.
    :type exception: Optional[BaseException]
    :returns: One of the :class:`_BranchOutcome` string constants.
    :rtype: str
    """
    if exception is None:
        return _BranchOutcome.SUCCESS
    status_code, sub_status = _status_codes_from_exception(exception)
    if is_regional_failure(status_code, sub_status, exception):
        return _BranchOutcome.REGIONAL_FAILURE
    return _BranchOutcome.DEFINITIVE


class MetadataCrossRegionHedgingHandler(AvailabilityStrategyHandlerMixin):
    """Bounded cross-region hedging handler for cold-start metadata cache reads.

    One instance per client. The per-client concurrency budget caps the number of
    in-flight metadata hedges; when it is exhausted, eligible requests fall back to a
    primary-only send.

    :param concurrency_budget: Max number of in-flight metadata hedges for this client.
    :type concurrency_budget: int
    """

    def __init__(self, concurrency_budget: int = DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET) -> None:
        budget = max(1, concurrency_budget)
        self._budget = Semaphore(budget)
        # Long-lived executor shared across this client's metadata hedges. Every in-flight
        # hedge needs two worker threads (primary + hedge), so size the pool to at least
        # 2 * budget; otherwise hedge tasks can starve behind primaries on low-core hosts.
        max_workers = max(os.cpu_count() or 1, 2 * budget)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)  # pylint: disable=consider-using-with

    def close(self) -> None:
        """Shut down the shared hedge executor, releasing its worker threads.

        Invoked from the client/connection teardown path (``CosmosClient.__exit__`` /
        ``close``) so a disposed client does not leak its metadata-hedge worker threads.
        Idempotent -- safe to call multiple times.

        :rtype: None
        """
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _classify_future(self, future: "Future") -> str:
        """Classify a COMPLETED future into a :class:`_BranchOutcome`.

        :param future: A future that is guaranteed to be done.
        :type future: ~concurrent.futures.Future
        :returns: One of the :class:`_BranchOutcome` string constants.
        :rtype: str
        """
        if future.cancelled():
            return _BranchOutcome.CANCELLED
        exception = future.exception()
        if isinstance(exception, CancelledError):
            return _BranchOutcome.CANCELLED
        return classify_branch_outcome(exception)

    @staticmethod
    def _wait_settled(future: "Future") -> None:
        """Block until ``future`` settles, swallowing its outcome (classified separately).

        :param future: The future to wait for.
        :type future: ~concurrent.futures.Future
        :rtype: None
        """
        try:
            future.exception()
        except CancelledError:
            pass

    def _finish(
        self,
        future: "Future",
        winner_sink: Optional[List[Any]],
        is_primary: bool,
        available_locations: List[str],
        request_params: RequestObject,
        completion_status: Event,
    ) -> ResponseType:
        """Signal completion, record the winner, and return/raise the winning branch's outcome.

        :param future: The winning (completed) future whose outcome is returned.
        :type future: ~concurrent.futures.Future
        :param winner_sink: Optional length-1 sink for the winner descriptor.
        :type winner_sink: Optional[List[Any]]
        :param is_primary: Whether the winning branch is the primary.
        :type is_primary: bool
        :param available_locations: Ordered applicable region names (index 0 = primary).
        :type available_locations: List[str]
        :param request_params: The originating request parameters.
        :type request_params: ~azure.cosmos._request_object.RequestObject
        :param completion_status: The shared completion event to signal the loser.
        :type completion_status: ~threading.Event
        :returns: The winning response tuple.
        :rtype: Tuple[dict, dict]
        """
        completion_status.set()
        self._record_winner(winner_sink, is_primary, available_locations, request_params)
        if future.cancelled():
            raise CancelledError("The request has been cancelled")
        exception = future.exception()
        if exception is not None:
            raise exception
        return future.result()  # type: ignore[return-value]

    def _send_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType],
        location_index: int,
        available_locations: List[str],
        complete_status: Event,
    ) -> ResponseType:
        strategy = request_params.availability_strategy
        if strategy is None:
            raise ValueError("availability_strategy should not be null for metadata hedging")

        delay = 0 if location_index == 0 else strategy.threshold_ms
        if delay > 0:
            time.sleep(delay / 1000)

        params = copy.deepcopy(request_params)
        params.is_hedging_request = location_index > 0
        params.completion_status = complete_status
        params.excluded_locations = self._create_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations,
        )

        req = copy.deepcopy(request)

        if complete_status.is_set():
            raise CancelledError("The request has been cancelled")

        return execute_request_fn(params, req)

    def _resolve_winner(
        self,
        first_future: "Future",
        primary_future: "Future",
        hedge_future: "Future",
    ) -> Tuple["Future", bool]:
        """Resolve which settled branch wins, keeping the primary authoritative.

        A hedge can win only by settling first with a ``SUCCESS``, and even then never over
        a primary that has already produced a definitive (non-regional) outcome. A primary
        regional failure yields to a successful hedge; otherwise the primary's outcome (its
        exception rethrown by :meth:`_finish`) is authoritative. Mirrors the .NET
        ``ResolveWinnerAsync``.

        :param first_future: The branch that settled first.
        :type first_future: ~concurrent.futures.Future
        :param primary_future: The primary branch future.
        :type primary_future: ~concurrent.futures.Future
        :param hedge_future: The hedge branch future.
        :type hedge_future: ~concurrent.futures.Future
        :returns: The winning future and whether it is the primary branch.
        :rtype: Tuple[~concurrent.futures.Future, bool]
        """
        if first_future is hedge_future:
            if self._classify_future(hedge_future) == _BranchOutcome.SUCCESS:
                # A successful hedge wins unless the primary has ALREADY settled with a
                # definitive (non-regional) outcome, which the hedge must never override.
                if primary_future.done() and \
                        self._classify_future(primary_future) != _BranchOutcome.REGIONAL_FAILURE:
                    return primary_future, True
                return hedge_future, False
            # A non-success hedge can never win; wait for the primary's authoritative outcome.
            self._wait_settled(primary_future)
            return primary_future, True

        # Primary settled first. Success or a definitive error is authoritative.
        if self._classify_future(primary_future) != _BranchOutcome.REGIONAL_FAILURE:
            return primary_future, True

        # Primary regional failure -> a successful hedge may now win; otherwise the primary's
        # (authoritative) regional failure is returned.
        self._wait_settled(hedge_future)
        if self._classify_future(hedge_future) == _BranchOutcome.SUCCESS:
            return hedge_future, False
        return primary_future, True

    def execute_request(
        self,
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType],
        winner_sink: Optional[List[Any]] = None,
    ) -> ResponseType:
        """Execute a metadata read with bounded primary + single-hedge cross-region hedging.

        :param request_params: Request parameters for the metadata read.
        :type request_params: ~azure.cosmos._request_object.RequestObject
        :param global_endpoint_manager: Manager for endpoint routing and health tracking.
        :type global_endpoint_manager:
            ~azure.cosmos._GlobalPartitionEndpointManagerForCircuitBreaker
        :param request: The HTTP request to be executed.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :param execute_request_fn: Function that executes the actual request.
        :type execute_request_fn: Callable[..., Tuple[dict, dict]]
        :param winner_sink: Optional length-1 list to receive the winner descriptor for
            PartitionKeyRange continuation pinning (``hedge_won`` / ``winning_region`` /
            ``pin_excluded_locations``).
        :type winner_sink: Optional[List[Any]]
        :returns: The winning response tuple.
        :rtype: Tuple[dict, dict]
        """
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)
        if len(available_locations) <= 1:
            logger.debug("Metadata hedge skipped: %s", MetadataHedgeSkipReason.SINGLE_REGION)
            return execute_request_fn(request_params, request)

        acquired = self._budget.acquire(blocking=False)  # pylint: disable=consider-using-with
        if not acquired:
            logger.debug("Metadata hedge skipped: %s", MetadataHedgeSkipReason.BUDGET_EXHAUSTED)
            return execute_request_fn(request_params, request)

        completion_status = Event()
        try:
            primary_future = self._executor.submit(
                self._send_with_delay, request_params, request, execute_request_fn,
                0, available_locations, completion_status)
            hedge_future = self._executor.submit(
                self._send_with_delay, request_params, request, execute_request_fn,
                1, available_locations, completion_status)

            # Resolve the primary-vs-hedge race, keeping the primary authoritative: a hedge
            # can win only by settling first with a SUCCESS, and even then only while the
            # primary has not already produced a definitive (non-regional) answer. Mirrors
            # the .NET ``ResolveWinnerAsync``.
            #
            # Note: no per-region failure is recorded when the hedge wins. Metadata cache
            # reads are account-global, not per-partition, so the circuit-breaker health
            # tracker (keyed on partition-key ranges) does not apply here; a slow primary is
            # not necessarily an unhealthy one.
            first_future = next(as_completed([primary_future, hedge_future]))
            winner_future, is_primary = self._resolve_winner(
                first_future, primary_future, hedge_future)
            return self._finish(
                winner_future, winner_sink, is_primary,
                available_locations, request_params, completion_status)
        finally:
            completion_status.set()
            self._budget.release()


def execute_metadata_hedging(
    handler: MetadataCrossRegionHedgingHandler,
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
    request: HttpRequest,
    execute_request_fn: Callable[..., ResponseType],
    winner_sink: Optional[List[Any]] = None,
) -> ResponseType:
    """Execute a metadata read with cold-start cross-region hedging.

    :param handler: The per-client metadata hedging handler.
    :type handler: ~azure.cosmos._metadata_hedging.MetadataCrossRegionHedgingHandler
    :param request_params: Request parameters for the metadata read.
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :param global_endpoint_manager: Manager for endpoint routing and health tracking.
    :type global_endpoint_manager:
        ~azure.cosmos._GlobalPartitionEndpointManagerForCircuitBreaker
    :param request: The HTTP request to be executed.
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param execute_request_fn: Function that executes the actual request.
    :type execute_request_fn: Callable[..., Tuple[dict, dict]]
    :param winner_sink: Optional length-1 list to receive the winner descriptor
        (``hedge_won`` / ``winning_region`` / ``pin_excluded_locations``) so a
        PartitionKeyRange drain can pin later pages to the winning region.
    :type winner_sink: Optional[List[Any]]
    :returns: The winning response tuple.
    :rtype: Tuple[dict, dict]
    """
    if request_params.availability_strategy is None:
        request_params.availability_strategy = MetadataCrossRegionHedgingStrategy()
    return handler.execute_request(
        request_params, global_endpoint_manager, request, execute_request_fn, winner_sink=winner_sink)
