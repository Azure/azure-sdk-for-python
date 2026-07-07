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
Azure/azure-cosmos-dotnet-v3#5923). It provides bounded cross-region hedging for
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
    classification: transport-level failures and timeouts, ``503``, ``500``, and
    ``403`` with sub-status ``DatabaseAccountNotFound``.

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
    return False


def _status_codes_from_exception(exception: BaseException) -> Tuple[Optional[int], Optional[int]]:
    if isinstance(exception, exceptions.CosmosHttpResponseError):
        return exception.status_code, exception.sub_status
    return None, None


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

    def is_acceptable_winner(  # pylint: disable=unused-argument
        self,
        result: Optional[ResponseType],
        exception: Optional[BaseException],
        is_hedge: bool,
    ) -> bool:
        """Return True if a settled branch is an acceptable winner.

        A successful response is always acceptable. A regional-failure exception is never
        acceptable (the other branch should win). A hedge-branch ``401``/``403`` response
        is rejected so a hedge auth failure can never win over the primary.

        :param result: The successful response tuple, or None if the branch raised.
        :type result: Optional[Tuple[dict, dict]]
        :param exception: The exception raised by the branch, or None on success.
        :type exception: Optional[BaseException]
        :param is_hedge: Whether the branch is the hedge (non-primary) branch.
        :type is_hedge: bool
        :returns: True if the branch is an acceptable winner.
        :rtype: bool
        """
        if exception is None:
            return True

        if isinstance(exception, CancelledError):
            return False

        status_code, sub_status = _status_codes_from_exception(exception)

        if is_regional_failure(status_code, sub_status, exception):
            return False

        if is_hedge and status_code in (StatusCodes.UNAUTHORIZED, StatusCodes.FORBIDDEN):
            return False

        # A non-regional, non-auth definitive error (e.g. 404) is a real answer; surface it.
        return True

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

    def execute_request(
        self,
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType],
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
            futures: List[Future] = [primary_future, hedge_future]

            for completed_future in as_completed(futures):
                is_primary = completed_future is primary_future
                exception = completed_future.exception()
                result = None if exception is not None else completed_future.result()

                if self.is_acceptable_winner(result, exception, is_hedge=not is_primary):
                    completion_status.set()
                    # Note: no per-region failure is recorded for the primary when the
                    # hedge wins. Metadata cache reads are account-global, not
                    # per-partition, so the circuit-breaker health tracker (keyed on
                    # partition-key ranges) does not apply here; a slow primary is not
                    # necessarily an unhealthy one.
                    if exception is not None:
                        raise exception
                    return result  # type: ignore[return-value]

            # Neither branch produced an acceptable winner; prefer the primary's outcome
            # so the metadata read fails the same way it would without hedging.
            completion_status.set()
            primary_exception = primary_future.exception()
            if primary_exception is not None:
                raise primary_exception
            return primary_future.result()
        finally:
            completion_status.set()
            self._budget.release()


def execute_metadata_hedging(
    handler: MetadataCrossRegionHedgingHandler,
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
    request: HttpRequest,
    execute_request_fn: Callable[..., ResponseType],
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
    :returns: The winning response tuple.
    :rtype: Tuple[dict, dict]
    """
    if request_params.availability_strategy is None:
        request_params.availability_strategy = MetadataCrossRegionHedgingStrategy()
    return handler.execute_request(request_params, global_endpoint_manager, request, execute_request_fn)
