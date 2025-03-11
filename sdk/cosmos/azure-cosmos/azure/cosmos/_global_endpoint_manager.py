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

import threading
from typing import Tuple

from azure.core.exceptions import AzureError

from . import _constants as constants
from . import exceptions
from .documents import DatabaseAccount
from ._location_cache import LocationCache


# pylint: disable=protected-access


class _GlobalEndpointManager(object): # pylint: disable=too-many-instance-attributes
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
            client.connection_policy.UseMultipleWriteLocations
        )
        self.refresh_needed = False
        self.refresh_lock = threading.RLock()
        self.last_refresh_time = 0
        self._database_account_cache = None

    def get_use_multiple_write_locations(self):
        return self.location_cache.can_use_multiple_write_locations()

    def get_refresh_time_interval_in_ms_stub(self):
        return constants._Constants.DefaultEndpointsRefreshTime

    def get_write_endpoint(self):
        return self.location_cache.get_write_regional_routing_context()

    def get_read_endpoint(self):
        return self.location_cache.get_read_regional_routing_context()

    def resolve_service_endpoint(self, request):
        return self.location_cache.resolve_service_endpoint(request)

    def mark_endpoint_unavailable_for_read(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_read(endpoint, refresh_cache)

    def mark_endpoint_unavailable_for_write(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_write(endpoint, refresh_cache)

    def get_ordered_write_locations(self):
        return self.location_cache.get_ordered_write_locations()

    def get_ordered_read_locations(self):
        return self.location_cache.get_ordered_read_locations()

    def can_use_multiple_write_locations(self, request):
        return self.location_cache.can_use_multiple_write_locations_for_request(request)

    def force_refresh_on_startup(self, database_account):
        self.refresh_needed = True
        self.refresh_endpoint_list(database_account)

    def update_location_cache(self):
        self.location_cache.update_location_cache()

    def refresh_endpoint_list(self, database_account, **kwargs):
        if self.location_cache.current_time_millis() - self.last_refresh_time > self.refresh_time_interval_in_ms:
            self.refresh_needed = True
        if self.refresh_needed:
            with self.refresh_lock:
                # if refresh is not needed or refresh is already taking place, return
                if not self.refresh_needed:
                    return
                try:
                    self._refresh_endpoint_list_private(database_account, **kwargs)
                except Exception as e:
                    raise e

    def _refresh_endpoint_list_private(self, database_account=None, **kwargs):
        if database_account:
            self.location_cache.perform_on_database_account_read(database_account)
            self.refresh_needed = False
            self.last_refresh_time = self.location_cache.current_time_millis()
        else:
            if self.location_cache.should_refresh_endpoints() or self.refresh_needed:
                self.refresh_needed = False
                self.last_refresh_time = self.location_cache.current_time_millis()
                # this will perform getDatabaseAccount calls to check endpoint health
                self._endpoints_health_check(**kwargs)

    def _GetDatabaseAccount(self, **kwargs) -> Tuple[DatabaseAccount, str]:
        """Gets the database account.

        First tries by using the default endpoint, and if that doesn't work,
        use the endpoints for the preferred locations in the order they are
        specified, to get the database account.
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account
        and the endpoint that was used for the request.
        :rtype: tuple of (~azure.cosmos.DatabaseAccount, str)
        """
        try:
            database_account = self._GetDatabaseAccountStub(self.DefaultEndpoint, **kwargs)
            self._database_account_cache = database_account
            self.location_cache.mark_endpoint_available(self.DefaultEndpoint)
            return database_account, self.DefaultEndpoint
        # If for any reason(non-globaldb related), we are not able to get the database
        # account from the above call to GetDatabaseAccount, we would try to get this
        # information from any of the preferred locations that the user might have
        # specified (by creating a locational endpoint) and keeping eating the exception
        # until we get the database account and return None at the end, if we are not able
        # to get that info from any endpoints
        except (exceptions.CosmosHttpResponseError, AzureError):
            # when atm is available, L: 145, 146 should be removed as the global endpoint shouldn't be used
            # for dataplane operations anymore
            self.mark_endpoint_unavailable_for_read(self.DefaultEndpoint, False)
            self.mark_endpoint_unavailable_for_write(self.DefaultEndpoint, False)
            for location_name in self.PreferredLocations:
                locational_endpoint = LocationCache.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = self._GetDatabaseAccountStub(locational_endpoint, **kwargs)
                    self._database_account_cache = database_account
                    self.location_cache.mark_endpoint_available(locational_endpoint)
                    return database_account, locational_endpoint
                except (exceptions.CosmosHttpResponseError, AzureError):
                    self.mark_endpoint_unavailable_for_read(locational_endpoint, False)
                    self.mark_endpoint_unavailable_for_write(locational_endpoint, False)
            raise

    def _endpoints_health_check(self, **kwargs):
        """Gets the database account for each endpoint.

        Validating if the endpoint is healthy else marking it as unavailable.
        """
        endpoints_attempted = set()
        database_account, attempted_endpoint = self._GetDatabaseAccount(**kwargs)
        endpoints_attempted.add(attempted_endpoint)
        self.location_cache.perform_on_database_account_read(database_account)
        # get all the regional routing contexts to check
        endpoints = self.location_cache.endpoints_to_health_check()
        success_count = 0
        for endpoint in endpoints:
            if endpoint not in endpoints_attempted:
                if success_count >= 4:
                    break
                endpoints_attempted.add(endpoint)
                # save current dba timeouts
                previous_dba_read_timeout = self.Client.connection_policy.DBAReadTimeout
                previous_dba_connection_timeout = self.Client.connection_policy.DBAConnectionTimeout
                try:
                    if (endpoint in
                            self.location_cache.location_unavailability_info_by_endpoint):
                        # if the endpoint is unavailable, we need to lower the timeouts to be more aggressive in the
                        # health check. This helps reduce the time the health check is blocking all requests.
                        self.Client.connection_policy.override_dba_timeouts(constants._Constants
                                                                            .UnavailableEndpointDBATimeouts,
                                                                            constants._Constants
                                                                            .UnavailableEndpointDBATimeouts)
                        self.Client._GetDatabaseAccountCheck(endpoint, **kwargs)
                    else:
                        self.Client._GetDatabaseAccountCheck(endpoint, **kwargs)
                    success_count += 1
                    self.location_cache.mark_endpoint_available(endpoint)
                except (exceptions.CosmosHttpResponseError, AzureError):
                    self.mark_endpoint_unavailable_for_read(endpoint, False)
                    self.mark_endpoint_unavailable_for_write(endpoint, False)
                finally:
                    # after the health check for that endpoint setting the timeouts back to their original values
                    self.Client.connection_policy.override_dba_timeouts(previous_dba_read_timeout,
                                                                        previous_dba_connection_timeout)
        self.location_cache.update_location_cache()

    def _GetDatabaseAccountStub(self, endpoint, **kwargs):
        """Stub for getting database account from the client.
        This can be used for mocking purposes as well.

        :param str endpoint: the endpoint being used to get the database account
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        if endpoint in self.location_cache.location_unavailability_info_by_endpoint:
            previous_dba_read_timeout = self.Client.connection_policy.DBAReadTimeout
            previous_dba_connection_timeout = self.Client.connection_policy.DBAConnectionTimeout
            try:
                # if the endpoint is unavailable, we need to lower the timeouts to be more aggressive in the
                # health check. This helps reduce the time the health check is blocking all requests.
                self.Client.connection_policy.override_dba_timeouts(constants._Constants
                                                                    .UnavailableEndpointDBATimeouts,
                                                                    constants._Constants
                                                                    .UnavailableEndpointDBATimeouts)
                database_account = self.Client.GetDatabaseAccount(endpoint, **kwargs)
            finally:
                # after the health check for that endpoint setting the timeouts back to their original values
                self.Client.connection_policy.override_dba_timeouts(previous_dba_read_timeout,
                                                                    previous_dba_connection_timeout)
        else:
            database_account = self.Client.GetDatabaseAccount(endpoint, **kwargs)
        return database_account
