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

import unittest

from azure.servicemanagement.schedulermanagementservice import (
    SchedulerManagementService,
)

from azure.servicemanagement import (
    CloudServices,
    CloudService,
)

from util import (
    AzureTestCase,
    create_service_management,
    credentials,
    getUniqueName
)


class SchedulerManagementServiceTest(AzureTestCase):

    def setUp(self):
        self.ss = create_service_management(SchedulerManagementService)
        self.cloud_service_id = getUniqueName('ss')


    def tearDown(self):
        self.cleanup()
        return super(SchedulerManagementServiceTest, self).tearDown()

    def cleanup(self):
        self.ss.delete_cloud_service(self.cloud_service_id)
        pass

    def _create_cloud_service(self):
        self.ss.create_cloud_service(self.cloud_service_id, "label", "description", "West Europe")

    #--Operations for scheduler ----------------------------------------
    def test_list_cloud_services(self):
        # Arrange
        self._create_cloud_service()

        # Act
        result = self.ss.list_cloud_services()

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CloudServices)

        for cs in result:
            self.assertIsNotNone(cs)
            self.assertIsInstance(cs, CloudService)


    def test_get_cloud_service(self):
        # Arrange
        self._create_cloud_service()

        # Act
        result = self.ss.get_cloud_service(self.cloud_service_id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.cloud_service_id)
        self.assertEqual(result.label, "label")
        self.assertEqual(result.geo_region, "West Europe")

    def test_create_cloud_service(self):
        # Arrange

        # Act
        result = self.ss.create_cloud_service(self.cloud_service_id, "label", "description", "West Europe")

        # Assert
        self.assertIsNone(result)

    @unittest.skip("functionality not working, haven't had a chance to debug")
    def test_check_name_availability(self):
        # Arrange
        self._create_cloud_service()

        # Act
        result = self.ss.check_job_collection_name(self.cloud_service_id,"BOB")

        # Assert
        self.assertIsNotNone(result)
