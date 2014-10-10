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
                 host=MANAGEMENT_HOST):
        super(SqlDatabaseManagementService, self).__init__(
            subscription_id, cert_file, host)

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
    
