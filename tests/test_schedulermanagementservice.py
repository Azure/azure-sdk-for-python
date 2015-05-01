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
from datetime import datetime

from azure.servicemanagement.schedulermanagementservice import (
    SchedulerManagementService,
)

from azure.servicemanagement import (
    CloudServices,
    CloudService
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
        self.cloud_service_id = getUniqueName('cloud_service_')

    def tearDown(self):
        self.cleanup()
        return super(SchedulerManagementServiceTest, self).tearDown()

    def cleanup(self):
        self.ss.delete_cloud_service(self.cloud_service_id)
        pass

    def _create_cloud_service(self):
        self.ss.create_cloud_service(
            self.cloud_service_id, "label", "description", "West Europe")

    def _create_job_dict(self):
        return {
            "startTime": datetime.utcnow(),
            "action":
            {
                "type": "http",
                "request":
                {
                    "uri": "http://bing.com/",
                    "method": "GET",
                    "headers":
                    {
                        "Content-Type": "text/plain"
                    }
                }
            },
            "recurrence":
            {
                "frequency": "minute",
                "interval": 30,
                "count": 10
            },
            "state": "enabled"
        }

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
        result = self.ss.create_cloud_service(
            self.cloud_service_id, "label", "description", "West Europe")

        # Assert
        self.assertIsNone(result)

    @unittest.skip("functionality not working, haven't had a chance to debug")
    def test_check_name_availability(self):
        # Arrange
        self._create_cloud_service()

        # Act
        result = self.ss.check_job_collection_name(
            self.cloud_service_id, "BOB")

        # Assert
        self.assertIsNotNone(result)

    def test_create_job_collection(self):
        # Arrange
        self._create_cloud_service()

        # Act
        result = self.ss.create_job_collection(
            self.cloud_service_id, getUniqueName('job_collection_'))

        # Assert
        self.assertIsNone(result)

    def test_delete_job_collection(self):
        # Arrange
        job_collection_id = getUniqueName('job_collection_')
        self._create_cloud_service()
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)

        # Act
        result = self.ss.delete_job_collection(
            self.cloud_service_id, job_collection_id)

        # Assert
        self.assertIsNone(result)

    def test_get_job_collection(self):
        # Arrange
        self._create_cloud_service()
        job_collection_id = getUniqueName('job_collection_')
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)

        # Act
        result = self.ss.get_job_collection(
            self.cloud_service_id, job_collection_id)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, job_collection_id)

    def test_create_job(self):
        # Arrange
        job_collection_id = getUniqueName('job_collection_')
        self._create_cloud_service()
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)

        # Act
        job = self._create_job_dict()

        result = self.ss.create_job(
            self.cloud_service_id, job_collection_id, "job_id", job)

        # Assert
        self.assertIsNone(result)

    def test_delete_job(self):
        # Arrange
        job_collection_id = getUniqueName('job_collection_')
        self._create_cloud_service()
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)
        self.ss.create_job(
            self.cloud_service_id,
            job_collection_id,
            "job_id",
            self._create_job_dict()
        )

        # Act
        result = self.ss.delete_job(
            self.cloud_service_id, job_collection_id, "job_id")

        # Assert
        self.assertIsNone(result)

    def test_get_job(self):
        job_collection_id = getUniqueName('job_collection_')
        self._create_cloud_service()
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)
        self.ss.create_job(
            self.cloud_service_id,
            job_collection_id,
            "job_id",
            self._create_job_dict()
        )

        # Act
        result = self.ss.get_job(
            self.cloud_service_id,
            job_collection_id,
            "job_id"
        )
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["state"], "enabled")

    def test_get_all_jobs(self):
        job_collection_id = getUniqueName('job_collection_')
        self._create_cloud_service()
        self.ss.create_job_collection(self.cloud_service_id, job_collection_id)
        self.ss.create_job(
            self.cloud_service_id,
            job_collection_id,
            "job_id",
            self._create_job_dict()
        )

        # Act
        result = self.ss.get_all_jobs(
            self.cloud_service_id,
            job_collection_id
        )
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
