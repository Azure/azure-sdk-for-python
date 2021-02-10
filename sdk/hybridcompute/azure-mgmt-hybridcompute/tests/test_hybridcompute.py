# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import unittest

from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.hybridcompute import HybridComputeManagementClient

@unittest.skip("skip test")
class HybridComputeTests(AzureMgmtTestCase):
    def setUp(self):
        super(HybridComputeTests, self).setUp()
        self.client = self.create_mgmt_client(HybridComputeManagementClient)

    def test_get(self):
        resource_group_name = 'azure-sdk-test'
        machine_name = 'TestMachine1'
        machine = self.client.machines.get(
            resource_group_name,
            machine_name
        )
        self.assertEqual(machine.name, machine_name)
        self.assertEqual(machine.location, 'westus2')

    def test_list_by_resource_group(self):
        resource_group_name = 'azure-sdk-test'
        result = list(self.client.machines.list_by_resource_group(resource_group_name))
        self.assertEqual(len(result), 2)

    def test_list_by_subscription(self):
        result = list(self.client.machines.list_by_subscription())
        self.assertEqual(len(result), 1449)

    def test_delete(self):
        resource_group_name = 'hybridrptest'
        machine_name = 'fv-az467iqj4s_e2etest'

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

