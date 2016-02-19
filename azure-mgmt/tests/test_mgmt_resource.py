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
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

class MgmtResourceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceTest, self).setUp()

    @record
    def test_resource_groups(self):
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
        #self.assertEqual(result_create.status_code, HttpStatusCode.Created)

        result_get = self.resource_client.resource_groups.get(self.group_name)
        #self.assertEqual(result_get.status_code, HttpStatusCode.OK)
        self.assertEqual(result_get.name, self.group_name)
        self.assertEqual(result_get.tags['tag1'], 'value1')

        result_check = self.resource_client.resource_groups.check_existence(
            self.group_name,
        )
        #self.assertEqual(result_check.status_code, HttpStatusCode.NoContent)
        self.assertTrue(result_check)

        result_check = self.resource_client.resource_groups.check_existence(
            'unknowngroup',
        )
        #self.assertEqual(result_check.status_code, HttpStatusCode.NotFound)
        self.assertFalse(result_check)

        result_list = self.resource_client.resource_groups.list()
        #self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

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
        #self.assertEqual(result_patch.status_code, HttpStatusCode.OK)
        self.assertEqual(result_patch.tags['tag1'], 'valueA')
        self.assertEqual(result_patch.tags['tag2'], 'valueB')

        result_delete = self.resource_client.resource_groups.delete(self.group_name)
        #self.assertEqual(result_get.status_code, HttpStatusCode.OK)

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
  ]
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
    def test_provider_locations(self):
        result_get = self.resource_client.providers.get('Microsoft.Web')
        for resource in result_get.resource_types:
            if resource.resource_type == 'sites':
                self.assertIn('West US', resource.locations)

    @record
    def test_providers(self):
        result_list = self.resource_client.providers.list()
        for provider in result_list:
            print(provider.namespace)
            self.resource_client.providers.register(provider.namespace)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
