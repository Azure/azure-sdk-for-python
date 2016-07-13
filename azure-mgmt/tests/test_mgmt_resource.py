# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource.resources
import azure.common.exceptions
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

class MgmtResourceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceTest, self).setUp()

    @record
    def test_tag_operations(self):
        tag_name = 'tag1'
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
        self.assertEqual(len(tags), 1)
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

    @record
    def test_resource_groups(self):
        # Create or update
        params_create = azure.mgmt.resource.resources.models.ResourceGroup(
            location=self.region,
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.resource_client.resource_groups.create_or_update(
            self.group_name,
            params_create,
        )

        # Get
        result_get = self.resource_client.resource_groups.get(self.group_name)
        self.assertEqual(result_get.name, self.group_name)
        self.assertEqual(result_get.tags['tag1'], 'value1')

        # Check existence
        result_check = self.resource_client.resource_groups.check_existence(
            self.group_name,
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
        result_list_top = result_list_top.next()
        self.assertEqual(len(result_list_top), 2)

        # Patch
        params_patch = azure.mgmt.resource.resources.models.ResourceGroup(
            location=self.region,
            tags={
                'tag1': 'valueA',
                'tag2': 'valueB',
            },
        )
        result_patch = self.resource_client.resource_groups.patch(
            self.group_name,
            params_patch,
        )
        self.assertEqual(result_patch.tags['tag1'], 'valueA')
        self.assertEqual(result_patch.tags['tag2'], 'valueB')

        # List resources
        resources = list(self.resource_client.resource_groups.list_resources(
            self.group_name
        ))

        # Export template
        template = self.resource_client.resource_groups.export_template(
            self.group_name,
            ['*']
        )
        self.assertTrue(hasattr(template, 'template'))

        # Delete
        result_delete = self.resource_client.resource_groups.delete(self.group_name)
        result_delete.wait()

    @record
    def test_resources(self):
        self.create_resource_group()

        resource_name = self.get_resource_name("pytestavset")

        create_params = azure.mgmt.resource.resources.models.GenericResource(
            location = 'West US',
        )
        #create_params.properties = {}

        create_result = self.resource_client.resources.create_or_update(
            resource_group_name=self.group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2015-05-01-preview",
            parameters=create_params
        )
        #self.assertEqual(create_result.status_code, HttpStatusCode.OK)

        get_result = self.resource_client.resources.get(
            resource_group_name=self.group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2015-05-01-preview",
        )
        #self.assertEqual(get_result.status_code, HttpStatusCode.OK)
        self.assertEqual(get_result.name, resource_name)

        delete_result = self.resource_client.resources.delete(
            resource_group_name=self.group_name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name=resource_name,
            api_version="2015-05-01-preview",
        )
        #self.assertEqual(delete_result.status_code, HttpStatusCode.OK)

    @record
    def test_deployments(self):
        self.create_resource_group()

        # for more sample templates, see https://github.com/Azure/azure-quickstart-templates
        deployment_name = self.get_resource_name("pytestdeployment")

        deployment_exists = self.resource_client.deployments.check_existence(
            self.group_name,
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
      "apiVersion": "2015-05-01-preview",
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

        deployment_create_result = self.resource_client.deployments.create_or_update(
            self.group_name,
            deployment_name,
            deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        deployment_list_result = self.resource_client.deployments.list(
            self.group_name,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        self.assertEqual(len(deployment_list_result), 1)
        self.assertEqual(deployment_name, deployment_list_result[0].name)

        deployment_get_result = self.resource_client.deployments.get(
            self.group_name,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

        deployment_operations = list(self.resource_client.deployment_operations.list(
            self.group_name,
            deployment_name
        ))
        self.assertGreater(len(deployment_operations), 1)

        deployment_operation = deployment_operations[0]
        deployment_operation_get = self.resource_client.deployment_operations.get(
            self.group_name,
            deployment_name,
            deployment_operation.operation_id
        )
        self.assertEqual(deployment_operation_get.operation_id, deployment_operation.operation_id)

        # Should throw, since the deployment is done => cannot be cancelled
        with self.assertRaises(azure.common.exceptions.CloudError) as cm:
            self.resource_client.deployments.cancel(
                self.group_name,
                deployment_name
            )
        self.assertIn('cannot be cancelled', cm.exception.message)

        # Delete the template
        async_delete = self.resource_client.deployments.delete(
            self.group_name,
            deployment_name
        )
        async_delete.wait()

    @record
    def test_deployments_linked_template(self):
        self.create_resource_group()

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

        deployment_create_result = self.resource_client.deployments.create_or_update(
            self.group_name,
            deployment_name,
            deployment_params,
        )
        deployment_create_result = deployment_create_result.result()
        self.assertEqual(deployment_name, deployment_create_result.name)

        deployment_list_result = self.resource_client.deployments.list(
            self.group_name,
            None,
        )
        deployment_list_result = list(deployment_list_result)
        self.assertEqual(len(deployment_list_result), 1)
        self.assertEqual(deployment_name, deployment_list_result[0].name)

        deployment_get_result = self.resource_client.deployments.get(
            self.group_name,
            deployment_name,
        )
        self.assertEqual(deployment_name, deployment_get_result.name)

    @record
    def test_deployments_linked_template_error(self):
        self.create_resource_group()

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

        deployment_create_result = self.resource_client.deployments.create_or_update(
            self.group_name,
            deployment_name,
            deployment_params,
        )   
        with self.assertRaises(azure.common.exceptions.CloudError) as err:
            deployment_create_result = deployment_create_result.result()
        cloud_error = err.exception
        self.assertTrue(cloud_error.message)        


    @record
    def test_provider_locations(self):
        result_get = self.resource_client.providers.get('Microsoft.Web')
        for resource in result_get.resource_types:
            if resource.resource_type == 'sites':
                self.assertIn('West US', resource.locations)

    @record
    def test_providers(self):
        self.resource_client.providers.unregister('Microsoft.Batch')
        self.resource_client.providers.get('Microsoft.Batch')

        result_list = self.resource_client.providers.list()
        for provider in result_list:
            self.resource_client.providers.register(provider.namespace)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
