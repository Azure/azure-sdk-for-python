# coding: utf-8
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import unittest
import time
import json
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.managednetwork import ManagedNetworkManagementClient
import azure.mgmt.managednetwork.models

class MgmtManagedNetworkTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtManagedNetworkTest, self).setUp()
        self.client = self.create_mgmt_client(ManagedNetworkManagementClient)
    
    def test_put_get_managednetwork(self):
        resource_group_name = "MNCRG"
        managednetwork_Name = "PythonSDKTestMNC"
        scope = azure.mgmt.managednetwork.models.Scope()
        sub = {}
        subscriptions = []
        sub["id"] = "subscriptions/18ba8369-92e4-4d70-8b1e-937660bde798"
        subscriptions.append(sub)
        scope.subscriptions = subscriptions
        managedNetwork = azure.mgmt.managednetwork.models.ManagedNetwork()
        managedNetwork.scope = scope
        managedNetwork.location = "West US 2"
        self.client.managed_networks.create_or_update(managedNetwork, "MNCRG", managednetwork_Name)
        managednetworkResult = self.client.managed_networks.get(resource_group_name, managednetwork_Name)
        self.assertEqual(managednetworkResult.name, managednetwork_Name)
        self.assertEqual(managednetworkResult.location, "West US 2")
        self.assertEqual(managednetworkResult.scope.subscriptions[0].id, sub["id"])
        self.assertEqual(len(managednetworkResult.scope.subscriptions), 1)

    def test_delete_managednetwork(self):
        resource_group_name = "MNCRG"
        managednetwork_Name = "PythonSDKTestMNC_Delete"
        scope = azure.mgmt.managednetwork.models.Scope()
        sub = {}
        subscriptions = []
        sub["id"] = "subscriptions/18ba8369-92e4-4d70-8b1e-937660bde798"
        subscriptions.append(sub)
        scope.subscriptions = subscriptions
        managedNetwork = azure.mgmt.managednetwork.models.ManagedNetwork()
        managedNetwork.scope = scope
        managedNetwork.location = "West US 2"
        self.client.managed_networks.create_or_update(managedNetwork, resource_group_name, managednetwork_Name)
        self.client.managed_networks.delete(resource_group_name, managednetwork_Name)
        
    def test_managed_network_group_and_policy(self):
        resource_group_name = "MNC-Portal"
        managednetwork_Name = "TestMNCforPolicy"
        managed_network_group_name = "TestGroup"
        managed_network_policy_name = "TestPolicy"
        location = "West US 2"
        virtual_networks = []
        vnet1 = {}
        vnet2 = {}
        vnetHub = {}
        vnet1["id"] = "subscriptions/18ba8369-92e4-4d70-8b1e-937660bde798/resourceGroups/MNC-Portal/providers/Microsoft.Network/virtualNetworks/Spoke11"
        vnet2["id"] = "subscriptions/18ba8369-92e4-4d70-8b1e-937660bde798/resourceGroups/MNC-Portal/providers/Microsoft.Network/virtualNetworks/Spoke12"
        vnetHub["id"] = "subscriptions/18ba8369-92e4-4d70-8b1e-937660bde798/resourceGroups/MNC-Portal/providers/Microsoft.Network/virtualNetworks/Hub"
        virtual_networks.append(vnet1)
        virtual_networks.append(vnet2)
        virtual_networks.append(vnetHub)
        scope = azure.mgmt.managednetwork.models.Scope()
        scope.virtual_networks = virtual_networks
        managedNetwork = azure.mgmt.managednetwork.models.ManagedNetwork()
        managedNetwork.scope = scope
        managedNetwork.location = location
        self.client.managed_networks.create_or_update(managedNetwork, resource_group_name, managednetwork_Name)
        managed_network_group = azure.mgmt.managednetwork.models.ManagedNetworkGroup()
        managed_network_group.location = location
        
        group_vnetList = []
        group_vnetList.append(vnet1)
        group_vnetList.append(vnet2)
        managed_network_group.virtual_networks = group_vnetList
        self.client.managed_network_groups.create_or_update(managed_network_group, resource_group_name, managednetwork_Name, managed_network_group_name)
        managednetworkgroupResult =  self.client.managed_network_groups.get(resource_group_name, managednetwork_Name, managed_network_group_name);
        self.assertEqual(managednetworkgroupResult.name, managed_network_group_name)
        self.assertEqual(managednetworkgroupResult.location, location)
        self.assertEqual(len(managednetworkgroupResult.virtual_networks), 2)
        
        spokes = []
        spoke = {}
        spoke["id"] = managednetworkgroupResult.id
        spokes.append(spoke) 
        properties = azure.mgmt.managednetwork.models.ManagedNetworkPeeringPolicyProperties(
            type = "HubAndSpokeTopology",
            hub = vnetHub,
            spokes = spokes
        )

        self.client.managed_network_peering_policies.create_or_update(resource_group_name, managednetwork_Name, managed_network_policy_name, location, properties)
        
        managednetworkpolicyResult = self.client.managed_network_peering_policies.get(resource_group_name, managednetwork_Name, managed_network_policy_name)
        self.assertEqual(managednetworkpolicyResult.name, managed_network_policy_name)
        self.assertEqual(managednetworkpolicyResult.location, location)
        self.assertEqual(managednetworkpolicyResult.properties.type, '1')
        self.assertEqual(managednetworkpolicyResult.properties.hub.id, vnetHub["id"])
        self.assertEqual(managednetworkpolicyResult.properties.spokes[0].id, managednetworkgroupResult.id)
        self.assertEqual(len(managednetworkpolicyResult.properties.spokes), 1)

if __name__ == '__main__':
    unittest.main()