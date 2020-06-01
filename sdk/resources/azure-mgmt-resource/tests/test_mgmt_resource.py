# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource.resources.models
import azure.common.exceptions
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
class MgmtResourceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceTest, self).setUp()
        self.resource_client = self.create_mgmt_client(
            azure.mgmt.resource.ResourceManagementClient
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

    def test_resource_groups(self):
        group_name = "test_mgmt_resource_test_resource_groups457f1050"
        # Create or update
        params_create = azure.mgmt.resource.resources.models.ResourceGroup(
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
        result_list_top = result_list_top.advance_page()
        self.assertEqual(len(result_list_top), 2)

        # Patch
        params_patch = azure.mgmt.resource.resources.models.ResourceGroupPatchable(
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
        template = self.resource_client.resource_groups.export_template(
            group_name,
            ['*']
        )
        # self.assertTrue(hasattr(template, 'template'))

        # Delete
        result_delete = self.resource_client.resource_groups.delete(group_name)
        result_delete.wait()

    @ResourceGroupPreparer()
    def test_resources(self, resource_group, location):

        resource_name = self.get_resource_name("pytestavset")

        resource_exist = self.resource_client.resources.check_existence(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01"
        )
        self.assertFalse(resource_exist)

        create_result = self.resource_client.resources.create_or_update(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01",
            parameters={'location': self.region}
        )
        result = create_result.result()
        self.assertEqual(result.name, resource_name)

        get_result = self.resource_client.resources.get(
            resource_group_name=resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01",
        )
        self.assertEqual(get_result.name, resource_name)

        resources = list(self.resource_client.resources.list(
            filter="name eq '{}'".format(resource_name)
        ))


        self.assertEqual(len(resources), 1)

        # the move always fails, so it needs to be disabled at least for now
        #new_group_name = self.get_resource_name("pynewgroup")
        #new_group = self.resource_client.resource_groups.create_or_update(
        #    new_group_name,
        #    {'location': location},
        #)

        #async_move = self.resource_client.resources.move_resources(
        #    resource_group.name,
        #    [get_result.id],
        #    new_group.id
        #)
        #async_move.wait()

        delete_result = self.resource_client.resources.delete(
            resource_group_name=resource_group.name, # new_group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2019-07-01",
        )
        delete_result.wait()

        #async_delete = self.resource_client.resource_groups.delete(
        #    new_group_name
        #)
        #async_delete.wait()


    @ResourceGroupPreparer()
    def test_deployments_basic(self, resource_group, location):

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestdeployment")

        deployment_exists = self.resource_client.deployments.check_existence(
            resource_group.name,
            deployment_name
        )
        self.assertFalse(deployment_exists)

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
        # Note: when specifying values for parameters, omit the outer elements
        parameters = {"location": { "value": "West US"}}
        deployment_params = azure.mgmt.resource.resources.models.DeploymentProperties(
            mode = azure.mgmt.resource.resources.models.DeploymentMode.incremental,
            template=template,
            parameters=parameters,
        )
        deployment = azure.mgmt.resource.resources.models.Deployment(properties=deployment_params)

        deployment_create_result = self.resource_client.deployments.create_or_update(
            resource_group.name,
            deployment_name,
            deployment,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        deployment_list_result = self.resource_client.deployments.list_by_resource_group(
            resource_group.name,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        self.assertEqual(len(deployment_list_result), 1)
        self.assertEqual(deployment_name, deployment_list_result[0].name)

        deployment_get_result = self.resource_client.deployments.get(
            resource_group.name,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        deployment_operations = list(self.resource_client.deployment_operations.list(
            resource_group.name,
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 1)

        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get(
            resource_group.name,
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.common.exceptions.CloudError) as cm:
            self.resource_client.deployments.cancel(
                resource_group.name,
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Validate
        #validation =self.resource_client.deployments.validate(
        #    resource_group.name,
        #    deployment_name,
        #    {'mode': azure.mgmt.resource.resources.models.DeploymentMode.incremental}
        #)
        #self.assertTrue(hasattr(validation, 'properties'))

        # Export template
        export =self.resource_client.deployments.export_template(
            resource_group.name,
            deployment_name
        )
        self.assertTrue(hasattr(export, 'template'))

        # Delete the template
        async_delete = self.resource_client.deployments.delete(
            resource_group.name,
            deployment_name
        )
        async_delete.wait()

    @ResourceGroupPreparer()
    def test_deployments_linked_template(self, resource_group, location):

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestlinked")
        template = azure.mgmt.resource.resources.models.TemplateLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-availability-set-create-3FDs-20UDs/azuredeploy.json',
        )
        parameters = azure.mgmt.resource.resources.models.ParametersLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-availability-set-create-3FDs-20UDs/azuredeploy.parameters.json',
        )

        deployment_params = azure.mgmt.resource.resources.models.DeploymentProperties(
            mode = azure.mgmt.resource.resources.models.DeploymentMode.incremental,
            template_link=template,
            parameters_link=parameters,
        )
        deployment = azure.mgmt.resource.resources.models.Deployment(properties=deployment_params)

        deployment_create_result = self.resource_client.deployments.create_or_update(
            resource_group.name,
            deployment_name,
            deployment,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        deployment_list_result = self.resource_client.deployments.list_by_resource_group(
            resource_group.name,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        self.assertEqual(len(deployment_list_result), 1)
        self.assertEqual(deployment_name, deployment_list_result[0].name)

        deployment_get_result = self.resource_client.deployments.get(
            resource_group.name,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

    @ResourceGroupPreparer()
    def test_deployments_linked_template_error(self, resource_group, location):

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestlinked")
        template = azure.mgmt.resource.resources.models.TemplateLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-vm-simple-linux/azuredeploy.json',
        )
        parameters = azure.mgmt.resource.resources.models.ParametersLink(
            uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-vm-simple-linux/azuredeploy.parameters.json',
        )

        deployment_params = azure.mgmt.resource.resources.models.DeploymentProperties(
            mode = azure.mgmt.resource.resources.models.DeploymentMode.incremental,
            template_link=template,
            parameters_link=parameters,
        )
        deployment = azure.mgmt.resource.resources.models.Deployment(properties=deployment_params)

        with self.assertRaises(azure.common.exceptions.CloudError) as err:
            self.resource_client.deployments.create_or_update(
                resource_group.name,
                deployment_name,
                deployment,
            )
        cloud_error = err.exception
        self.assertTrue(cloud_error.message)

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


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
