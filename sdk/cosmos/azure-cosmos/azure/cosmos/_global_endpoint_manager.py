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
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Any

from azure.core.exceptions import AzureError

from . import _constants as constants
from . import exceptions
from ._request_object import RequestObject
from .documents import DatabaseAccount
from ._location_cache import LocationCache
from ._utils import current_time_millis


# pylint: disable=protected-access
logger = logging.getLogger("azure.cosmos._GlobalEndpointManager")

class _GlobalEndpointManager(object): # pylint: disable=too-many-instance-attributes
    """
    This internal class implements the logic for endpoint management for
    geo-replicated database accounts.
    """

    def __init__(self, client):
        self.client = client
        self.PreferredLocations = client.connection_policy.PreferredLocations
        self.DefaultEndpoint = client.url_connection
        self.refresh_time_interval_in_ms = self.get_refresh_time_interval_in_ms_stub()
        self.location_cache = LocationCache(
            self.DefaultEndpoint,
            client.connection_policy
        )
        self.refresh_needed = False
        self.refresh_lock = threading.RLock()
        self.last_refresh_time = 0
        self._database_account_cache = None
        self.startup = True
        self._refresh_thread = None
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())

    def get_refresh_time_interval_in_ms_stub(self):
        return constants._Constants.DefaultEndpointsRefreshTime

    def get_write_endpoint(self):
        return self.location_cache.get_write_regional_routing_context()

    def get_read_endpoint(self):
        return self.location_cache.get_read_regional_routing_context()

    def _resolve_service_endpoint(
            self,
            request: RequestObject
    ) -> str:
        return self.location_cache.resolve_service_endpoint(request)

    def mark_endpoint_unavailable_for_read(self, endpoint, refresh_cache, context: str):
        self.location_cache.mark_endpoint_unavailable_for_read(endpoint, refresh_cache, context)

    def mark_endpoint_unavailable_for_write(self, endpoint, refresh_cache, context: str):
        self.location_cache.mark_endpoint_unavailable_for_write(endpoint, refresh_cache, context)

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

    def _mark_endpoint_unavailable(self, endpoint: str, context: str):
        """Marks an endpoint as unavailable for the appropriate operations.
        :param str endpoint: The endpoint to mark as unavailable.
        :param str context: The context for marking the endpoint as unavailable.
        """
        write_endpoints = self.location_cache.get_all_write_endpoints()
        self.mark_endpoint_unavailable_for_read(endpoint, False, context)
        if endpoint in write_endpoints:
            self.mark_endpoint_unavailable_for_write(endpoint, False, context)

    def refresh_endpoint_list(self, database_account, **kwargs):
        if current_time_millis() - self.last_refresh_time > self.refresh_time_interval_in_ms:
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
        # 1. If explicit database_account provided and not during startup, just update cache (no health check now)
        # 2. Else if refresh criteria met:
        #    a. If not startup -> spawn background thread to do full database account + health checks
        #    b. If startup -> get database account synchronously, then spawn background health checks,
        #    then mark startup False
        if database_account and not self.startup:
            self.location_cache.perform_on_database_account_read(database_account)
            self.refresh_needed = False
            self.last_refresh_time = current_time_millis()
        else:
            if self.location_cache.should_refresh_endpoints() or self.refresh_needed:
                self.refresh_needed = False
                self.last_refresh_time = current_time_millis()
                if not self.startup:
                    # background full refresh (database account + health checks)
                    self._start_background_refresh(self._refresh_database_account_and_health, kwargs)
                else:
                    self.location_cache.perform_on_database_account_read(database_account)
                    self._start_background_refresh(self._endpoints_health_check, kwargs)
                    self.startup = False

    def _start_background_refresh(self, target: Callable[..., None], kwargs: dict[str, Any]):
        """Starts a daemon thread to run the given target if one is not already active.
        :param Callable target: The function to run in the background thread.
        :param dict kwargs: The keyword arguments to pass to the target function.
        """
        if not (self._refresh_thread and self._refresh_thread.is_alive()):
            def runner():
                try:
                    target(**kwargs)
                except Exception as exception: #pylint: disable=broad-exception-caught
                    # background failures should not crash main thread
                    # Intentionally swallow to avoid affecting foreground; logging could be added.
                    logger.error("Health check task failed: %s", exception, exc_info=True)
            t = threading.Thread(target=runner, name="cosmos-endpoint-refresh", daemon=True)
            self._refresh_thread = t
            t.start()

    def _GetDatabaseAccount(self, **kwargs) -> DatabaseAccount:
        """Gets the database account.

        First tries by using the default endpoint, and if that doesn't work,
        use the endpoints for the preferred locations in the order they are
        specified, to get the database account.
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account
        and the endpoint that was used for the request.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        try:
            database_account = self._GetDatabaseAccountStub(self.DefaultEndpoint, **kwargs)
            self._database_account_cache = database_account
            return database_account
        # If for any reason(non-globaldb related), we are not able to get the database
        # account from the above call to GetDatabaseAccount, we would try to get this
        # information from any of the preferred locations that the user might have
        # specified (by creating a locational endpoint) and keeping eating the exception
        # until we get the database account and return None at the end, if we are not able
        # to get that info from any endpoints
        except (exceptions.CosmosHttpResponseError, AzureError):
            for location_name in self.PreferredLocations:
                locational_endpoint = LocationCache.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = self._GetDatabaseAccountStub(locational_endpoint, **kwargs)
                    self._database_account_cache = database_account
                    return database_account
                except (exceptions.CosmosHttpResponseError, AzureError):
                    self._mark_endpoint_unavailable(locational_endpoint, "_GetDatabaseAccount")
            raise

    def _endpoints_health_check(self, **kwargs):
        """Performs concurrent health checks for each endpoint (background-safe)."""
        endpoints = self.location_cache.endpoints_to_health_check()

        def _health_check(endpoint: str):
            try:
                self.client.health_check(endpoint, **kwargs)
                self.location_cache.mark_endpoint_available(endpoint)
            except (exceptions.CosmosHttpResponseError, AzureError):
                self._mark_endpoint_unavailable(endpoint, "_endpoints_health_check")

        futures = [self.executor.submit(_health_check, ep) for ep in endpoints]
        for f in as_completed(futures):
            # propagate unexpected exceptions (should be none besides those swallowed in health check)
            _ = f.result()
        # After all probes, update cache once
        self.location_cache.update_location_cache()

    def _refresh_database_account_and_health(self, **kwargs):
        database_account = self._GetDatabaseAccount(**kwargs)
        self.location_cache.perform_on_database_account_read(database_account)
        self._endpoints_health_check(**kwargs)

    def _GetDatabaseAccountStub(self, endpoint, **kwargs):
        """Stub for getting database account from the client.
        This can be used for mocking purposes as well.

        :param str endpoint: the endpoint being used to get the database account
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        return self.client.GetDatabaseAccount(endpoint, **kwargs)
