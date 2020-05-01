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

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_PARENT_NAME = "myResourceParent"
        RESOURCE_NAME = "myResource"
        APPLY_UPDATE_NAME = "myApplyUpdate"
        CONFIGURATION_ASSIGNMENT_NAME = "myConfigurationAssignment"
        MAINTENANCE_CONFIGURATION_NAME = "myMaintenanceConfiguration"

        # /MaintenanceConfigurations/put/MaintenanceConfigurations_CreateOrUpdateForResource[put]
        BODY = {
          "location": "westus2",
          "namespace": "Microsoft.Maintenance"
        }
        result = self.mgmt_client.maintenance_configurations.create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, configuration=BODY)

        # /ApplyUpdates/put/ApplyUpdates_CreateOrUpdate[put]
        result = self.mgmt_client.apply_updates.create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, apply_update_name=APPLY_UPDATE_NAME)

        # /ConfigurationAssignments/put/ConfigurationAssignments_CreateOrUpdate[put]
        BODY = {
          "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Maintenance/maintenanceConfigurations/" + MAINTENANCE_CONFIGURATION_NAME + ""
        }
        result = self.mgmt_client.configuration_assignments.create_or_update(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, configuration_assignment_name=CONFIGURATION_ASSIGNMENT_NAME, configuration_assignment=BODY)

        # /ApplyUpdates/put/ApplyUpdates_CreateOrUpdateParent[put]
        result = self.mgmt_client.apply_updates.create_or_update_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME, apply_update_name=APPLY_UPDATE_NAME)

        # /ConfigurationAssignments/put/ConfigurationAssignments_CreateOrUpdateParent[put]
        BODY = {
          "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Maintenance/maintenanceConfigurations/" + MAINTENANCE_CONFIGURATION_NAME + ""
        }
        result = self.mgmt_client.configuration_assignments.create_or_update_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME, configuration_assignment_name=CONFIGURATION_ASSIGNMENT_NAME, configuration_assignment=BODY)

        # /ApplyUpdates/get/ApplyUpdates_GetParent[get]
        result = self.mgmt_client.apply_updates.get_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME, apply_update_name=APPLY_UPDATE_NAME)

        # /ConfigurationAssignments/get/ConfigurationAssignments_ListParent[get]
        result = self.mgmt_client.configuration_assignments.list_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME)

        # /Updates/get/Updates_ListParent[get]
        result = self.mgmt_client.updates.list_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME)

        # /ApplyUpdates/get/ApplyUpdates_Get[get]
        result = self.mgmt_client.apply_updates.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, apply_update_name=APPLY_UPDATE_NAME)

        # /ConfigurationAssignments/get/ConfigurationAssignments_List[get]
        result = self.mgmt_client.configuration_assignments.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /Updates/get/Updates_List[get]
        result = self.mgmt_client.updates.list(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /MaintenanceConfigurations/get/MaintenanceConfigurations_GetForResource[get]
        result = self.mgmt_client.maintenance_configurations.get(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)

        # /MaintenanceConfigurations/get/MaintenanceConfigurations_List[get]
        result = self.mgmt_client.maintenance_configurations.list()

        # /Operations/get/Operations_List[get]
        result = self.mgmt_client.operations.list()

        # /MaintenanceConfigurations/patch/MaintenanceConfigurations_UpdateForResource[patch]
        BODY = {
          "location": "westus2",
          "namespace": "Microsoft.Maintenance"
        }
        result = self.mgmt_client.maintenance_configurations.update_method(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, configuration=BODY)

        # /ConfigurationAssignments/delete/ConfigurationAssignments_DeleteParent[delete]
        result = self.mgmt_client.configuration_assignments.delete_parent(resource_group_name=RESOURCE_GROUP, resource_parent_name=RESOURCE_PARENT_NAME, resource_name=RESOURCE_NAME, configuration_assignment_name=CONFIGURATION_ASSIGNMENT_NAME)

        # /ConfigurationAssignments/delete/ConfigurationAssignments_Delete[delete]
        result = self.mgmt_client.configuration_assignments.delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME, configuration_assignment_name=CONFIGURATION_ASSIGNMENT_NAME)

        # /MaintenanceConfigurations/delete/MaintenanceConfigurations_DeleteForResource[delete]
        result = self.mgmt_client.maintenance_configurations.delete(resource_group_name=RESOURCE_GROUP, resource_name=RESOURCE_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
