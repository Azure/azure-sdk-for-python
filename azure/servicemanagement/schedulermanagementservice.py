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
    _str
    )
from azure.servicemanagement import (
    CloudServices,
    )
from azure.servicemanagement.servicemanagementclient import (
    _ServiceManagementClient,
    )

class SchedulerManagementService(_ServiceManagementClient):
    ''' Note that this class is a preliminary work on Scheduler
        management. Since it lack a lot a features, final version
        can be slightly different from the current one.
    '''

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST):
        super(SchedulerManagementService, self).__init__(
            subscription_id, cert_file, host)

    #--Operations for scheduler ----------------------------------------
    def list_cloud_services(self):
        '''
        List the cloud services for scheduling defined on the account.
        '''
        return self._perform_get(self._get_list_cloud_services_path(),
                                 CloudServices)


    #--Helper functions --------------------------------------------------
    def _get_list_cloud_services_path(self):
        return self._get_path('cloudservices', None)

