# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# coverd ops:
#   tags: 9/9
#   resource_groups: 7/7
#   resources: 14/14
#   deployments: 34/43  TODO: tenant is forbidden
#   deployment_operations: 8/10 TODO: tenant is forbidden
#   providers: 6/6
#   operations: 1/1


import unittest

# import azure.mgmt.managementgroups
import azure.mgmt.resource
import azure.mgmt.resource.resources.v2019_07_01

from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

template = {
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {
        "type": "string",
        "allowedValues": [
            "East US",
            "West US",
            "West Europe",
            "East Asia",
            "South East Asia"
        ],
        "metadata": {
            "description": "Location to deploy to"
        }
        }
    },
    "resources": [
        {
        "type": "Microsoft.Compute/availabilitySets",
        "name": "availabilitySet1",
        "apiVersion": "2019-07-01",
        "location": "[parameters('location')]",
        "properties": {}
        }
    ],
    "outputs": {
        "myparameter": {
        "type": "object",
        "value": "[reference('Microsoft.Compute/availabilitySets/availabilitySet1')]"
        }
    }
}

class MgmtResourceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceTest, self).setUp()
        from azure.mgmt.resource import ResourceManagementClient
        self.resource_client = self.create_mgmt_client(
            ResourceManagementClient
        )

        from azure.mgmt.resource.resources.v2019_07_01 import ResourceManagementClient
        self.resource_client_v07 = self.create_mgmt_client(
            ResourceManagementClient
        )

        if self.is_live:
            # special client
            import azure.mgmt.managementgroups
            self.mgmtgroup_client = azure.mgmt.managementgroups.ManagementGroupsAPI(
                credentials=self.settings.get_credentials()
            )

    def test_tag_operations(self):
        tag_name = 'tagxyz'
        tag_value = 'value1'

        # Create or update
        tag = self.resource_client.tags.create_or_update(
            tag_name
        )
        self.assertEqual(tag.tag_name, tag_name)

        # Create or update value
        tag = self.resource_client.tags.create_or_update_value(
            tag_name,
            tag_value
        )
        self.assertEqual(tag.tag_value, tag_value)

        # List
        tags = list(self.resource_client.tags.list())
        self.assertGreater(len(tags), 0)
        self.assertTrue(all(hasattr(v, 'tag_name') for v in tags))

        # Delete value
        self.resource_client.tags.delete_value(
            tag_name,
            tag_value
        )

        # Delete tag
        self.resource_client.tags.delete(
            tag_name
        )

        # Create or update at scope
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        SCOPE = "subscriptions/" + SUBSCRIPTION_ID
        BODY = {
          "properties": {
            "tags": {
              "tagKey1": "tagValue1",
              "tagKey2": "tagValue2"
            }
          }
        }
        tag = self.resource_client.tags.create_or_update_at_scope(
            SCOPE,
            BODY
        )

        # Get at scope
        tag = self.resource_client.tags.get_at_scope(
            SCOPE
        )

        # TODO: need example file
        # Update at scope
        BODY = {
          "operation": "Delete",
          "properties": {
            "tags": {
              "tagKey1": "tagValue1"
            }
          }
        }
        tag = self.resource_client.tags.update_at_scope(
            SCOPE,
            BODY
        )

        # TODO: need example file
        # Delete at scope
        self.resource_client.tags.delete_at_scope(
            SCOPE
        )

    def test_resource_groups(self):
        group_name = "test_mgmt_resource_test_resource_groups457f1050"
        # Create or update
        from azure.mgmt.resource.resources.v2019_10_01 import models as models1001
        params_create = models1001.ResourceGroup(
            location=self.region,
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.resource_client.resource_groups.create_or_update(
            group_name,
            params_create,
        )

        # Get
        result_get = self.resource_client.resource_groups.get(group_name)
        self.assertEqual(result_get.name, group_name)
        self.assertEqual(result_get.tags['tag1'], 'value1')

        # Check existence
        result_check = self.resource_client.resource_groups.check_existence(
            group_name,
        )
        self.assertTrue(result_check)

        result_check = self.resource_client.resource_groups.check_existence(
            'unknowngroup',
        )
        self.assertFalse(result_check)

        # List
        result_list = self.resource_client.resource_groups.list()
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        result_list_top = self.resource_client.resource_groups.list(top=2)
        # result_list_top = result_list_top.advance_page()
        # self.assertEqual(len(result_list_top), 2)

        # Patch
        params_patch = models1001.ResourceGroupPatchable(
            tags={
                'tag1': 'valueA',
                'tag2': 'valueB',
            },
        )
        result_patch = self.resource_client.resource_groups.update(
            group_name,
            params_patch,
        )
        self.assertEqual(result_patch.tags['tag1'], 'valueA')
        self.assertEqual(result_patch.tags['tag2'], 'valueB')

        # List resources
        resources = list(self.resource_client.resources.list_by_resource_group(
            group_name
        ))

        # Export template
        BODY = {
          'resources': ['*']
        }
        template = self.resource_client.resource_groups.begin_export_template(
            group_name,
            BODY
        )
        template.result()
        # self.assertTrue(hasattr(template, 'template'))

        # Delete
        result_delete = self.resource_client.resource_groups.begin_delete(group_name)
        result_delete.wait()

    @RandomNameResourceGroupPreparer()
    def test_resources(self, resource_group, location):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        resource_name = self.get_resource_name("pytestavset")
        resource_name_2 = self.get_resource_name("pytestavset123")

        resource_exist = self.resource_client.resources.check_existence(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-10-01"
        )
        self.assertFalse(resource_exist)

        resource_id = "/subscriptions/{guid}/resourceGroups/{resourcegroupname}/providers/{resourceprovidernamespace}/{resourcetype}/{resourcename}".format(
            guid=SUBSCRIPTION_ID,
            resourcegroupname=resource_group.name,
            resourceprovidernamespace="Microsoft.Compute",
            resourcetype="availabilitySets",
            resourcename=resource_name_2
        )
        resource_exist = self.resource_client.resources.check_existence_by_id(
            resource_id,
            api_version="2019-10-01"
        )

        create_result = self.resource_client.resources.begin_create_or_update_by_id(
            resource_id,
            parameters={'location': self.region},
            api_version="2019-07-01"
        )
        result = create_result.result()

        create_result = self.resource_client.resources.begin_create_or_update(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            parameters={'location': self.region},
            api_version="2019-07-01"
        )
        result = create_result.result()
        self.assertEqual(result.name, resource_name)

        get_result = self.resource_client.resources.get(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01"
        )
        self.assertEqual(get_result.name, resource_name)

        get_result = self.resource_client.resources.get_by_id(
            resource_id,
            api_version="2019-07-01"
        )

        resources = list(self.resource_client.resources.list(
            filter="name eq '{}'".format(resource_name)
        ))
        self.assertEqual(len(resources), 1)

        # List resources by group
        resources = self.resource_client.resources.list_by_resource_group(
            resource_group.name
        )

        # the move always fails, so it needs to be disabled at least for now
        new_group_name = self.get_resource_name("pynewgroup")
        new_group = self.resource_client.resource_groups.create_or_update(
           new_group_name,
           {'location': location},
        )

        async_move = self.resource_client.resources.begin_validate_move_resources(
           resource_group.name,
           {
             'resources': [get_result.id],
             'target_resource_group': new_group.id
           }
        )
        async_move.result()

        async_move = self.resource_client.resources.begin_move_resources(
           resource_group.name,
           {                                                                                                                                                                                                             'resources': [get_result.id],                                                                                                                                                                               'target_resource_group': new_group.id                                                                                                                                                                     }
        )
        async_move.result()

        new_resource_id = "/subscriptions/{guid}/resourceGroups/{resourcegroupname}/providers/{resourceprovidernamespace}/{resourcetype}/{resourcename}".format(
            guid=SUBSCRIPTION_ID,
            resourcegroupname=new_group_name,
            resourceprovidernamespace="Microsoft.Compute",
            resourcetype="availabilitySets",
            resourcename=resource_name_2
        )

        # TODO: azure.core.exceptions.ServiceResponseError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response',))
        update_result = self.resource_client.resources.begin_update(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            # parameters={'properties': {"platform_fault_domain_count": 2}},
            parameters={'tags': {"tag1": "value1"}},
            api_version="2019-07-01"
        )
        result = update_result.result()

        update_result = self.resource_client.resources.begin_update_by_id(
            new_resource_id,
            # parameters={'properties': {"platform_fault_domain_count": 2}},
            parameters={'tags': {"tag1": "value1"}},
            api_version="2019-07-01"
        )
        result = update_result.result()

        delete_result = self.resource_client.resources.begin_delete(
            resource_group_name=resource_group.name, # new_group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01"
        )
        delete_result.wait()

        result = self.resource_client.resources.begin_delete_by_id(
            new_resource_id,
            api_version="2019-07-01"
        )
        result = result.result()

        async_delete = self.resource_client.resource_groups.begin_delete(
           new_group_name
        )
        async_delete.wait()

    @RandomNameResourceGroupPreparer()
    def test_deployments_basic(self, resource_group, location):
        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestdeployment")

        # Check deployment existence
        deployment_exists = self.resource_client.deployments.check_existence(
            resource_group.name,
            deployment_name
        )
        # self.assertFalse(deployment_exists)

        # Note: when specifying values for parameters, omit the outer elements
        parameters = {"location": { "value": "West US"}}
        deployment_params = { 
          "mode": "Incremental",
          "template": template,
          "parameters": parameters
        }

        # TODO:azure.core.exceptions.HttpResponseError: (AuthorizationFailed) 
        # Calculate teplate hash
        # result = self.resource_client.deployments.calculate_template_hash(template)

        # Create deployment
        deployment_create_result = self.resource_client.deployments.begin_create_or_update(
            resource_group.name,
            deployment_name,
            {"properties": deployment_params},
            # deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        # List deployments by resource
        deployment_list_result = self.resource_client.deployments.list_by_resource_group(
            resource_group.name,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        # self.assertEqual(len(deployment_list_result), 1)
        # self.assertEqual(deployment_name, deployment_list_result[0].name)

        # Get deployment
        deployment_get_result = self.resource_client.deployments.get(
            resource_group.name,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        # What if
        result = self.resource_client.deployments.begin_what_if(
            resource_group.name,
            deployment_name,
            {
              "properties": {
                "mode": "Incremental",
                "template": template
              }
            },
        )
        result = result.result()

        # List deployment operations
        deployment_operations = list(self.resource_client.deployment_operations.list(
            resource_group.name,
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 1)

        # Get deployment operations
        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get(
            resource_group.name,
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.core.exceptions.ResourceExistsError) as cm:
            self.resource_client.deployments.cancel(
                resource_group.name,
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        validation =self.resource_client.deployments.begin_validate(
           resource_group.name,
           deployment_name,
           {"properties": deployment_params}
        )
        validation = validation.result()
        self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template(
            resource_group.name,
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.begin_delete(
            resource_group.name,
            deployment_name
        )
        async_delete.wait()

    @RandomNameResourceGroupPreparer()
    def test_deployments_at_scope(self, resource_group, location):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        SCOPE = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
            subscriptionId=SUBSCRIPTION_ID,
            resourceGroupName=resource_group.name
        )

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestdeployment")

        # Check deployment existence
        deployment_exists = self.resource_client.deployments.check_existence_at_scope(
            SCOPE,
            deployment_name
        )
        # # self.assertFalse(deployment_exists)
        
        # Note: when specifying values for parameters, omit the outer elements
        parameters = {"location": { "value": "West US"}}
        deployment_params = { 
          "mode": "Incremental",
          "template": template,
          "parameters": parameters
        }

        # Create deployment
        deployment_create_result = self.resource_client.deployments.begin_create_or_update_at_scope(
            SCOPE,
            deployment_name,
            {"properties": deployment_params},
            # deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        # List deployments at scope
        deployment_list_result = self.resource_client.deployments.list_at_scope(
            SCOPE,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        # self.assertEqual(len(deployment_list_result), 1)
        # self.assertEqual(deployment_name, deployment_list_result[0].name)

        # Get deployment
        deployment_get_result = self.resource_client.deployments.get_at_scope(
            SCOPE,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        # List deployment operations
        deployment_operations = list(self.resource_client.deployment_operations.list_at_scope(
            SCOPE,
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 1)

        # Get deployment operations
        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get_at_scope(
            SCOPE,
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.core.exceptions.ResourceExistsError) as cm:
            self.resource_client.deployments.cancel_at_scope(
                SCOPE,
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        result =self.resource_client.deployments.begin_validate_at_scope(
            SCOPE,
           deployment_name,
           {"properties": deployment_params}
        )
        validation = result.result()
        self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template_at_scope(
            SCOPE,
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.begin_delete_at_scope(
            SCOPE,
            deployment_name
        )
        async_delete.wait()

    @unittest.skip("(InvalidAuthenticationToken)")
    def test_deployments_at_management_group(self):
        # create management group use track 1 version
        group_id = "20000000-0001-0000-0000-000000000123456"
        
        if self.is_live:
            result = self.mgmtgroup_client.management_groups.create_or_update(
                group_id,
                {
                "name": group_id,
                }
            )
            result = result.result()

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestlinked")

        # Check deployment existence
        deployment_exists = self.resource_client.deployments.check_existence_at_management_group_scope(
            group_id,
            deployment_name
        )
        # [ZIM] tis doesn't work for some reason
        # self.assertFalse(deployment_exists)

        from azure.mgmt.resource.resources.v2019_10_01 import models as models1001

        template = models1001.TemplateLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )
        parameters = models1001.ParametersLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )

        deployment_params = { 
          "mode": "Incremental",
          "template_link": template,
          "parameters_link": parameters
        } 

        # Create deployment
        deployment_create_result = self.resource_client.deployments.begin_create_or_update_at_management_group_scope(
            group_id,
            deployment_name,
            {"location": "West US", "properties": deployment_params},
            # deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        # List deployments at scope
        deployment_list_result = self.resource_client.deployments.list_at_management_group_scope(
            group_id,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        ##  self.assertEqual(len(deployment_list_result), 1)
        self.assertEqual(deployment_name, deployment_list_result[0].name)

        # Get deployment
        deployment_get_result = self.resource_client.deployments.get_at_management_group_scope(
            group_id,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        # List deployment operations
        deployment_operations = list(self.resource_client.deployment_operations.list_at_management_group_scope(
            group_id,
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 0)

        # Get deployment operations
        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get_at_management_group_scope(
            group_id,
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.core.exceptions.ResourceExistsError) as cm:
            self.resource_client.deployments.cancel_at_management_group_scope(
                group_id,
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        result =self.resource_client.deployments.begin_validate_at_management_group_scope(
            group_id,
            deployment_name,
            {"location": "West US", "properties": deployment_params}
        )
        validation = result.result()
        self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template_at_management_group_scope(
            group_id,
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.begin_delete_at_management_group_scope(
            group_id,
            deployment_name
        )
        async_delete.wait()

        if self.is_live:
            # delete management group with track 1 version
            result = self.mgmtgroup_client.management_groups.delete(group_id)
            result = result.result()
    
    def test_deployments_at_subscription(self):
        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestlinked")

        # Check deployment existence
        deployment_exists = self.resource_client.deployments.check_existence_at_subscription_scope(
            deployment_name
        )
        # self.assertFalse(deployment_exists)
        from azure.mgmt.resource.resources.v2019_10_01 import models as models1001

        template = models1001.TemplateLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )
        parameters = models1001.ParametersLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )

        deployment_params = { 
          'mode': 'Incremental',
          'template_link': {
            'uri': 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
          },
          'parameters_link': {
            'uri': 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
          }
        }

        # Create deployment
        deployment_create_result = self.resource_client.deployments.begin_create_or_update_at_subscription_scope(
            deployment_name,
            {"location": "West US", "properties": deployment_params},
            # deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        # List deployments at subscription
        deployment_list_result = self.resource_client.deployments.list_at_subscription_scope(
            # None,
        )
        deployment_list_result = list(deployment_list_result)
        # self.assertEqual(len(deployment_list_result), 1)
        # self.assertEqual(deployment_name, deployment_list_result[0].name)

        # Get deployment
        deployment_get_result = self.resource_client.deployments.get_at_subscription_scope(
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        # What if
        result = self.resource_client.deployments.begin_what_if_at_subscription_scope(
            deployment_name,
            {"location": "West US", "properties": deployment_params}
        )
        result = result.result()

        # List deployment operations
        deployment_operations = list(self.resource_client.deployment_operations.list_at_subscription_scope(
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 0)

        # Get deployment operations
        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get_at_subscription_scope(
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.core.exceptions.ResourceExistsError) as cm:
            self.resource_client.deployments.cancel_at_subscription_scope(
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        result =self.resource_client.deployments.begin_validate_at_subscription_scope(
            deployment_name,
            {"location": "West US", "properties": deployment_params}
        )
        validation = result.result()
        self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template_at_subscription_scope(
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.begin_delete_at_subscription_scope(
            deployment_name
        )
        async_delete.wait()

    @unittest.skip("forbidden")
    def test_deployments_at_tenant(self):

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestlinked")

        # Check deployment existence
        deployment_exists = self.resource_client.deployments.check_existence_at_tenant_scope(
            deployment_name
        )
        # this test always fails
        # self.assertFalse(deployment_exists)

        template = azure.mgmt.resource.resources.v2019_10_01.models.TemplateLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )
        parameters = azure.mgmt.resource.resources.v2019_10_01.models.ParametersLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/100-blank-template/azuredeploy.json'
        )

        # deployment_params = azure.mgmt.resource.resources.v2019_10_01.models.DeploymentProperties(
        #    mode = azure.mgmt.resource.resources.v2019_10_01.models.DeploymentMode.incremental,
        #    template_link=template,
        #    parameters_link=parameters,
        #)

        # Create deployment
        deployment_create_result = self.resource_client.deployments.begin_create_or_update_at_tenant_scope(
            deployment_name,
            {"location": "West US", "properties": deployment_params},
            # deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        # List deployments at subscription
        deployment_list_result = self.resource_client.deployments.list_at_tenant_scope(
            None,
        )
        deployment_list_result = list(deployment_list_result)
        # self.assertEqual(len(deployment_list_result), 1)
        # self.assertEqual(deployment_name, deployment_list_result[0].name)

        # Get deployment
        deployment_get_result = self.resource_client.deployments.get_at_tenant_scope(
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        # List deployment operations
        deployment_operations = list(self.resource_client.deployment_operations.list_at_tenant_scope(
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 1)

        # Get deployment operations
        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get_at_tenant_scope(
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.core.exceptions.ResourceExistsError) as cm:
            self.resource_client.deployments.cancel_at_tenant_scope(
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        validation =self.resource_client.deployments.validate_at_tenant_scope(
            deployment_name,
            {"properties": deployment_params}
        )
        self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template_at_tenant_scope(
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.begin_delete_at_tenant_scope(
            deployment_name
        )
        async_delete.wait()

    def test_provider_locations(self):
        result_get = self.resource_client.providers.get('Microsoft.Web')
        for resource in result_get.resource_types:
            if resource.resource_type == 'sites':
                self.assertIn('West US', resource.locations)

    def test_provider_registration(self):
        self.resource_client.providers.unregister('Microsoft.Search')
        self.resource_client.providers.get('Microsoft.Search')
        self.resource_client.providers.register('Microsoft.Search')

    def test_providers(self):
        result_list = self.resource_client.providers.list()
        for provider in result_list:
            break
    
    def test_provider_tenant(self):
        self.resource_client.providers.get_at_tenant_scope("Microsoft.Web")
        self.resource_client.providers.list_at_tenant_scope()

    def test_operations(self):
        self.resource_client.operations.list()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
