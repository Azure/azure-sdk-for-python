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
import os
from typing import Dict, Set, Any
from ._constants import _Constants as Constants
from azure.cosmos._location_cache import current_time_millis, EndpointOperationType
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper, Range


MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
REFRESH_INTERVAL = 60 * 1000 # milliseconds
INITIAL_UNAVAILABLE_TIME = 60 * 1000 # milliseconds
# partition is unhealthy if sdk tried to recover and failed
UNHEALTHY = "unhealthy"
# partition is unhealthy tentative when it initially marked unavailable
UNHEALTHY_TENTATIVE = "unhealthy_tentative"
# partition is healthy tentative when sdk is trying to recover
HEALTHY_TENTATIVE = "healthy_tentative"
# unavailability info keys
LAST_UNAVAILABILITY_CHECK_TIME_STAMP = "lastUnavailabilityCheckTimeStamp"
HEALTH_STATUS = "healthStatus"


def _has_exceeded_failure_rate_threshold(
        successes: int,
        failures: int,
        failure_rate_threshold: int,
) -> bool:
    if successes + failures < MINIMUM_REQUESTS_FOR_FAILURE_RATE:
        return False
    return (failures / successes * 100) >= failure_rate_threshold

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
        self.unavailability_info: Dict[str, Any] = {}


    def reset_health_stats(self) -> None:
        self.write_failure_count = 0
        self.read_failure_count = 0
        self.write_success_count = 0
        self.read_success_count = 0
        self.read_consecutive_failure_count = 0
        self.write_consecutive_failure_count = 0


class PartitionHealthTracker(object):
    """
    This internal class implements the logic for tracking health thresholds for a partition.
    """


    def __init__(self) -> None:
        # partition -> regions -> health info
        self.pkrange_wrapper_to_health_info: Dict[PartitionKeyRangeWrapper, Dict[str, _PartitionHealthInfo]] = {}
        self.last_refresh = current_time_millis()

    # TODO: @tvaron3 look for useful places to add logs

    def mark_partition_unavailable(self, pkrange_wrapper: PartitionKeyRangeWrapper, location: str) -> None:
        # mark the partition key range as unavailable
        self._transition_health_status_on_failure(pkrange_wrapper, location)

    def _transition_health_status_on_failure(
            self,
            pkrange_wrapper: PartitionKeyRangeWrapper,
            location: str
    ) -> None:
        current_time = current_time_millis()
        if pkrange_wrapper not in self.pkrange_wrapper_to_health_info:
            # healthy -> unhealthy tentative
            partition_health_info = _PartitionHealthInfo()
            partition_health_info.unavailability_info = {
                LAST_UNAVAILABILITY_CHECK_TIME_STAMP: current_time,
                HEALTH_STATUS: UNHEALTHY_TENTATIVE
            }
            self.pkrange_wrapper_to_health_info[pkrange_wrapper] = {
                location: partition_health_info
            }
        else:
            region_to_partition_health = self.pkrange_wrapper_to_health_info[pkrange_wrapper]
            if location in region_to_partition_health:
                # healthy tentative -> unhealthy
                # if the operation type is not empty, we are in the healthy tentative state
                self.pkrange_wrapper_to_health_info[pkrange_wrapper][location].unavailability_info[HEALTH_STATUS] = UNHEALTHY
                # reset the last unavailability check time stamp
                self.pkrange_wrapper_to_health_info[pkrange_wrapper][location].unavailability_info[LAST_UNAVAILABILITY_CHECK_TIME_STAMP] = UNHEALTHY
            else:
                # healthy -> unhealthy tentative
                # if the operation type is empty, we are in the unhealthy tentative state
                partition_health_info = _PartitionHealthInfo()
                partition_health_info.unavailability_info = {
                    LAST_UNAVAILABILITY_CHECK_TIME_STAMP: current_time,
                    HEALTH_STATUS: UNHEALTHY_TENTATIVE
                }
                self.pkrange_wrapper_to_health_info[pkrange_wrapper][location] = partition_health_info

    def _transition_health_status_on_success(
            self,
            pkrange_wrapper: PartitionKeyRangeWrapper,
            location: str
    ) -> None:
        if pkrange_wrapper in self.pkrange_wrapper_to_health_info:
            # healthy tentative -> healthy
            self.pkrange_wrapper_to_health_info[pkrange_wrapper].pop(location, None)

    def _check_stale_partition_info(self, pkrange_wrapper: PartitionKeyRangeWrapper) -> None:
        current_time = current_time_millis()

        stale_partition_unavailability_check = int(os.getenv(Constants.STALE_PARTITION_UNAVAILABILITY_CHECK,
                                                         Constants.STALE_PARTITION_UNAVAILABILITY_CHECK_DEFAULT)) * 1000
        if pkrange_wrapper in self.pkrange_wrapper_to_health_info:
            for location, partition_health_info in self.pkrange_wrapper_to_health_info[pkrange_wrapper].items():
                elapsed_time = current_time - partition_health_info.unavailability_info[LAST_UNAVAILABILITY_CHECK_TIME_STAMP]
                current_health_status = partition_health_info.unavailability_info[HEALTH_STATUS]
                # check if the partition key range is still unavailable
                if ((current_health_status == UNHEALTHY and elapsed_time > stale_partition_unavailability_check)
                        or (current_health_status == UNHEALTHY_TENTATIVE
                            and  elapsed_time > INITIAL_UNAVAILABLE_TIME)):
                    # unhealthy or unhealthy tentative -> healthy tentative
                    self.pkrange_wrapper_to_health_info[pkrange_wrapper][location].unavailability_info[HEALTH_STATUS] = HEALTHY_TENTATIVE

        if current_time - self.last_refresh < REFRESH_INTERVAL:
            # all partition stats reset every minute
            self._reset_partition_health_tracker_stats()


    def get_excluded_locations(self, pkrange_wrapper: PartitionKeyRangeWrapper) -> Set[str]:
        self._check_stale_partition_info(pkrange_wrapper)
        if pkrange_wrapper in self.pkrange_wrapper_to_health_info:
            return set(self.pkrange_wrapper_to_health_info[pkrange_wrapper].keys())
        else:
            return set()


    def add_failure(self, pkrange_wrapper: PartitionKeyRangeWrapper, operation_type: str, location: str) -> None:
        # Retrieve the failure rate threshold from the environment.
        failure_rate_threshold = int(os.getenv(Constants.FAILURE_PERCENTAGE_TOLERATED,
                                               Constants.FAILURE_PERCENTAGE_TOLERATED_DEFAULT))

        # Ensure that the health info dictionary is properly initialized.
        if pkrange_wrapper not in self.pkrange_wrapper_to_health_info:
            self.pkrange_wrapper_to_health_info[pkrange_wrapper] = {}
        if location not in self.pkrange_wrapper_to_health_info[pkrange_wrapper]:
            self.pkrange_wrapper_to_health_info[pkrange_wrapper][location] = _PartitionHealthInfo()

        health_info = self.pkrange_wrapper_to_health_info[pkrange_wrapper][location]

        # Determine attribute names and environment variables based on the operation type.
        if operation_type == EndpointOperationType.WriteType:
            success_attr = 'write_success_count'
            failure_attr = 'write_failure_count'
            consecutive_attr = 'write_consecutive_failure_count'
            env_key = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE
            default_consec_threshold = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE_DEFAULT
        else:
            success_attr = 'read_success_count'
            failure_attr = 'read_failure_count'
            consecutive_attr = 'read_consecutive_failure_count'
            env_key = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ
            default_consec_threshold = Constants.CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ_DEFAULT

        # Increment failure and consecutive failure counts.
        setattr(health_info, failure_attr, getattr(health_info, failure_attr) + 1)
        setattr(health_info, consecutive_attr, getattr(health_info, consecutive_attr) + 1)

        # Retrieve the consecutive failure threshold from the environment.
        consecutive_failure_threshold = int(os.getenv(env_key, default_consec_threshold))

        # Call the threshold checker with the current stats.
        self._check_thresholds(
            pkrange_wrapper,
            getattr(health_info, success_attr),
            getattr(health_info, failure_attr),
            getattr(health_info, consecutive_attr),
            location,
            failure_rate_threshold,
            consecutive_failure_threshold
        )

    def _check_thresholds(
            self,
            pkrange_wrapper: PartitionKeyRangeWrapper,
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
            self._transition_health_status_on_failure(pkrange_wrapper, location)

        # add to consecutive failures and check that threshold was not exceeded
        if consecutive_failures >= consecutive_failure_threshold:
            self._transition_health_status_on_failure(pkrange_wrapper, location)

    def add_success(self, pkrange_wrapper: PartitionKeyRangeWrapper, operation_type: str, location: str) -> None:
        # Ensure that the health info dictionary is initialized.
        if pkrange_wrapper not in self.pkrange_wrapper_to_health_info:
            self.pkrange_wrapper_to_health_info[pkrange_wrapper] = {}
        if location not in self.pkrange_wrapper_to_health_info[pkrange_wrapper]:
            self.pkrange_wrapper_to_health_info[pkrange_wrapper][location] = _PartitionHealthInfo()

        health_info = self.pkrange_wrapper_to_health_info[pkrange_wrapper][location]

        if operation_type == EndpointOperationType.WriteType:
            health_info.write_success_count += 1
            health_info.write_consecutive_failure_count = 0
        else:
            health_info.read_success_count += 1
            health_info.read_consecutive_failure_count = 0
        self._transition_health_status_on_success(pkrange_wrapper, operation_type)


    def _reset_partition_health_tracker_stats(self) -> None:
        for pkrange_wrapper in self.pkrange_wrapper_to_health_info:
            for location in self.pkrange_wrapper_to_health_info[pkrange_wrapper]:
                self.pkrange_wrapper_to_health_info[pkrange_wrapper][location].reset_health_stats()
