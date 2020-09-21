# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------

from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.hybridcompute import HybridComputeManagementClient
from azure.mgmt.hybridcompute.models import ErrorResponseException

import sys
import logging
logger = logging.getLogger('msrest')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

class HybridComputeTests(AzureMgmtTestCase):
    def setUp(self):
        super(HybridComputeTests, self).setUp()
        self.client = self.create_mgmt_client(HybridComputeManagementClient)

    def test_get(self):
        resource_group_name = 'azure-sdk-test'
        machine_name = 'test'
        machine = self.client.machines.get(
            resource_group_name,
            machine_name
        )
        self.assertEqual(machine.name, machine_name)
        self.assertEqual(machine.location, 'eastus')

    def test_list_by_resource_group(self):
        resource_group_name = 'azure-sdk-test'
        result = list(self.client.machines.list_by_resource_group(resource_group_name))
        self.assertEqual(len(result), 1)

    def test_list_by_subscription(self):
        result = list(self.client.machines.list_by_subscription())
        self.assertEqual(len(result), 1)

    def test_delete(self):
        resource_group_name = 'azure-sdk-test'
        machine_name = 'test'

        machine = self.client.machines.get(
            resource_group_name,
            machine_name
        )
        self.assertIsNotNone(machine)

        self.client.machines.delete(
            resource_group_name,
            machine_name
        )
        with self.assertRaises(ErrorResponseException):
            self.client.machines.get(resource_group_name,machine_name)

