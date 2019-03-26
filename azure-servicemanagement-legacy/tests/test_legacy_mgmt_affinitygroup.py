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

from azure.servicemanagement import (
    AffinityGroups,
    AffinityGroup,
    Locations,
    ServiceManagementService,
)
from testutils.common_recordingtestcase import (
    TestMode,
    record,
)
from tests.legacy_mgmt_testcase import LegacyMgmtTestCase


class LegacyMgmtAffinityGroupTest(LegacyMgmtTestCase):

    def setUp(self):
        super(LegacyMgmtAffinityGroupTest, self).setUp()

        self.sms = self.create_service_management(ServiceManagementService)

        self.affinity_group_name = self.get_resource_name('utaffgrp')
        self.hosted_service_name = None
        self.storage_account_name = None

    def tearDown(self):
        if not self.is_playback():
            try:
                if self.hosted_service_name is not None:
                    self.sms.delete_hosted_service(self.hosted_service_name)
            except:
                pass

            try:
                if self.storage_account_name is not None:
                    self.sms.delete_storage_account(self.storage_account_name)
            except:
                pass

            try:
                self.sms.delete_affinity_group(self.affinity_group_name)
            except:
                pass

        return super(LegacyMgmtAffinityGroupTest, self).tearDown()

    #--Helpers-----------------------------------------------------------------
    def _create_affinity_group(self, name):
        result = self.sms.create_affinity_group(
            name, 'tstmgmtaffgrp', 'West US', 'tstmgmt affinity group')
        self.assertIsNone(result)

    def _affinity_group_exists(self, name):
        try:
            props = self.sms.get_affinity_group_properties(name)
            return props is not None
        except:
            return False

    #--Test cases for affinity groups ------------------------------------
    @record
    def test_list_affinity_groups(self):
        # Arrange
        self._create_affinity_group(self.affinity_group_name)

        # Act
        result = self.sms.list_affinity_groups()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

        group = None
        for temp in result:
            if temp.name == self.affinity_group_name:
                group = temp
                break

        self.assertIsNotNone(group)
        self.assertIsNotNone(group.name)
        self.assertIsNotNone(group.label)
        self.assertIsNotNone(group.description)
        self.assertIsNotNone(group.location)
        self.assertIsNotNone(group.capabilities)
        self.assertTrue(len(group.capabilities) > 0)

    @record
    def test_get_affinity_group_properties(self):
        # Arrange
        self.hosted_service_name = self.get_resource_name('utsvc')
        self.storage_account_name = self.get_resource_name('utstorage')
        self._create_affinity_group(self.affinity_group_name)
        self.sms.create_hosted_service(
            self.hosted_service_name,
            'affgrptestlabel',
            'affgrptestdesc',
            None,
            self.affinity_group_name)
        self.sms.create_storage_account(
            self.storage_account_name,
            self.storage_account_name + 'desc',
            self.storage_account_name + 'label',
            self.affinity_group_name)

        # Act
        result = self.sms.get_affinity_group_properties(
            self.affinity_group_name)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.name, self.affinity_group_name)
        self.assertIsNotNone(result.label)
        self.assertIsNotNone(result.description)
        self.assertIsNotNone(result.location)
        self.assertIsNotNone(result.hosted_services[0])
        self.assertEqual(
            result.hosted_services[0].service_name, self.hosted_service_name)
        self.assertEqual(
            result.hosted_services[0].hosted_service_properties.affinity_group,
            self.affinity_group_name)
        # not sure why azure does not return any storage service
        self.assertTrue(len(result.capabilities) > 0)

    @record
    def test_create_affinity_group(self):
        # Arrange
        label = 'tstmgmtaffgrp'
        description = 'tstmgmt affinity group'

        # Act
        result = self.sms.create_affinity_group(
            self.affinity_group_name, label, 'West US', description)

        # Assert
        self.assertIsNone(result)
        self.assertTrue(self._affinity_group_exists(self.affinity_group_name))

    @record
    def test_update_affinity_group(self):
        # Arrange
        self._create_affinity_group(self.affinity_group_name)
        label = 'tstlabelupdate'
        description = 'testmgmt affinity group update'

        # Act
        result = self.sms.update_affinity_group(
            self.affinity_group_name, label, description)

        # Assert
        self.assertIsNone(result)
        props = self.sms.get_affinity_group_properties(
            self.affinity_group_name)
        self.assertEqual(props.label, label)
        self.assertEqual(props.description, description)

    @record
    def test_delete_affinity_group(self):
        # Arrange
        self._create_affinity_group(self.affinity_group_name)

        # Act
        result = self.sms.delete_affinity_group(self.affinity_group_name)

        # Assert
        self.assertIsNone(result)
        self.assertFalse(self._affinity_group_exists(self.affinity_group_name))

    #--Test cases for locations ------------------------------------------
    @record
    def test_list_locations(self):
        # Arrange

        # Act
        result = self.sms.list_locations()

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertIsNotNone(result[0].name)
        self.assertIsNotNone(result[0].display_name)
        self.assertIsNotNone(result[0].available_services)
        self.assertTrue(len(result[0].available_services) > 0)
        self.assertTrue(len(result[0].compute_capabilities.web_worker_role_sizes) > 0)
        self.assertTrue(len(result[0].compute_capabilities.virtual_machines_role_sizes) > 0)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
