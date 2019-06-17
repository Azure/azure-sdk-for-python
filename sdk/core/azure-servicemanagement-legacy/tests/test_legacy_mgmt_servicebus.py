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
import time
import unittest

from azure.common import (
    AzureHttpError,
    AzureMissingResourceHttpError,
)
from azure.servicemanagement import ServiceBusManagementService
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


class LegacyMgmtServiceBusTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtServiceBusTest, self).setUp()

        self.sms = self.create_service_management(ServiceBusManagementService)

        self.sb_namespace = self.get_resource_name('uts')

    def tearDown(self):
        if not self.is_playback():
            try:
                self.sms.delete_namespace(self.sb_namespace)
            except:
                pass
        return super(LegacyMgmtServiceBusTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _namespace_exists(self, name):
        try:
            ns = self.sms.get_namespace(name)
            # treat it as non-existent if it is in process of being removed
            return ns.status != 'Removing'
        except:
            return False

    def _wait_for_namespace_active(self, name):
        count = 0
        ns = self.sms.get_namespace(name)
        while ns.status != 'Active':
            count = count + 1
            if count > 120:
                self.assertTrue(
                    False,
                    'Timed out waiting for service bus namespace activation.')
            time.sleep(5)
            ns = self.sms.get_namespace(name)

    #--Operations for service bus ----------------------------------------
    @record
    def test_get_regions(self):
        # Arrange

        # Act
        result = self.sms.get_regions()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        for region in result:
            self.assertTrue(len(region.code) > 0)
            self.assertTrue(len(region.fullname) > 0)

    @record
    def test_list_namespaces(self):
        # Arrange

        # Act
        result = self.sms.list_namespaces()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        for ns in result:
            self.assertTrue(len(ns.name) > 0)
            self.assertTrue(len(ns.region) > 0)

    @record
    def test_get_namespace(self):
        # Arrange
        name = self.settings.SERVICEBUS_NAME

        # Act
        result = self.sms.get_namespace(name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, name)
        self.assertIsNotNone(result.region)
        self.assertIsNotNone(result.default_key)
        self.assertIsNotNone(result.status)
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.acs_management_endpoint)
        self.assertIsNotNone(result.servicebus_endpoint)
        self.assertIsNotNone(result.connection_string)
        self.assertTrue(result.enabled)

    @record
    def test_get_namespace_with_non_existing_namespace(self):
        # Arrange
        name = self.sb_namespace

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sms.get_namespace(name)

        # Assert

    @record
    def test_check_namespace_availability_not_available(self):
        # arrange
        name = self.settings.SERVICEBUS_NAME

        # act
        availability = self.sms.check_namespace_availability(name)

        # assert
        self.assertFalse(availability.result)

    @record
    def test_check_namespace_availability_available(self):
        # arrange
        name = 'someunusedname'

        # act
        availability = self.sms.check_namespace_availability(name)

        # assert
        self.assertTrue(availability.result)

    @record
    def test_create_namespace(self):
        # Arrange
        name = self.sb_namespace
        region = 'West US'

        # Act
        result = self.sms.create_namespace(name, region)
        self._wait_for_namespace_active(name)

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._namespace_exists(name))
        
    @record
    def test_list_topics(self):
        # Arrange
        name = self.settings.SERVICEBUS_NAME

        # Act
        result = self.sms.list_topics(name)
        
        # Assert
        # You HAVE to have at least Topic in SERVICEBUS_NAME, otherwise
        # we don't actually test the parser
        self.assertGreater(len(result), 0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    @record
    def test_list_queues(self):
        # Arrange
        name = self.settings.SERVICEBUS_NAME

        # Act
        result = self.sms.list_queues(name)
        
        # Assert
        # You HAVE to have at least Topic in SERVICEBUS_NAME, otherwise
        # we don't actually test the parser
        self.assertGreater(len(result), 0)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    @record
    def test_list_notification_hubs(self):
        # Arrange
        name = self.settings.SERVICEBUS_NAME

        # Act
        result = self.sms.list_notification_hubs(name)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    @record
    def test_list_relays(self):
        # Arrange
        name = self.settings.SERVICEBUS_NAME

        # Act
        result = self.sms.list_relays(name)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    @record
    def test_create_namespace_with_existing_namespace(self):
        # Arrange
        name = self.sb_namespace
        region = 'West US'
        self.sms.create_namespace(name, region)
        self._wait_for_namespace_active(name)

        # Act
        with self.assertRaises(AzureHttpError):
            self.sms.create_namespace(name, region)

        # Assert

    @record
    def test_delete_namespace(self):
        # Arrange
        name = self.sb_namespace
        region = 'West US'
        self.sms.create_namespace(name, region)
        self._wait_for_namespace_active(name)

        # Act
        result = self.sms.delete_namespace(name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._namespace_exists(name))

    @record
    def test_delete_namespace_with_non_existing_namespace(self):
        # Arrange
        name = self.sb_namespace

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.sms.delete_namespace(name)

        # Assert

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
