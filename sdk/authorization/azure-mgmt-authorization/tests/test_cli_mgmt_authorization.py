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
#   GlobalAdministrator: 1/1
#   ProviderOperationsMetadata: 2/2
#   Permissions: 2/2
#   RoleDefinitions: 5/5
#   DenyAssignments: 6/6
#   RoleAssignments: 10/10

import unittest

import azure.mgmt.authorization
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAuthorizationTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAuthorizationTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.authorization.AuthorizationManagementClient
        )
    

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
