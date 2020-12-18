# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import pytest

import azure.mgmt.communication
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.communication.models import CommunicationServiceResource
from azure.mgmt.communication.models import KeyType
from azure.mgmt.communication.models import TaggedResource
from azure.mgmt.communication.models import RegenerateKeyParameters

AZURE_LOCATION = "westus"
COMMUNICATION_SERVICE_LOCATION = "global"
COMMUNICATION_SERVICE_DATA_LOCATION = "UnitedStates"
DISABLE_MGMT_TESTS = True
DISABLE_REASON = "Temporary issue causing the tests to fail"

class MgmtCommunicationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtCommunicationTest, self).setUp()
        self.communication_client = self.create_mgmt_client(
            azure.mgmt.communication.CommunicationServiceManagementClient
        )

    @pytest.mark.skipif(DISABLE_MGMT_TESTS, reason=DISABLE_REASON)
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_communication_list_by_subscription(self, resource_group):
        GROUP_NAME = resource_group.name
        resource_name = self.get_resource_name("test-resource-list-by-subscription")

        resource = CommunicationServiceResource(
            location=COMMUNICATION_SERVICE_LOCATION,
            data_location = COMMUNICATION_SERVICE_DATA_LOCATION
        )
        resource = self.communication_client.communication_service.begin_create_or_update(
            GROUP_NAME,
            resource_name,
            resource
        ).result()

        self.assertEqual(resource.name, resource_name)
        self.assertEqual(resource.provisioning_state, "Succeeded")
        self.assertIsNotNone(resource.immutable_resource_id)
        self.assertEqual(resource.location, COMMUNICATION_SERVICE_LOCATION)
        self.assertEqual(resource.data_location, COMMUNICATION_SERVICE_DATA_LOCATION)
        self.assertIsNone(resource.notification_hub_id)
        self.assertIsNone(resource.tags)

        resources = self.communication_client.communication_service.list_by_subscription()
        self.assertIsNotNone(resources)

        # Verify that the resource we just created is in the list
        resource_found = False
        for resource in resources:
            if resource.name == resource_name:
                resource_found = True
        self.assertTrue(resource_found)

    @pytest.mark.skipif(DISABLE_MGMT_TESTS, reason=DISABLE_REASON)
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_communication_list_by_rg(self, resource_group):
        GROUP_NAME = resource_group.name
        resource_name = self.get_resource_name("test-resource-list-by-rg")

        resource = CommunicationServiceResource(
            location=COMMUNICATION_SERVICE_LOCATION,
            data_location = COMMUNICATION_SERVICE_DATA_LOCATION
        )
        resource = self.communication_client.communication_service.begin_create_or_update(
            GROUP_NAME,
            resource_name,
            resource
        ).result()

        self.assertEqual(resource.name, resource_name)
        self.assertEqual(resource.provisioning_state, "Succeeded")
        self.assertIsNotNone(resource.immutable_resource_id)
        self.assertEqual(resource.location, COMMUNICATION_SERVICE_LOCATION)
        self.assertEqual(resource.data_location, COMMUNICATION_SERVICE_DATA_LOCATION)
        self.assertIsNone(resource.notification_hub_id)
        self.assertIsNone(resource.tags)

        resources = self.communication_client.communication_service.list_by_resource_group(GROUP_NAME)
        self.assertIsNotNone(resources)

        # Verify that the resource we just created is in the list
        resource_found = False
        for resource in resources:
            if resource.name == resource_name:
                resource_found = True
        self.assertTrue(resource_found)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
