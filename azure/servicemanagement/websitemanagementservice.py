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
    _str,
    )
from azure.servicemanagement import (
    WebSpaces,
    WebSpace,
    Sites,
    Site,
    )
from azure.servicemanagement.servicemanagementclient import (
    _ServiceManagementClient,
    )

class WebsiteManagementService(_ServiceManagementClient):
    ''' Note that this class is a preliminary work on WebSite
        management. Since it lack a lot a features, final version
        can be slightly different from the current one.
    '''

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST):
        super(WebsiteManagementService, self).__init__(
            subscription_id, cert_file, host)

    #--Operations for web sites ----------------------------------------
    def list_webspaces(self):
        '''
        List the webspaces defined on the account.
        '''
        return self._perform_get(self._get_list_webspaces_path(),
                                 WebSpaces)

    def get_webspace(self, webspace_name):
        '''
        Get details of a specific webspace.
        '''
        return self._perform_get(self._get_webspace_details_path(webspace_name),
                                 WebSpace)

    def list_sites(self, webspace_name):
        '''
        List the web sites defined on this webspace.
        '''
        return self._perform_get(self._get_sites_path(webspace_name),
                                 Sites)

    def get_site(self, webspace_name, website_name):
        '''
        List the web sites defined on this webspace.
        '''
        return self._perform_get(self._get_sites_details_path(webspace_name,
                                                              website_name),
                                 Site)

    #--Helper functions --------------------------------------------------
    def _get_list_webspaces_path(self):
        return self._get_path('services/webspaces', None)

    def _get_webspace_details_path(self, webspace_name):
        return self._get_path('services/webspaces/', webspace_name)

    def _get_sites_path(self, webspace_name):
        return self._get_path('services/webspaces/',
                              webspace_name) + '/sites'

    def _get_sites_details_path(self, webspace_name, website_name):
        return self._get_path('services/webspaces/',
                              webspace_name) + '/sites/' + _str(website_name) 
