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
from typing import Optional, Mapping, Any
from .documents import _OperationType
from .http_constants import ResourceType
from ._constants import _Constants as Constants

class RequestObject(object): # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            resource_type: str,
            operation_type: str,
            headers: dict[str, Any],
            pk_val: Optional[Any] = None,
            endpoint_override: Optional[str] = None,
    ) -> None:
        self.resource_type = resource_type
        self.operation_type = operation_type
        self.endpoint_override = endpoint_override
        self.should_clear_session_token_on_session_read_failure: bool = False  # pylint: disable=name-too-long
        self.headers = headers
        self.use_preferred_locations: Optional[bool] = None
        self.location_index_to_route: Optional[int] = None
        self.location_endpoint_to_route: Optional[str] = None
        self.excluded_locations: Optional[list[str]] = None
        self.excluded_locations_circuit_breaker: list[str] = []
        self.healthy_tentative_location: Optional[str] = None
        self.read_timeout_override: Optional[int] = None
        self.pk_val = pk_val
        self.retry_write: int = 0

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

    def set_excluded_location_from_options(self, options: Mapping[str, Any]) -> None:
        if self._can_set_excluded_location(options):
            self.excluded_locations = options['excludedLocations']

    def set_retry_write(self, request_options: Mapping[str, Any], client_retry_write: int) -> None:
        if self.resource_type == ResourceType.Document:
            if request_options and request_options.get(Constants.Kwargs.RETRY_WRITE):
                # If request retry write is > 0, set the option
                self.retry_write = request_options[Constants.Kwargs.RETRY_WRITE]
            elif client_retry_write and self.operation_type != _OperationType.Patch:
                # If it is not a patch operation and the client config is set, set the retry write to the client value
                self.retry_write = client_retry_write
            else:
                self.retry_write = 0

    def set_excluded_locations_from_circuit_breaker(self, excluded_locations: list[str]) -> None: # pylint: disable=name-too-long
        self.excluded_locations_circuit_breaker = excluded_locations
