# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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

"""Internal class for global endpoint manager implementation in the Azure Cosmos
database service.
"""

import asyncio
from six.moves.urllib.parse import urlparse

from .. import _constants as constants
from .. import exceptions
from .._location_cache import LocationCache

# pylint: disable=protected-access

class _GlobalEndpointManager(object):
    """
    This internal class implements the logic for endpoint management for
    geo-replicated database accounts.
    """

    def __init__(self, client):
        self.Client = client
        self.EnableEndpointDiscovery = client.connection_policy.EnableEndpointDiscovery
        self.PreferredLocations = client.connection_policy.PreferredLocations
        self.DefaultEndpoint = client.url_connection
        self.refresh_time_interval_in_ms = self.get_refresh_time_interval_in_ms_stub()
        self.location_cache = LocationCache(
            self.PreferredLocations,
            self.DefaultEndpoint,
            self.EnableEndpointDiscovery,
            client.connection_policy.UseMultipleWriteLocations,
            self.refresh_time_interval_in_ms,
        )
        self.refresh_needed = False
        self.refresh_lock = asyncio.RLock()
        self.last_refresh_time = 0

    def get_refresh_time_interval_in_ms_stub(self):  # pylint: disable=no-self-use
        return constants._Constants.DefaultUnavailableLocationExpirationTime

    def get_write_endpoint(self):
        return self.location_cache.get_write_endpoint()

    def get_read_endpoint(self):
        return self.location_cache.get_read_endpoint()

    def resolve_service_endpoint(self, request):
        return self.location_cache.resolve_service_endpoint(request)

    def mark_endpoint_unavailable_for_read(self, endpoint):
        self.location_cache.mark_endpoint_unavailable_for_read(endpoint)

    def mark_endpoint_unavailable_for_write(self, endpoint):
        self.location_cache.mark_endpoint_unavailable_for_write(endpoint)

    def get_ordered_write_endpoints(self):
        return self.location_cache.get_ordered_write_endpoints()