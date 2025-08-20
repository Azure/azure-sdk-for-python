# The MIT License (MIT)
# Copyright (c) 2018 Microsoft Corporation

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

"""Represents a request object.
"""
from types import SimpleNamespace
from typing import Optional, Mapping, Any, Dict, List

from ._availability_strategy import AvailabilityStrategy
from ._constants import _Constants as Constants
from .documents import _OperationType
from .http_constants import ResourceType


class RequestObject(object): # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            resource_type: str,
            operation_type: str,
            headers: Dict[str, Any],
            endpoint_override: Optional[str] = None,
    ) -> None:
        self.resource_type = resource_type
        self.operation_type = operation_type
        self.endpoint_override = endpoint_override
        self.should_clear_session_token_on_session_read_failure: bool = False  # pylint: disable=name-too-long
        self.headers = headers
        self.availability_strategy: Optional[AvailabilityStrategy] = None
        self.use_preferred_locations: Optional[bool] = None
        self.location_index_to_route: Optional[int] = None
        self.location_endpoint_to_route: Optional[str] = None
        self.last_routed_location_endpoint_within_region: Optional[str] = None
        self.excluded_locations: Optional[List[str]] = None
        self.excluded_locations_circuit_breaker: List[str] = []
        self.healthy_tentative_location: Optional[str] = None
        self.retry_write: bool = False
        self.is_hedging_request: bool = False # Flag to track if this is a hedged request
        self.completion_status: Optional[SimpleNamespace] = None # Status shared between parallel requests

    def route_to_location_with_preferred_location_flag(  # pylint: disable=name-too-long
        self,
        location_index: int,
        use_preferred_locations: bool
    ) -> None:
        self.location_index_to_route = location_index
        self.use_preferred_locations = use_preferred_locations
        self.location_endpoint_to_route = None

    def route_to_location(self, location_endpoint: str) -> None:
        self.location_index_to_route = None
        self.use_preferred_locations = None
        self.location_endpoint_to_route = location_endpoint

    def clear_route_to_location(self) -> None:
        self.location_index_to_route = None
        self.use_preferred_locations = None
        self.location_endpoint_to_route = None

    def _can_set_excluded_location(self, options: Mapping[str, Any]) -> bool:
        # If 'excludedLocations' wasn't in the options, excluded locations cannot be set
        if (options is None
            or 'excludedLocations' not in options):
            return False

        # The 'excludedLocations' cannot be None
        if options['excludedLocations'] is None:
            raise ValueError("Excluded locations cannot be None. "
                             "If you want to remove all excluded locations, try passing an empty list.")

        return True

    def set_availability_strategy_from_options(
            self,
            options: Mapping[str, Any],
            client_strategy: Optional[AvailabilityStrategy] = None) -> None:
        """Sets the availability strategy for this request from options.
        If not in options, uses the client's default strategy.

        :param options: The request options that may contain availabilityStrategy
        :type options: Mapping[str, Any]
        :param client_strategy: The client's default availability strategy
        :type client_strategy: ~azure.cosmos.AvailabilityStrategy
        :return: None
        """
        # First try to get from options
        if options is not None and 'availabilityStrategy' in options and options['availabilityStrategy'] is not None:
            self.availability_strategy = options['availabilityStrategy']
        # If not in options, use client default
        elif client_strategy is not None:
            self.availability_strategy = client_strategy

    def set_excluded_location_from_options(self, options: Mapping[str, Any]) -> None:
        if self._can_set_excluded_location(options):
            self.excluded_locations = options['excludedLocations']

    def set_retry_write(self, request_options: Mapping[str, Any], client_retry_write: bool) -> None:
        if self.resource_type == ResourceType.Document:
            if request_options and request_options.get(Constants.Kwargs.RETRY_WRITE):
                # If request retry write is True, set the option
                self.retry_write = request_options[Constants.Kwargs.RETRY_WRITE]
            elif client_retry_write and self.operation_type != _OperationType.Patch:
                # If it is not a patch operation and the client config is set, set the retry write to True
                self.retry_write = client_retry_write

    def set_excluded_locations_from_circuit_breaker(self, excluded_locations: List[str]) -> None: # pylint: disable=name-too-long
        self.excluded_locations_circuit_breaker = excluded_locations

    def set_is_hedging_request(self, is_hedging_request: bool) -> None:
        self.is_hedging_request = is_hedging_request

    def set_completion_status(self, status: SimpleNamespace) -> None:
        """Set the shared completion status between parallel requests
        
        :param status: Status object shared between parallel requests. If None, creates new one.
        :type status: ~types.SimpleNamespace
        """
        if status is None:
            raise ValueError("completion status argument can not be None")
        self.completion_status = status

    def get_completion_status(self) -> Optional[SimpleNamespace]:
        """Get the shared completion status
        
        :return: The completion status or None if not set
        :rtype: Optional[~types.SimpleNamespace]
        """
        return self.completion_status

    def get_is_hedging_request(self) -> bool:
        """Check if this is a hedged request
        
        :return: True if this is a hedged request, False otherwise
        :rtype: bool
        """
        return self.is_hedging_request

    def should_cancel_request(self) -> bool:
        """Check if this request should be cancelled due to parallel request completion
        
        :return: True if request should be cancelled, False otherwise
        :rtype: bool
        """
        status = self.get_completion_status()
        return status is not None and status.is_completed
