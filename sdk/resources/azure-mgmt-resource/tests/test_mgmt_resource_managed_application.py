# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   applications: 10/10
#   application_definitions: 7/7

import unittest

import azure.mgmt.resource
# import azure.mgmt.managementgroups
import azure.mgmt.resource.resources.v2019_10_01
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

@unittest.skip("Hard to test, skip them")
class MgmtResourceLinksTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceLinksTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.resource.ApplicationClient
        )

        self.resource_client = self.create_mgmt_client(
            azure.mgmt.resource.ResourceManagementClient
        )

        if self.is_live:
            # special client
            from azure.mgmt.managementgroups import ManagementGroupsAPI
            self.mgmtgroup_client = ManagementGroupsAPI(
                credentials=self.settings.get_credentials()
            )

    @RandomNameResourceGroupPreparer()
    def test_application_by_id(self, resource_group, location):
        application_name = "applicationtest"
        app_def_name = "applicationdefinition"
        group_name = "test_group_name_xyz"
        application_definition_id = "/subscriptions/{guid}/resourceGroups/{resource_group_name}/providers/Microsoft.Solutions/applicationDefinitions/{applicationDefinition_name}".format(
            guid=self.settings.SUBSCRIPTION_ID,
            resource_group_name=resource_group.name,
            applicationDefinition_name=app_def_name
        )
        application_id = "/subscriptions/{guid}/resourceGroups/{resource_group_name}/providers/Microsoft.Solutions/applications/{application_name}".format(
            guid=self.settings.SUBSCRIPTION_ID,
            resource_group_name=resource_group.name,
            application_name=application_name
        )

        params_create = azure.mgmt.resource.resources.v2019_10_01.models.ResourceGroup(
            location="east US",
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.resource_client.resource_groups.create_or_update(
            group_name,
            params_create,
        )

        # # create management group use track 1 version
        # group_id = "20000000-0001-0000-0000-000000000123"
        # mgmtgroup = self.mgmtgroup_client.management_groups.create_or_update(
        #     group_id,
        #     {
        #       "name": group_id,
        #     }
        # )
        # mgmtgroup = mgmtgroup.result()

        # Create application definition by id
        BODY = {
            "lockLevel": "None",
            "displayName": "myManagedApplicationDef",
            "description": "myManagedApplicationDef description",
            "authorizations": [
            # {
            #     "principalId": "validprincipalguid",
            #     "roleDefinitionId": "validroleguid"
            # }
            ],
            "packageFileUri": "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-managed-application-with-linked-templates/artifacts/ManagedAppZip/pkg.zip",
            "location": "East US"
        }
        app_definition = self.mgmt_client.application_definitions.begin_create_or_update_by_id(
            application_definition_id,
            BODY
        )
        app_definition = app_definition.result()

        # Get application definition by id
        self.mgmt_client.application_definitions.get_by_id(
            application_definition_id
        )

        # Create application by id
        BODY = {
            "applicationDefinitionId": app_definition.id,
            "managedResourceGroupId": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/myManagedRG" + group_name,
            "location": "East US",
            "kind": "ServiceCatalog"
        }
        result = self.mgmt_client.applications.begin_create_or_update_by_id(
            application_id,
            BODY
        )
        result = result.result()

        # Get application by id
        self.mgmt_client.applications.get_by_id(
            application_id
        )

        # Update application by id
        BODY = {
            "managedResourceGroupId": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/myManagedRG" + group_name,
            "kind": "ServiceCatalog"
        }
        try:
            self.mgmt_client.applications.update_by_id(
                application_id,
                BODY
            )
        except HttpResponseError as e:
            if not str(e).startswith("Operation returned an invalid status 'Accepted'"):
                raise e

        # Delete application by id
        result = self.mgmt_client.applications.begin_delete_by_id(
            application_id
        )
        result = result.result()

        # Delete application definition by id
        result = self.mgmt_client.application_definitions.begin_delete_by_id(
            application_definition_id
        )
        result = result.result()

        # Delete
        result_delete = self.resource_client.resource_groups.begin_delete(group_name)
        result_delete.wait()

    @RandomNameResourceGroupPreparer()
    def test_application(self, resource_group, location):
        app_def_name = "applicationdefinition"
        application_name = "applicationtest"
        group_name = "test_group_name_xyz"

        params_create = azure.mgmt.resource.resources.v2019_10_01.models.ResourceGroup(
            location="east US",
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.resource_client.resource_groups.create_or_update(
            group_name,
            params_create,
        )

        # Create application definition
        BODY = {
            "lockLevel": "None",
            "displayName": "myManagedApplicationDef",
            "description": "myManagedApplicationDef description",
            "authorizations": [
            # {
            #     "principalId": "validprincipalguid",
            #     "roleDefinitionId": "validroleguid"
            # }
            ],
            "packageFileUri": "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-managed-application-with-linked-templates/artifacts/ManagedAppZip/pkg.zip",
            "location": "East US"
        }
        app_definition  = self.mgmt_client.application_definitions.begin_create_or_update(
            resource_group.name,
            app_def_name,
            BODY
        )
        app_definition = app_definition.result()

        # get application definition
        self.mgmt_client.application_definitions.get(
            resource_group.name,
            app_def_name
        )

        # list application definition by resource group
        self.mgmt_client.application_definitions.list_by_resource_group(
            resource_group.name
        )

        # Create application
        BODY = {
            "applicationDefinitionId": app_definition.id,
            "managedResourceGroupId": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/myManagedRG" + group_name,
            "location": "East US",
            "kind": "ServiceCatalog"
        }
        result = self.mgmt_client.applications.begin_create_or_update(
            resource_group.name,
            application_name,
            BODY
        )
        result.wait()

        # Get application
        self.mgmt_client.applications.get(
            resource_group.name,
            application_name
        )

        # Update application
        BODY = {
            "managedResourceGroupId": "/subscriptions/" + self.settings.SUBSCRIPTION_ID + "/resourceGroups/myManagedRG" + group_name,
            "kind": "ServiceCatalog"
        }
        try:
            self.mgmt_client.applications.update(
                resource_group.name,
                application_name,
                BODY
            )
        except HttpResponseError as e:
            if not str(e).startswith("Operation returned an invalid status 'Accepted'"):
                raise e

        # List application by resorce group
        self.mgmt_client.applications.list_by_resource_group(
            resource_group.name
        )

        # List application by subscription
        self.mgmt_client.applications.list_by_subscription()

        # Delete application
        result = self.mgmt_client.applications.begin_delete(
            resource_group.name,
            application_name
        )
        result = result.result()

        # delete app defninition
        result = self.mgmt_client.application_definitions.begin_delete(
            resource_group.name,
            app_def_name
        )
        result.wait(0)

        # Delete
        result_delete = self.resource_client.resource_groups.begin_delete(group_name)
        result_delete.wait()
        

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
