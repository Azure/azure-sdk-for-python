# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 27
# Methods Covered : 27
# Examples Total  : 27
# Examples Tested : 27
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   ClassicAdministrators: 1/1
#   GlobalAdministrator: 0/1
#   ProviderOperationsMetadata: 2/2
#   Permissions: 2/2
#   RoleDefinitions: 3/5
#   DenyAssignments: 3/6
#   RoleAssignments: 10/10

import unittest

import azure.mgmt.authorization
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtAuthorization(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        # (UnsupportedApiVersionForRoleDefinitionHasDataActions) Assignments to roles with DataActions and NotDataActions \
        # are not supported on API version '2015-07-01'
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient,
            api_version="2018-01-01-preview"
        )
        self.mgmt_client_180701 = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient,
            api_version="2018-07-01-preview"
        )
        self.mgmt_client_default = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient
        )
        if self.is_live:
            from azure.mgmt.resource import ResourceManagementClient
            self.resource_client = self.create_mgmt_client(
                ResourceManagementClient
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_deny_assignment(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        SCOPE = "subscriptions/{subscriptionId}".format(
            subscriptionId=SUBSCRIPTION_ID
        )        

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_180701.deny_assignments.list()
        # deny_assignment = result.next()
        # DENY_ASSIGNMENT_ID_URL = deny_assignment.id
        # DENY_ASSIGNMENT_ID = deny_assignment.name

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client_180701.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_180701.deny_assignments.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client_180701.deny_assignments.get(scope=SCOPE, deny_assignment_id=DENY_ASSIGNMENT_ID)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client_180701.deny_assignments.get_by_id(deny_assignment_id=DENY_ASSIGNMENT_ID_URL)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_180701.deny_assignments.list_for_scope(scope=SCOPE)

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_role_assignment_by_id(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        SCOPE = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
            subscriptionId=SUBSCRIPTION_ID,
            resourceGroupName=RESOURCE_GROUP
        )        
        ROLE_DEFINITION_NAME = "e078ab98-ef3a-4c9a-aba7-12f5172b45d0"
        ROLE_ASSIGNMENT_NAME = "88888888-7000-0000-0000-000000000003"
        ROLE_ID = SCOPE + "/providers/Microsoft.Authorization/roleAssignments/" + ROLE_ASSIGNMENT_NAME

#--------------------------------------------------------------------------
        # /RoleAssignments/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
            "role_definition_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + ROLE_DEFINITION_NAME,
            "principal_id": self.settings.CLIENT_OID,
        }
        result = self.mgmt_client.role_assignments.create_by_id(role_id=ROLE_ID, parameters=BODY)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.get_by_id(role_id=ROLE_ID)

#--------------------------------------------------------------------------
        # /RoleAssignments/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.delete_by_id(role_id=ROLE_ID)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_list_by_resource(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_NAME = "resourcexxx"
        RESOURCE_GROUP = resource_group.name
        RESOURCE_ID = "/subscriptions/{guid}/resourceGroups/{resourcegroupname}/providers/{resourceprovidernamespace}/{resourcetype}/{resourcename}".format(
            guid=SUBSCRIPTION_ID,
            resourcegroupname=RESOURCE_GROUP,
            resourceprovidernamespace="Microsoft.Compute",
            resourcetype="availabilitySets",
            resourcename=RESOURCE_NAME
        )

        if self.is_live:
            create_result = self.resource_client.resources.begin_create_or_update_by_id(
                RESOURCE_ID,
                parameters={'location': AZURE_LOCATION},
                api_version="2019-07-01"
            )
            result = create_result.result()

#--------------------------------------------------------------------------
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.permissions.list_for_resource(
            resource_group_name=RESOURCE_GROUP,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=RESOURCE_NAME
        )

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(
            resource_group_name=RESOURCE_GROUP,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=RESOURCE_NAME
        )

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_role_assignment(self, **kwargs):
        resource_group = kwargs.pop("resource_group")

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP = resource_group.name
        SCOPE = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
            subscriptionId=SUBSCRIPTION_ID,
            resourceGroupName=RESOURCE_GROUP
        )        
        ROLE_DEFINITION_NAME = "e078ab98-ef3a-4c9a-aba7-12f5172b45d0"
        ROLE_ASSIGNMENT_NAME = "88888888-7000-0000-0000-000000000003"
        RESOURCE_PROVIDER_NAMESPACE = "Microsoft.Compute"

#--------------------------------------------------------------------------
        # /RoleAssignments/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
            "role_definition_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + ROLE_DEFINITION_NAME,
            "principal_id": self.settings.CLIENT_OID,
        }
        result = self.mgmt_client.role_assignments.create(scope=SCOPE, role_assignment_name=ROLE_ASSIGNMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.get(scope=SCOPE, role_assignment_name=ROLE_ASSIGNMENT_NAME)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list()

#--------------------------------------------------------------------------
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.permissions.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ClassicAdministrators/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_default.classic_administrators.list()

#--------------------------------------------------------------------------
        # /GlobalAdministrator/post/GetConfigurations[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client_default.global_administrator.elevate_access()

#--------------------------------------------------------------------------
        # /ProviderOperationsMetadata/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.provider_operations_metadata.get(resource_provider_namespace=RESOURCE_PROVIDER_NAMESPACE)

#--------------------------------------------------------------------------
        # /ProviderOperationsMetadata/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.provider_operations_metadata.list()

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_scope(scope=SCOPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.delete(scope=SCOPE, role_assignment_name=ROLE_ASSIGNMENT_NAME)

    @unittest.skip('hard to test')
    @recorded_by_proxy
    def test_role_definition(self):

        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        SCOPE = "subscriptions/{subscriptionId}".format(
            subscriptionId=SUBSCRIPTION_ID
        )
        # ROLE_DEFINITION_ID = "b24988ac-6180-42a0-ab88-20f7382dd24e"
        ROLE_DEFINITION_ID = "7b266cd7-0bba-4ae2-8423-90ede5e1e898"
        
#--------------------------------------------------------------------------
        # /RoleDefinitions/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
          "role_name": "testRole",
          "type": "CustomRole",
          "description": "Role description",
          "assignable_scopes": [
            # "/"
            "/" + SCOPE
          ],
          "permissions": [
            {
              "not_data_actions": [
                "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/write"
              ],
              "actions": [
                "Microsoft.Compute/*/read",
                "Microsoft.Compute/virtualMachines/start/action",
                "Microsoft.Compute/virtualMachines/restart/action",
                "Microsoft.Network/*/read",
                "Microsoft.Storage/*/read",
                "Microsoft.Authorization/*/read",
                "Microsoft.Resources/subscriptions/resourceGroups/read",
                "Microsoft.Resources/subscriptions/resourceGroups/resources/read",
                "Microsoft.Insights/alertRules/*"
              ],
              "data_actions": [
                "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/*"
              ]
            }
          ]
        }
        # result = self.mgmt_client_default.role_definitions.create_or_update(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID, role_definition=BODY)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_default.role_definitions.get(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        ROLE_DEFINITION_ID_URL = SCOPE + "/providers/Microsoft.Authorization/roleDefinitions/{roleDefinitionId}".format(roleDefinitionId=ROLE_DEFINITION_ID)
        result = self.mgmt_client_default.role_definitions.get_by_id(role_definition_id=ROLE_DEFINITION_ID_URL)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client_default.role_definitions.list(scope=SCOPE)

#--------------------------------------------------------------------------
        # /RoleDefinitions/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client_default.role_definitions.delete(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
