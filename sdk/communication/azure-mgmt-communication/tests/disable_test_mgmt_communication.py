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
    def test_communication_crud(self, resource_group):
        GROUP_NAME = resource_group.name
        resource_name = self.get_resource_name("test-resource-crud")

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

        resource = self.communication_client.communication_service.get(
            GROUP_NAME,
            resource_name
        )
        self.assertEqual(resource.name, resource_name)
        self.assertEqual(resource.provisioning_state, "Succeeded")
        self.assertIsNotNone(resource.immutable_resource_id)
        self.assertEqual(resource.location, COMMUNICATION_SERVICE_LOCATION)
        self.assertEqual(resource.data_location, COMMUNICATION_SERVICE_DATA_LOCATION)
        self.assertIsNone(resource.notification_hub_id)
        self.assertIsNone(resource.tags)

        tags = {"tags": {"tag1": "tag1val", "tag2": "tag2val"} }
        resource = self.communication_client.communication_service.update(
            GROUP_NAME,
            resource_name,
            TaggedResource(**tags)
        )
        self.assertEqual(resource.name, resource_name)
        self.assertEqual(resource.provisioning_state, "Succeeded")
        self.assertIsNotNone(resource.immutable_resource_id)
        self.assertEqual(resource.location, COMMUNICATION_SERVICE_LOCATION)
        self.assertEqual(resource.data_location, COMMUNICATION_SERVICE_DATA_LOCATION)
        self.assertIsNone(resource.notification_hub_id)
        self.assertIsNotNone(resource.tags)
        self.assertEqual(resource.tags["tag1"], "tag1val")
        self.assertEqual(resource.tags["tag2"], "tag2val")

        keys = self.communication_client.communication_service.list_keys(GROUP_NAME, resource_name)
        self.assertIsNotNone(keys.primary_key)
        self.assertIsNotNone(keys.secondary_key)
        self.assertIsNotNone(keys.primary_connection_string)
        self.assertIsNotNone(keys.secondary_connection_string)

        key_type = {"key_type": "Primary"}
        keys_regenerated_primary = self.communication_client.communication_service.regenerate_key(
            GROUP_NAME,
            resource_name,
            RegenerateKeyParameters(**key_type)
        )
        self.assertNotEqual(keys.primary_key, keys_regenerated_primary.primary_key)
        self.assertNotEqual(keys.primary_connection_string, keys_regenerated_primary.primary_connection_string)

        key_type = {"key_type": "Secondary"}
        keys_regenerated_secondary = self.communication_client.communication_service.regenerate_key(
            GROUP_NAME,
            resource_name,
            RegenerateKeyParameters(**key_type)
        )
        self.assertNotEqual(keys.secondary_key, keys_regenerated_secondary.secondary_key)
        self.assertNotEqual(keys.secondary_connection_string, keys_regenerated_secondary.secondary_connection_string)

        # Delete can take a long time to return when running live. Disable polling requirement until we can determine why.
        self.communication_client.communication_service.begin_delete(
            GROUP_NAME,
            resource_name,
            polling = False
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
