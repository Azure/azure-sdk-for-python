# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 18
# Methods Covered : 18
# Examples Total  : 18
# Examples Tested : 18
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.maintenance
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMaintenanceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMaintenanceTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.maintenance.MaintenanceManagementClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_maintenance(self, resource_group):
        raise unittest.SkipTest("Skipping WebApp test")
        SERVICE_NAME = "myapimrndxyz"

        # MaintenanceConfigurations_CreateOrUpdateForResource[put]
        BODY = {
          "location": "westus2",
          "properties": {
            "namespace": "Microsoft.Maintenance"
          }
        }
        result = self.mgmt_client.maintenance_configurations.create_or_update(resource_group.name, MAINTENANCE_CONFIGURATION_NAME, BODY)

        # ApplyUpdates_CreateOrUpdate[put]
        BODY = {}
        result = self.mgmt_client.apply_updates.create_or_update(resource_group.name, {RESOURCE_TYPE}_NAME, APPLY_UPDATE_NAME, BODY)

        # ConfigurationAssignments_CreateOrUpdate[put]
        BODY = {
          "properties": {
            "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Maintenance/maintenanceConfigurations/" + MAINTENANCE_CONFIGURATION_NAME + ""
          }
        }
        result = self.mgmt_client.configuration_assignments.create_or_update(resource_group.name, {RESOURCE_TYPE}_NAME, CONFIGURATION_ASSIGNMENT_NAME, BODY)

        # ApplyUpdates_CreateOrUpdateParent[put]
        BODY = {}
        result = self.mgmt_client.apply_updates.create_or_update_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, APPLY_UPDATE_NAME, BODY)

        # ConfigurationAssignments_CreateOrUpdateParent[put]
        BODY = {
          "properties": {
            "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Maintenance/maintenanceConfigurations/" + MAINTENANCE_CONFIGURATION_NAME + ""
          }
        }
        result = self.mgmt_client.configuration_assignments.create_or_update_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, CONFIGURATION_ASSIGNMENT_NAME, BODY)

        # ApplyUpdates_GetParent[get]
        result = self.mgmt_client.apply_updates.get_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, APPLY_UPDATE_NAME)

        # ConfigurationAssignments_ListParent[get]
        result = self.mgmt_client.configuration_assignments.list_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, )

        # Updates_ListParent[get]
        result = self.mgmt_client.updates.list_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, )

        # ApplyUpdates_Get[get]
        result = self.mgmt_client.apply_updates.get(resource_group.name, {RESOURCE_TYPE}_NAME, APPLY_UPDATE_NAME)

        # ConfigurationAssignments_List[get]
        result = self.mgmt_client.configuration_assignments.list(resource_group.name, {RESOURCE_TYPE}_NAME, )

        # Updates_List[get]
        result = self.mgmt_client.updates.list(resource_group.name, {RESOURCE_TYPE}_NAME, )

        # MaintenanceConfigurations_GetForResource[get]
        result = self.mgmt_client.maintenance_configurations.get(resource_group.name, MAINTENANCE_CONFIGURATION_NAME)

        # MaintenanceConfigurations_List[get]
        result = self.mgmt_client.maintenance_configurations.list()

        # Operations_List[get]
        result = self.mgmt_client.operations.list()

        # MaintenanceConfigurations_UpdateForResource[patch]
        BODY = {
          "location": "westus2",
          "properties": {
            "namespace": "Microsoft.Maintenance"
          }
        }
        result = self.mgmt_client.maintenance_configurations.update_method(resource_group.name, MAINTENANCE_CONFIGURATION_NAME, BODY)

        # ConfigurationAssignments_DeleteParent[delete]
        result = self.mgmt_client.configuration_assignments.delete_parent(resource_group.name, {RESOURCE_PARENT_TYPE}_NAME, {RESOURCE_TYPE}_NAME, CONFIGURATION_ASSIGNMENT_NAME)

        # ConfigurationAssignments_Delete[delete]
        result = self.mgmt_client.configuration_assignments.delete(resource_group.name, {RESOURCE_TYPE}_NAME, CONFIGURATION_ASSIGNMENT_NAME)

        # MaintenanceConfigurations_DeleteForResource[delete]
        result = self.mgmt_client.maintenance_configurations.delete(resource_group.name, MAINTENANCE_CONFIGURATION_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
