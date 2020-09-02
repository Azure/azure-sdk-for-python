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
#   Permissions: 1/2
#   RoleDefinitions: 0/5
#   DenyAssignments: 3/6
#   RoleAssignments: 9/10

import unittest

import azure.mgmt.authorization
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAuthorizationTest(AzureMgmtTestCase):

    def setUp(self):
        # (UnsupportedApiVersionForRoleDefinitionHasDataActions) Assignments to roles with DataActions and NotDataActions \
        # are not supported on API version '2015-07-01'
        super(MgmtAuthorizationTest, self).setUp()
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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_deny_assignment(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_role_assignment_by_id(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
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
    def test_role_assignment(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
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
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.permissions.list_for_resource(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_provider_namespace=)

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
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.permissions.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

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


    # @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    # def test_role_definition(self, resource_group):
    @unittest.skip("(RoleDefinitionLimitExceeded) Role definition limit exceeded. No more role definitions can be created.")
    def test_role_definition(self):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        # RESOURCE_GROUP = resource_group.name
        # SCOPE = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
        #     subscriptionId=SUBSCRIPTION_ID,
        #     resourceGroupName=RESOURCE_GROUP
        # )
        SCOPE = "subscriptions/{subscriptionId}".format(
            subscriptionId=SUBSCRIPTION_ID
        )
        ROLE_DEFINITION_ID = "b24988ac-6180-42a0-ab88-20f7382dd24e"
        
#--------------------------------------------------------------------------
        # /RoleDefinitions/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
          "role_name": "testRole",
          "type": "CustomRole",
          "description": "Role description",
          "assignable_scopes": [
            SCOPE
          ],
          "permissions": [
            {
              "actions": [
                "*/read"
              ],
              "notActions": []
            }
          ]
        }
        result = self.mgmt_client.role_definitions.create_or_update(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID, role_definition=BODY)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.get(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        ROLE_DEFINITION_ID_URL = SCOPE + "/providers/Microsoft.Authorization/roleDefinitions/{roleDefinitionId}".format(roleDefinitionId=ROLE_DEFINITION_ID)
        result = self.mgmt_client.role_definitions.get_by_id(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID_URL)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.list(scope=SCOPE)

#--------------------------------------------------------------------------
        # /RoleDefinitions/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.delete(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_authorization(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        RESOURCE_PROVIDER_NAMESPACE = "myResourceProvider"
        RESOURCE_TYPE = "myResourceType"
        # {RESOURCE_NAME}_NAME = "myResource"
        # MICROSOFT.AUTHORIZATION_NAME = "myMicrosoftAuthorization"
        ROLE_DEFINITION_ID = "myRoleDefinitionId"
        ROLE_DEFINITION_NAME = "myRoleDefinition"
        DENY_ASSIGNMENT_ID = "myDenyAssignmentId"
        ROLE_ASSIGNMENT_NAME = "myRoleAssignment"

        SCOPE = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
            subscriptionId=SUBSCRIPTION_ID,
            resourceGroupName=RESOURCE_GROUP
        )

#--------------------------------------------------------------------------
        # /RoleAssignments/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
          "condition": "@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase 'foo_storage_container'",
          "condition_version": "1.0",
          "description": "Grants UserFoo role assignment bar in scope baz",
          "role_definition_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + ROLE_DEFINITION_NAME,
          "principal_id": "d93a38bc-d029-4160-bfb0-fbda779ac214",
          "principal_type": "User",
          "can_delegate": False
        }
        result = self.mgmt_client.role_assignments.create(scope=SCOPE, role_assignment_name=ROLE_ASSIGNMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /RoleDefinitions/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.role_definitions.create_or_update(scope=SCOPE, role_definition_id=ROLE_DEFINITION_ID, role_definition=BODY)

#--------------------------------------------------------------------------
        # /RoleAssignments/put/GetConfigurations[put]
#--------------------------------------------------------------------------
        BODY = {
          "condition": "@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase 'foo_storage_container'",
          "condition_version": "1.0",
          "description": "Grants UserFoo role assignment bar in scope baz",
          "role_definition_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Authorization/roleDefinitions/" + ROLE_DEFINITION_NAME,
          "principal_id": "d93a38bc-d029-4160-bfb0-fbda779ac214",
          "principal_type": "User",
          "can_delegate": False
        }
        # result = self.mgmt_client.role_assignments.create(role_assignment_name=ROLE_ASSIGNMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.permissions.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /Permissions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.permissions.list_for_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ClassicAdministrators/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.classic_administrators.list()

#--------------------------------------------------------------------------
        # /ProviderOperationsMetadata/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.provider_operations_metadata.get(resource_provider_namespace=RESOURCE_PROVIDER_NAMESPACE)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.get(role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.get(role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /ProviderOperationsMetadata/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.provider_operations_metadata.get(resource_provider_namespace=RESOURCE_PROVIDER_NAMESPACE)

#--------------------------------------------------------------------------
        # /DenyAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deny_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /RoleDefinitions/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.get(role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /RoleAssignments/get/GetConfigurations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.list_for_resource(resource_group_name=RESOURCE_GROUP, resource_type=RESOURCE_TYPE)

#--------------------------------------------------------------------------
        # /GlobalAdministrator/post/GetConfigurations[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.global_administrator.elevate_access()

#--------------------------------------------------------------------------
        # /RoleAssignments/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.delete(role_assignment_name=ROLE_ASSIGNMENT_NAME)

#--------------------------------------------------------------------------
        # /RoleDefinitions/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_definitions.delete(role_definition_id=ROLE_DEFINITION_ID)

#--------------------------------------------------------------------------
        # /RoleAssignments/delete/GetConfigurations[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.role_assignments.delete(role_assignment_name=ROLE_ASSIGNMENT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
