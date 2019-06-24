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
import time
import unittest

from azure.common import AzureHttpError
from azure.servicemanagement import ServiceManagementService
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


class LegacyMgmtStorageTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtStorageTest, self).setUp()

        self.sms = self.create_service_management(ServiceManagementService)

        self.storage_account_name = self.get_resource_name('utstor')

    def tearDown(self):
        if not self.is_playback():
            try:
                self.sms.delete_storage_account(self.storage_account_name)
            except:
                pass

        return super(LegacyMgmtStorageTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_storage_account(self, name):
        result = self.sms.create_storage_account(
            name,
            name + 'description',
            name + 'label',
            None,
            'West US',
            False,
            {'ext1': 'val1', 'ext2': 42})
        self._wait_for_async(result.request_id)

    def _storage_account_exists(self, name):
        try:
            props = self.sms.get_storage_account_properties(name)
            return props is not None
        except:
            return False

    def _wait_for_async(self, request_id):
        # Note that we keep the same ratio of timeout/sleep_interval in
        # live and playback so we end up with same number of loops/requests
        if self.is_playback():
            self.sms.wait_for_operation_status(request_id, timeout=1.2, sleep_interval=0.2)
        else:
            self.sms.wait_for_operation_status(request_id, timeout=30, sleep_interval=5)

    #--Test cases for storage accounts -----------------------------------
    @record
    def test_list_storage_accounts(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)

        # Act
        result = self.sms.list_storage_accounts()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        storage = None
        for temp in result:
            if temp.service_name == self.storage_account_name:
                storage = temp
                break

        self.assertIsNotNone(storage)
        self.assertIsNotNone(storage.service_name)
        self.assertIsNone(storage.storage_service_keys)
        self.assertIsNotNone(storage.storage_service_properties)
        self.assertIsNotNone(storage.storage_service_properties.affinity_group)
        self.assertIsNotNone(storage.storage_service_properties.description)
        self.assertIsNotNone(
            storage.storage_service_properties.geo_primary_region)
        self.assertIsNotNone(
            storage.storage_service_properties.geo_replication_enabled)
        self.assertIsNotNone(
            storage.storage_service_properties.geo_secondary_region)
        self.assertIsNotNone(storage.storage_service_properties.label)
        self.assertIsNotNone(
            storage.storage_service_properties.last_geo_failover_time)
        self.assertIsNotNone(storage.storage_service_properties.location)
        self.assertIsNotNone(storage.storage_service_properties.status)
        self.assertIsNotNone(
            storage.storage_service_properties.status_of_primary)
        self.assertIsNotNone(
            storage.storage_service_properties.status_of_secondary)
        self.assertIsNotNone(storage.storage_service_properties.endpoints)
        self.assertTrue(len(storage.storage_service_properties.endpoints) > 0)
        self.assertIsNotNone(storage.extended_properties)
        self.assertTrue(len(storage.extended_properties) > 0)

    @record
    def test_get_storage_account_properties(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)

        # Act
        result = self.sms.get_storage_account_properties(
            self.storage_account_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.service_name, self.storage_account_name)
        self.assertIsNotNone(result.url)
        self.assertIsNone(result.storage_service_keys)
        self.assertIsNotNone(result.storage_service_properties)
        self.assertIsNotNone(result.storage_service_properties.affinity_group)
        self.assertIsNotNone(result.storage_service_properties.description)
        self.assertIsNotNone(
            result.storage_service_properties.geo_primary_region)
        self.assertIsNotNone(
            result.storage_service_properties.geo_replication_enabled)
        self.assertIsNotNone(
            result.storage_service_properties.geo_secondary_region)
        self.assertIsNotNone(result.storage_service_properties.label)
        self.assertIsNotNone(
            result.storage_service_properties.last_geo_failover_time)
        self.assertIsNotNone(result.storage_service_properties.location)
        self.assertIsNotNone(result.storage_service_properties.status)
        self.assertIsNotNone(
            result.storage_service_properties.status_of_primary)
        self.assertIsNotNone(
            result.storage_service_properties.status_of_secondary)
        self.assertEqual(result.storage_service_properties.account_type, 'Standard_LRS')
        self.assertIsNotNone(result.storage_service_properties.endpoints)
        self.assertTrue(len(result.storage_service_properties.endpoints) > 0)
        self.assertIsNotNone(result.extended_properties)
        self.assertTrue(len(result.extended_properties) > 0)
        self.assertIsNotNone(result.capabilities)
        self.assertTrue(len(result.capabilities) > 0)

    @record
    def test_get_storage_account_keys(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)

        # Act
        result = self.sms.get_storage_account_keys(self.storage_account_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.url)
        self.assertIsNotNone(result.service_name)
        self.assertIsNotNone(result.storage_service_keys.primary)
        self.assertIsNotNone(result.storage_service_keys.secondary)
        self.assertIsNone(result.storage_service_properties)

    @record
    def test_regenerate_storage_account_keys(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)
        previous = self.sms.get_storage_account_keys(self.storage_account_name)

        # Act
        result = self.sms.regenerate_storage_account_keys(
            self.storage_account_name, 'Secondary')

        # Assert
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.url)
        self.assertIsNotNone(result.service_name)
        self.assertIsNotNone(result.storage_service_keys.primary)
        self.assertIsNotNone(result.storage_service_keys.secondary)
        self.assertIsNone(result.storage_service_properties)
        self.assertEqual(result.storage_service_keys.primary,
                         previous.storage_service_keys.primary)
        self.assertNotEqual(result.storage_service_keys.secondary,
                            previous.storage_service_keys.secondary)

    @record
    def test_create_storage_account(self):
        # Arrange
        description = self.storage_account_name + 'description'
        label = self.storage_account_name + 'label'

        # Act
        result = self.sms.create_storage_account(
            self.storage_account_name,
            description,
            label,
            None,
            'West US',
            True,
            {'ext1': 'val1', 'ext2': 42})
        self._wait_for_async(result.request_id)

        # Assert
        self.assertTrue(
            self._storage_account_exists(self.storage_account_name))

    @record
    def test_update_storage_account(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)
        description = self.storage_account_name + 'descriptionupdate'
        label = self.storage_account_name + 'labelupdate'

        # Act
        result = self.sms.update_storage_account(
            self.storage_account_name,
            description,
            label,
            False,
            {'ext1': 'val1update', 'ext2': 53, 'ext3': 'brandnew'})

        # Assert
        self.assertIsNone(result)
        props = self.sms.get_storage_account_properties(
            self.storage_account_name)
        self.assertEqual(
            props.storage_service_properties.description, description)
        self.assertEqual(props.storage_service_properties.label, label)
        self.assertEqual(props.extended_properties['ext1'], 'val1update')
        self.assertEqual(props.extended_properties['ext2'], '53')
        self.assertEqual(props.extended_properties['ext3'], 'brandnew')

    @record
    def test_delete_storage_account(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)

        # Act
        result = self.sms.delete_storage_account(self.storage_account_name)
        self._wait_for_async(result.request_id)

        # Assert
        self.assertFalse(
            self._storage_account_exists(self.storage_account_name))

    @record
    def test_check_storage_account_name_availability_not_available(self):
        # Arrange
        self._create_storage_account(self.storage_account_name)

        # Act
        result = self.sms.check_storage_account_name_availability(
            self.storage_account_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertFalse(result.result)

    @record
    def test_check_storage_account_name_availability_available(self):
        # Arrange

        # Act
        result = self.sms.check_storage_account_name_availability(
            self.storage_account_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(result.result)

    @record
    def test_unicode_create_storage_account_unicode_name(self):
        # Arrange
        self.storage_account_name = self.storage_account_name + u'啊齄丂狛狜'
        description = 'description'
        label = 'label'

        # Act
        with self.assertRaises(AzureHttpError):
            # not supported - queue name must be alphanumeric, lowercase
            result = self.sms.create_storage_account(
                self.storage_account_name,
                description,
                label,
                None,
                'West US',
                True,
                {'ext1': 'val1', 'ext2': 42})
            self._wait_for_async(result.request_id)

        # Assert

    @record
    def test_unicode_create_storage_account_unicode_description_label(self):
        # Arrange
        description = u'啊齄丂狛狜'
        label = u'丂狛狜'

        # Act
        result = self.sms.create_storage_account(
            self.storage_account_name,
            description,
            label,
            None,
            'West US',
            True,
            {'ext1': 'val1', 'ext2': 42})
        self._wait_for_async(result.request_id)

        # Assert
        result = self.sms.get_storage_account_properties(
            self.storage_account_name)
        self.assertEqual(
            result.storage_service_properties.description, description)
        self.assertEqual(result.storage_service_properties.label, label)

    @record
    def test_unicode_create_storage_account_unicode_property_value(self):
        # Arrange
        description = 'description'
        label = 'label'

        # Act
        result = self.sms.create_storage_account(
            self.storage_account_name,
            description,
            label,
            None,
            'West US',
            True,
            {'ext1': u'丂狛狜', 'ext2': 42})
        self._wait_for_async(result.request_id)

        # Assert
        result = self.sms.get_storage_account_properties(
            self.storage_account_name)
        self.assertEqual(
            result.storage_service_properties.description, description)
        self.assertEqual(result.storage_service_properties.label, label)
        self.assertEqual(result.extended_properties['ext1'], u'丂狛狜')

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
