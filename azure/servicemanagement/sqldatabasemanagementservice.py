#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from azure import (
    MANAGEMENT_HOST,
    _parse_service_resources_response,
    )
from azure.servicemanagement import (
    Servers,
    Database,
    )
from azure.servicemanagement.servicemanagementclient import (
    _ServiceManagementClient,
    )

class SqlDatabaseManagementService(_ServiceManagementClient):
    ''' Note that this class is a preliminary work on SQL Database
        management. Since it lack a lot a features, final version
        can be slightly different from the current one.
    '''

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST, request_session=None):
        '''
        Initializes the sql database management service.

        subscription_id: Subscription to manage.
        cert_file:
            Path to .pem certificate file (httplib), or location of the
            certificate in your Personal certificate store (winhttp) in the
            CURRENT_USER\my\CertificateName format.
            If a request_session is specified, then this is unused.
        host: Live ServiceClient URL. Defaults to Azure public cloud.
        request_session:
            Session object to use for http requests. If this is specified, it
            replaces the default use of httplib or winhttp. Also, the cert_file
            parameter is unused when a session is passed in.
            The session object handles authentication, and as such can support
            multiple types of authentication: .pem certificate, oauth.
            For example, you can pass in a Session instance from the requests
            library. To use .pem certificate authentication with requests
            library, set the path to the .pem file on the session.cert
            attribute.
        '''
        super(SqlDatabaseManagementService, self).__init__(
            subscription_id, cert_file, host, request_session)

    #--Operations for sql servers ----------------------------------------
    def list_servers(self):
        '''
        List the SQL servers defined on the account.
        '''
        return self._perform_get(self._get_list_servers_path(),
                                 Servers)

    #--Operations for sql databases ----------------------------------------
    def list_databases(self, name):
        '''
        List the SQL databases defined on the specified server name
        '''
        response = self._perform_get(self._get_list_databases_path(name),
                                     None)
        return _parse_service_resources_response(response, Database)


    #--Helper functions --------------------------------------------------
    def _get_list_servers_path(self):
        return self._get_path('services/sqlservers/servers', None)

    def _get_list_databases_path(self, name):
        # *contentview=generic is mandatory*
        return self._get_path('services/sqlservers/servers/',
                              name) + '/databases?contentview=generic' 
    
