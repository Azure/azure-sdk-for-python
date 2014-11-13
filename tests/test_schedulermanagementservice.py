# coding: utf-8

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


from azure.servicemanagement.schedulermanagementservice import (
    SchedulerManagementService,
)

from azure.servicemanagement import (
    CloudServices,
    CloudService,
)

from .util import (
    AzureTestCase,
    create_service_management,
    credentials,
)


class SchedulerManagementServiceTest(AzureTestCase):

    def setUp(self):
        self.sqlms = create_service_management(SchedulerManagementService)

    def tearDown(self):
        self.cleanup()
        return super(SchedulerManagementServiceTest, self).tearDown()

    def cleanup(self):
        pass

    #--Operations for scheduler ----------------------------------------
    def test_list_cloud_services(self):
        # Arrange

        # Act
        result = self.sms.list_cloud_services()

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CloudServices)

        for cs in result:
            self.assertIsNotNone(cs)
            self.assertIsInstance(cs, CloudService)
