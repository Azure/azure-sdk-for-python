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

import asyncio # pylint: disable=do-not-import-asyncio
import logging

from azure.core.exceptions import AzureError

from .. import _constants as constants
from .. import exceptions
from .._location_cache import LocationCache, EndpointOperationType


# pylint: disable=protected-access

logger = logging.getLogger("azure.cosmos._GlobalEndpointManager")

class _GlobalEndpointManager(object): # pylint: disable=too-many-instance-attributes
    """
    This internal class implements the logic for endpoint management for
    geo-replicated database accounts.
    """

    def __init__(self, client):
        self.client = client
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
        self.startup = True
        self.refresh_task = None
        self.refresh_needed = False
        self.refresh_lock = asyncio.Lock()
        self.last_refresh_time = 0
        self._database_account_cache = None
        self.consecutive_failures = {EndpointOperationType.ReadType: 0, EndpointOperationType.WriteType: 0}

    def get_refresh_time_interval_in_ms_stub(self):
        return constants._Constants.DefaultUnavailableLocationExpirationTime

    def get_write_endpoint(self):
        return self.location_cache.get_write_dual_endpoint()

    def get_read_endpoint(self):
        return self.location_cache.get_read_dual_endpoint()

    def resolve_service_endpoint(self, request):
        return self.location_cache.resolve_service_endpoint(request)

    def mark_endpoint_unavailable_for_read(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_read(endpoint, refresh_cache)

    def mark_endpoint_unavailable_for_write(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_write(endpoint, refresh_cache)

    def get_ordered_write_locations(self):
        return self.location_cache.get_ordered_write_locations()

    def can_use_multiple_write_locations(self, request):
        return self.location_cache.can_use_multiple_write_locations_for_request(request)

    async def force_refresh_on_startup(self, database_account):
        self.refresh_needed = True
        await self.refresh_endpoint_list(database_account)
        self.startup = False

    def update_location_cache(self):
        self.location_cache.update_location_cache()

    async def refresh_endpoint_list(self, database_account, **kwargs):
        if self.refresh_task and self.refresh_task.done():
            try:
                await self.refresh_task
                self.refresh_task = None
            except Exception as exception:
                logger.warning("Exception in health check task: %s", exception)
        if self.location_cache.current_time_millis() - self.last_refresh_time > self.refresh_time_interval_in_ms:
            self.refresh_needed = True
        if self.refresh_needed:
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
            self.last_refresh_time = self.location_cache.current_time_millis()
        else:
            if self.location_cache.should_refresh_endpoints() or self.refresh_needed:
                self.refresh_needed = False
                self.last_refresh_time = self.location_cache.current_time_millis()
                if not self.startup:
                    # this will perform getDatabaseAccount calls to check endpoint health
                    # in background
                    self.refresh_task = asyncio.create_task(self._endpoints_health_check(**kwargs))
                else:
                   # on startup do this in foreground
                   await self._endpoints_health_check(**kwargs)

    async def _endpoints_health_check(self, **kwargs):
        """Gets the database account for each endpoint.

        Validating if the endpoint is healthy else marking it as unavailable.
        """
        endpoints_attempted = set()
        database_account, endpoint = await self._GetDatabaseAccount(**kwargs)
        endpoints_attempted.add(endpoint)
        self.location_cache.perform_on_database_account_read(database_account)
        # should use the regions in the order returned from gateway and only the ones specified in preferred locations
        read_account_dual_endpoints_iterator = iter(self.location_cache.account_read_dual_endpoints_by_location.values())
        first_read_dual_endpoint = None
        for read_dual_endpoint in read_account_dual_endpoints_iterator:
            if read_dual_endpoint in self.location_cache.read_dual_endpoints:
                first_read_dual_endpoint = read_dual_endpoint
                break
        if first_read_dual_endpoint:
            dual_endpoints = [first_read_dual_endpoint]
        else:
            dual_endpoints = []
        write_dual_endpoints = [endpoint for endpoint in self.location_cache.account_write_dual_endpoints_by_location.values()
                                if endpoint in self.location_cache.write_dual_endpoints]
        dual_endpoints.extend(write_dual_endpoints)
        success_count = 0
        for dual_endpoint in dual_endpoints:
            if dual_endpoint.get_primary() not in endpoints_attempted:
                if success_count >= 2:
                    break
                endpoints_attempted.add(dual_endpoint.get_primary())
                try:
                    await self.client._GetDatabaseAccountCheck(dual_endpoint.get_primary(), **kwargs)
                    # health check continues until 2 successes or all endpoints are checked
                    success_count += 1
                    self.location_cache.mark_endpoint_available(dual_endpoint.get_primary())
                except (exceptions.CosmosHttpResponseError, AzureError):
                    if dual_endpoint in self.location_cache.read_dual_endpoints:
                        self.mark_endpoint_unavailable_for_read(dual_endpoint.get_primary(), False)
                    if dual_endpoint in self.location_cache.write_dual_endpoints:
                        self.mark_endpoint_unavailable_for_write(dual_endpoint.get_primary(), False)
        self.location_cache.update_location_cache()

    async def _GetDatabaseAccount(self, **kwargs):
        """Gets the database account.

        First tries by using the default endpoint, and if that doesn't work,
        use the endpoints for the preferred locations in the order they are
        specified, to get the database account.
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        try:
            database_account = await self._GetDatabaseAccountStub(self.DefaultEndpoint, **kwargs)
            self._database_account_cache = database_account
            return database_account, self.DefaultEndpoint
        # If for any reason(non-globaldb related), we are not able to get the database
        # account from the above call to GetDatabaseAccount, we would try to get this
        # information from any of the preferred locations that the user might have
        # specified (by creating a locational endpoint) and keeping eating the exception
        # until we get the database account and return None at the end, if we are not able
        # to get that info from any endpoints
        except (exceptions.CosmosHttpResponseError, AzureError):
            self.mark_endpoint_unavailable_for_read(self.DefaultEndpoint, False)
            self.mark_endpoint_unavailable_for_write(self.DefaultEndpoint, False)
            for location_name in self.PreferredLocations:
                locational_endpoint = LocationCache.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = await self._GetDatabaseAccountStub(locational_endpoint, **kwargs)
                    self._database_account_cache = database_account
                    return database_account, locational_endpoint
                except (exceptions.CosmosHttpResponseError, AzureError):
                    self.mark_endpoint_unavailable_for_read(locational_endpoint, False)
                    self.mark_endpoint_unavailable_for_write(locational_endpoint, False)
            raise

    async def _GetDatabaseAccountStub(self, endpoint, **kwargs):
        """Stub for getting database account from the client.
        This can be used for mocking purposes as well.

        :param str endpoint: the endpoint being used to get the database account
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        return await self.client.GetDatabaseAccount(endpoint, **kwargs)
