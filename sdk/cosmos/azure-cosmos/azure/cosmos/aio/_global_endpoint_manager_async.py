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
        self.refresh_lock = asyncio.Lock()
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

    def can_use_multiple_write_locations(self, request):
        return self.location_cache.can_use_multiple_write_locations_for_request(request)

    async def force_refresh(self, database_account):
        self.refresh_needed = True
        await self.refresh_endpoint_list(database_account)

    async def refresh_endpoint_list(self, database_account, **kwargs):
        async with self.refresh_lock:
            # if refresh is not needed or refresh is already taking place, return
            if not self.refresh_needed:
                return
            try:
                await self._refresh_endpoint_list_private(database_account, **kwargs)
            except Exception as e:
                raise e

    async def _refresh_endpoint_list_private(self, database_account=None, **kwargs):
        if database_account:
            self.location_cache.perform_on_database_account_read(database_account)
            self.refresh_needed = False

        if (
            self.location_cache.should_refresh_endpoints()
            and self.location_cache.current_time_millis() - self.last_refresh_time > self.refresh_time_interval_in_ms
        ):
            if not database_account:
                database_account = await self._GetDatabaseAccount(**kwargs)
                self.location_cache.perform_on_database_account_read(database_account)
                self.last_refresh_time = self.location_cache.current_time_millis()
                self.refresh_needed = False

    async def _GetDatabaseAccount(self, **kwargs):
        """Gets the database account.

        First tries by using the default endpoint, and if that doesn't work,
        use the endpoints for the preferred locations in the order they are
        specified, to get the database account.
        """
        try:
            database_account = await self._GetDatabaseAccountStub(self.DefaultEndpoint, **kwargs)
            return database_account
        # If for any reason(non-globaldb related), we are not able to get the database
        # account from the above call to GetDatabaseAccount, we would try to get this
        # information from any of the preferred locations that the user might have
        # specified (by creating a locational endpoint) and keeping eating the exception
        # until we get the database account and return None at the end, if we are not able
        # to get that info from any endpoints
        except exceptions.CosmosHttpResponseError:
            for location_name in self.PreferredLocations:
                locational_endpoint = _GlobalEndpointManager.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = await self._GetDatabaseAccountStub(locational_endpoint, **kwargs)
                    return database_account
                except exceptions.CosmosHttpResponseError:
                    pass

            return None

    async def _GetDatabaseAccountStub(self, endpoint, **kwargs):
        """Stub for getting database account from the client.

        This can be used for mocking purposes as well.
        """
        return await self.Client.GetDatabaseAccount(endpoint, **kwargs)