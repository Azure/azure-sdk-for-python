# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

"""Internal class for partition health tracker for circuit breaker.
"""
import logging
import threading
import os
from typing import Any
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper
from azure.cosmos._location_cache import EndpointOperationType
from azure.cosmos._request_object import RequestObject
from ._utils import current_time_millis
from ._constants import _Constants as Constants

MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
MAX_UNAVAILABLE_TIME_MS = 1200 * 1000 # 20 minutes in milliseconds
REFRESH_INTERVAL_MS = 60 * 1000 # 1 minute in milliseconds
INITIAL_UNAVAILABLE_TIME_MS = 60 * 1000 # 1 minute in milliseconds
# partition is unhealthy if sdk tried to recover and failed
UNHEALTHY = "unhealthy"
# partition is unhealthy tentative when it initially marked unavailable
UNHEALTHY_TENTATIVE = "unhealthy_tentative"
# unavailability info keys
UNAVAILABLE_INTERVAL = "unavailableInterval"
LAST_UNAVAILABILITY_CHECK_TIME_STAMP = "lastUnavailabilityCheckTimeStamp"
HEALTH_STATUS = "healthStatus"

class _PartitionHealthInfo(object):
    """
    This internal class keeps the health and statistics for a partition.
    """

    def __init__(self) -> None:
        self.write_failure_count: int = 0
        self.read_failure_count: int = 0
        self.write_success_count: int = 0
        self.read_success_count: int = 0
        self.read_consecutive_failure_count: int = 0
        self.write_consecutive_failure_count: int = 0
        self.unavailability_info: dict[str, Any] = {}

    def reset_failure_rate_health_stats(self) -> None:
        self.write_failure_count = 0
        self.read_failure_count = 0
        self.write_success_count = 0
        self.read_success_count = 0

    def transition_health_status(self, target_health_status: str, curr_time: int) -> None:
        if target_health_status == UNHEALTHY :
            self.unavailability_info[HEALTH_STATUS] = UNHEALTHY
            # reset the last unavailability check time stamp
            self.unavailability_info[UNAVAILABLE_INTERVAL] = \
                min(self.unavailability_info[UNAVAILABLE_INTERVAL] * 2,
                    MAX_UNAVAILABLE_TIME_MS)
            self.unavailability_info[LAST_UNAVAILABILITY_CHECK_TIME_STAMP] \
                = curr_time
        elif target_health_status == UNHEALTHY_TENTATIVE :
            self.unavailability_info = {
                LAST_UNAVAILABILITY_CHECK_TIME_STAMP: curr_time,
                UNAVAILABLE_INTERVAL: INITIAL_UNAVAILABLE_TIME_MS,
                HEALTH_STATUS: UNHEALTHY_TENTATIVE
            }

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}: {self.unavailability_info}\n"
                f"write failure count: {self.write_failure_count}\n"
                f"read failure count: {self.read_failure_count}\n"
                f"write success count: {self.write_success_count}\n"
                f"read success count: {self.read_success_count}\n"
                f"write consecutive failure count: {self.write_consecutive_failure_count}\n"
                f"read consecutive failure count: {self.read_consecutive_failure_count}\n")

def _has_exceeded_failure_rate_threshold(
        successes: int,
        failures: int,
        failure_rate_threshold: int,
) -> bool:
    if successes + failures < MINIMUM_REQUESTS_FOR_FAILURE_RATE:
        return False
    failure_rate = failures / (failures + successes) * 100
    return failure_rate >= failure_rate_threshold

def _should_mark_healthy_tentative(partition_health_info: _PartitionHealthInfo, curr_time: int) -> bool:
    elapsed_time = (curr_time -
                    partition_health_info.unavailability_info[LAST_UNAVAILABILITY_CHECK_TIME_STAMP])
    current_health_status = partition_health_info.unavailability_info[HEALTH_STATUS]
    stale_partition_unavailability_check = partition_health_info.unavailability_info[UNAVAILABLE_INTERVAL]
    # check if the partition key range is still unavailable
    return ((current_health_status == UNHEALTHY and elapsed_time > stale_partition_unavailability_check)
            or (current_health_status == UNHEALTHY_TENTATIVE and elapsed_time > INITIAL_UNAVAILABLE_TIME_MS))

logger = logging.getLogger("azure.cosmos._PartitionHealthTracker")

class _PartitionHealthTracker(object):
    """
    This internal class implements the logic for tracking health thresholds for a partition.
    """

    def __init__(self) -> None:
        # partition -> regions -> health info
        self.pk_range_wrapper_to_health_info: dict[PartitionKeyRangeWrapper, dict[str, _PartitionHealthInfo]] = {}
        self.last_refresh = current_time_millis()
        self.stale_partition_lock = threading.Lock()

    def _transition_health_status_on_failure(
            self,
            pk_range_wrapper: PartitionKeyRangeWrapper,
            location: str
    ) -> None:
        logger.warning("%s has been marked as unavailable.", pk_range_wrapper)
        current_time = current_time_millis()
        if pk_range_wrapper not in self.pk_range_wrapper_to_health_info:
            # healthy -> unhealthy tentative
            partition_health_info = _PartitionHealthInfo()
            partition_health_info.transition_health_status(UNHEALTHY_TENTATIVE, current_time)
            self.pk_range_wrapper_to_health_info[pk_range_wrapper] = {
                location: partition_health_info
            }
        else:
            region_to_partition_health = self.pk_range_wrapper_to_health_info[pk_range_wrapper]
            if location in region_to_partition_health and region_to_partition_health[location].unavailability_info:
                # healthy tentative -> unhealthy
                region_to_partition_health[location].transition_health_status(UNHEALTHY, current_time)
                # if the operation type is not empty, we are in the healthy tentative state
            else:
                # healthy -> unhealthy tentative
                # if the operation type is empty, we are in the unhealthy tentative state
                partition_health_info = _PartitionHealthInfo()
                partition_health_info.transition_health_status(UNHEALTHY_TENTATIVE, current_time)
                self.pk_range_wrapper_to_health_info[pk_range_wrapper][location] = partition_health_info

    def _transition_health_status_on_success(
            self,
            pk_range_wrapper: PartitionKeyRangeWrapper,
            location: str
    ) -> None:
        if pk_range_wrapper in self.pk_range_wrapper_to_health_info:
            # healthy tentative -> healthy
            self.pk_range_wrapper_to_health_info[pk_range_wrapper][location].unavailability_info = {}

    def check_stale_partition_info(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
    ) -> None:
        current_time = current_time_millis()

        if pk_range_wrapper in self.pk_range_wrapper_to_health_info:
            for location, partition_health_info in self.pk_range_wrapper_to_health_info[pk_range_wrapper].items():
                if partition_health_info.unavailability_info:
                    if _should_mark_healthy_tentative(partition_health_info, current_time):
                        # unhealthy or unhealthy tentative -> healthy tentative
                        # only one request should be used to recover
                        with self.stale_partition_lock:
                            if _should_mark_healthy_tentative(partition_health_info, current_time):
                                logger.debug("Attempting recovery for %s in %s where health info is %s.",
                                            pk_range_wrapper,
                                            location,
                                            partition_health_info)
                                # this will trigger one attempt to recover
                                partition_health_info.transition_health_status(UNHEALTHY, current_time)
                                request.healthy_tentative_location = location

        if current_time - self.last_refresh > REFRESH_INTERVAL_MS:
            # all partition stats reset every minute
            self._reset_partition_health_tracker_stats()
            self.last_refresh = current_time


    def get_unhealthy_locations(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
        ) -> list[str]:
        unhealthy_locations = []
        if pk_range_wrapper in self.pk_range_wrapper_to_health_info:
            for location, partition_health_info in self.pk_range_wrapper_to_health_info[pk_range_wrapper].items():
                if (partition_health_info.unavailability_info and
                        not (request.healthy_tentative_location and request.healthy_tentative_location == location)):
                    health_status = partition_health_info.unavailability_info[HEALTH_STATUS]
                    if health_status in (UNHEALTHY_TENTATIVE, UNHEALTHY) :
                        unhealthy_locations.append(location)
        return unhealthy_locations

    def add_failure(
            self,
            pk_range_wrapper: PartitionKeyRangeWrapper,
            operation_type: str,
            location: str
    ) -> None:
        # Retrieve the failure rate threshold from the environment.
        failure_rate_threshold = int(os.environ.get(Constants.FAILURE_PERCENTAGE_TOLERATED,
                                               Constants.FAILURE_PERCENTAGE_TOLERATED_DEFAULT))

        # Ensure that the health info dictionary is properly initialized.
        if pk_range_wrapper not in self.pk_range_wrapper_to_health_info:
            self.pk_range_wrapper_to_health_info[pk_range_wrapper] = {}
        if location not in self.pk_range_wrapper_to_health_info[pk_range_wrapper]:
            self.pk_range_wrapper_to_health_info[pk_range_wrapper][location] = _PartitionHealthInfo()

        health_info = self.pk_range_wrapper_to_health_info[pk_range_wrapper][location]

        # Determine attribute names and environment variables based on the operation type.
        if operation_type == EndpointOperationType.WriteType:
            success_attr = 'write_success_count'
            failure_attr = 'write_failure_count'
            consecutive_attr = 'write_consecutive_failure_count'
            env_key = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE
            default_consecutive_threshold = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE_DEFAULT
        else:
            success_attr = 'read_success_count'
            failure_attr = 'read_failure_count'
            consecutive_attr = 'read_consecutive_failure_count'
            env_key = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ
            default_consecutive_threshold = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT

        # Increment failure and consecutive failure counts.
        setattr(health_info, failure_attr, getattr(health_info, failure_attr) + 1)
        setattr(health_info, consecutive_attr, getattr(health_info, consecutive_attr) + 1)

        # Retrieve the consecutive failure threshold from the environment.
        consecutive_failure_threshold = int(os.environ.get(env_key, default_consecutive_threshold))
        # log the current stats
        logger.debug("Failure for partition %s in location %s has %s",
                    pk_range_wrapper,
                     location,
                     self.pk_range_wrapper_to_health_info[pk_range_wrapper][location])

        # Call the threshold checker with the current stats.
        self._check_thresholds(
            pk_range_wrapper,
            getattr(health_info, success_attr),
            getattr(health_info, failure_attr),
            getattr(health_info, consecutive_attr),
            location,
            failure_rate_threshold,
            consecutive_failure_threshold
        )

    def _check_thresholds(
            self,
            pk_range_wrapper: PartitionKeyRangeWrapper,
            successes: int,
            failures: int,
            consecutive_failures: int,
            location: str,
            failure_rate_threshold: int,
            consecutive_failure_threshold: int,
    ) -> None:
        # check the failure rate was not exceeded
        if _has_exceeded_failure_rate_threshold(
                successes,
                failures,
                failure_rate_threshold
        ):
            self._transition_health_status_on_failure(pk_range_wrapper, location)

        # add to consecutive failures and check that threshold was not exceeded
        if consecutive_failures >= consecutive_failure_threshold:
            self._transition_health_status_on_failure(pk_range_wrapper, location)

    def add_success(self, pk_range_wrapper: PartitionKeyRangeWrapper, operation_type: str, location: str) -> None:
        # Ensure that the health info dictionary is initialized.
        if pk_range_wrapper not in self.pk_range_wrapper_to_health_info:
            self.pk_range_wrapper_to_health_info[pk_range_wrapper] = {}
        if location not in self.pk_range_wrapper_to_health_info[pk_range_wrapper]:
            self.pk_range_wrapper_to_health_info[pk_range_wrapper][location] = _PartitionHealthInfo()

        health_info = self.pk_range_wrapper_to_health_info[pk_range_wrapper][location]

        if operation_type == EndpointOperationType.WriteType:
            health_info.write_success_count += 1
            health_info.write_consecutive_failure_count = 0
        else:
            health_info.read_success_count += 1
            health_info.read_consecutive_failure_count = 0
        self._transition_health_status_on_success(pk_range_wrapper, location)

    def _reset_partition_health_tracker_stats(self) -> None:
        for locations in self.pk_range_wrapper_to_health_info.values():
            for health_info in locations.values():
                health_info.reset_failure_rate_health_stats()
