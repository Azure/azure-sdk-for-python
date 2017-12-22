#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Internal class for global endpoint manager implementation in the Azure Cosmos DB database service.
"""

from six.moves.urllib.parse import urlparse
import pydocumentdb.constants as constants
import pydocumentdb.errors as errors

class _GlobalEndpointManager(object):
    """
    This internal class implements the logic for endpoint management for geo-replicated
    database accounts.
    """
    def __init__(self, client):
        self.Client = client        
        self.DefaultEndpoint = client.url_connection
        self._ReadEndpoint = client.url_connection
        self._WriteEndpoint = client.url_connection
        self.EnableEndpointDiscovery = client.connection_policy.EnableEndpointDiscovery
        self.PreferredLocations = client.connection_policy.PreferredLocations
        self.IsEndpointCacheInitialized = False

    @property
    def ReadEndpoint(self):
        """Gets the current read endpoint from the endpoint cache.
        """
        if not self.IsEndpointCacheInitialized:
            self.RefreshEndpointList()

        return self._ReadEndpoint

    @property
    def WriteEndpoint(self):
        """Gets the current write endpoint from the endpoint cache.
        """
        if not self.IsEndpointCacheInitialized:
            self.RefreshEndpointList()

        return self._WriteEndpoint

    def RefreshEndpointList(self):
        """Refreshes the endpoint list by retrieving the writable and readable locations
           from the geo-replicated database account and then updating the locations cache.
           We skip the refreshing if EnableEndpointDiscovery is set to False
        """
        if self.EnableEndpointDiscovery:
            database_account = self._GetDatabaseAccount()
            writable_locations = []
            readable_locations = []
        
            if database_account is not None:
                writable_locations = database_account.WritableLocations        
                readable_locations = database_account.ReadableLocations
            
            # Read and Write endpoints will be initialized to default endpoint if we were not able to get the database account info
            self._WriteEndpoint, self._ReadEndpoint = self.UpdateLocationsCache(writable_locations, readable_locations)
            self.IsEndpointCacheInitialized = True

    def _GetDatabaseAccount(self):
        """Gets the database account first by using the default endpoint, and if that doesn't returns
           use the endpoints for the preferred locations in the order they are specified to get 
           the database account.
        """
        try:
            database_account = self._GetDatabaseAccountStub(self.DefaultEndpoint)
            return database_account
        # If for any reason(non-globaldb related), we are not able to get the database account from the above call to GetDatabaseAccount,
        # we would try to get this information from any of the preferred locations that the user might have specified(by creating a locational endpoint)
        # and keeping eating the exception until we get the database account and return None at the end, if we are not able to get that info from any endpoints
        except errors.HTTPFailure:
            for location_name in self.PreferredLocations:
                locational_endpoint = _GlobalEndpointManager.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = self._GetDatabaseAccountStub(locational_endpoint)
                    return database_account
                except errors.HTTPFailure:
                    pass
        
            return None

    def _GetDatabaseAccountStub(self, endpoint):
        """Stub for getting database account from the client
           which can be used for mocking purposes as well.
        """
        return self.Client.GetDatabaseAccount(endpoint)

    @staticmethod
    def GetLocationalEndpoint(default_endpoint, location_name):
        # For default_endpoint like 'https://contoso.documents.azure.com:443/' parse it to generate URL format
        # This default_endpoint should be global endpoint(and cannot be a locational endpoint) and we agreed to document that
        endpoint_url = urlparse(default_endpoint)

        # hostname attribute in endpoint_url will return 'contoso.documents.azure.com'
        if endpoint_url.hostname is not None:
            hostname_parts = str(endpoint_url.hostname).lower().split('.')
            if hostname_parts is not None:
                # global_database_account_name will return 'contoso'
                global_database_account_name = hostname_parts[0]
            
                # Prepare the locational_database_account_name as contoso-EastUS for location_name 'East US'
                locational_database_account_name = global_database_account_name + '-' + location_name.replace(' ', '')
            
                # Replace 'contoso' with 'contoso-EastUS' and return locational_endpoint as https://contoso-EastUS.documents.azure.com:443/
                locational_endpoint = default_endpoint.lower().replace(global_database_account_name, locational_database_account_name, 1)  
                return locational_endpoint      
        
        return None
        
    def UpdateLocationsCache(self, writable_locations, readable_locations):
        """Updates the read and write endpoints from the passed-in readable and writable locations
        """
        # Use the default endpoint as Read and Write endpoints if EnableEndpointDiscovery 
        # is set to False.
        if not self.EnableEndpointDiscovery:
            write_endpoint = self.DefaultEndpoint            
            read_endpoint = self.DefaultEndpoint
            return write_endpoint, read_endpoint

        # Use the default endpoint as Write endpoint if there are no writable locations, or
        # first writable location as Write endpoint if there are writable locations 
        if len(writable_locations) == 0:
            write_endpoint = self.DefaultEndpoint
        else:
            write_endpoint = writable_locations[0][constants._Constants.DatabaseAccountEndpoint]

        # Use the Write endpoint as Read endpoint if there are no readable locations
        if len(readable_locations) == 0:
            read_endpoint = write_endpoint
        else:
            # Use the writable location as Read endpoint if there are no preferred locations or
            # none of the preferred locations are in read or write locations
            read_endpoint = write_endpoint

            if self.PreferredLocations is None:
                return write_endpoint, read_endpoint

            for preferred_location in self.PreferredLocations:
                # Use the first readable location as Read endpoint from the preferred locations
                for read_location in readable_locations:
                    if read_location[constants._Constants.Name] == preferred_location:
                        read_endpoint = read_location[constants._Constants.DatabaseAccountEndpoint]
                        return write_endpoint, read_endpoint
                # Else, use the first writable location as Read endpoint from the preferred locations
                for write_location in writable_locations:
                    if write_location[constants._Constants.Name] == preferred_location:
                        read_endpoint = write_location[constants._Constants.DatabaseAccountEndpoint]
                        return write_endpoint, read_endpoint
        return write_endpoint, read_endpoint
