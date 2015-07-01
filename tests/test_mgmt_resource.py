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

import azure.mgmt.resource
from azure.common import AzureException
from common_recordingtestcase import record
from mgmt_testcase import HttpStatusCode, AzureMgmtTestCase

class MgmtResourceTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceTest, self).setUp()

    @record
    def test_resource_groups(self):
        params_create = azure.mgmt.resource.ResourceGroup(
            location=self.region,
            tags={
                'tag1': 'value1',
            },
        )
        result_create = self.resource_client.resource_groups.create_or_update(
            self.group_name,
            params_create,
        )
        self.assertEqual(result_create.status_code, HttpStatusCode.Created)

        result_get = self.resource_client.resource_groups.get(self.group_name)
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)
        self.assertEqual(result_get.resource_group.name, self.group_name)
        self.assertEqual(result_get.resource_group.tags['tag1'], 'value1')

        result_check = self.resource_client.resource_groups.check_existence(
            self.group_name,
        )
        self.assertEqual(result_check.status_code, HttpStatusCode.NoContent)
        self.assertTrue(result_check.exists)

        result_check = self.resource_client.resource_groups.check_existence(
            'unknowngroup',
        )
        self.assertEqual(result_check.status_code, HttpStatusCode.NotFound)
        self.assertFalse(result_check.exists)

        params_list = azure.mgmt.resource.ResourceGroupListParameters()
        result_list = self.resource_client.resource_groups.list(params_list)
        self.assertEqual(result_list.status_code, HttpStatusCode.OK)
        self.assertGreater(len(result_list.resource_groups), 0)

        #TODO: get this to work
        #params_patch = azure.mgmt.resource.ResourceGroup()
        #params_patch.location = self.region
        #params_patch.tags['tag1'] = 'value1'
        #params_patch.tags['tag2'] = 'value2'
        #result_patch = self.resource_client.resource_groups.patch(
        #    self.group_name,
        #    params_patch,
        #)

        result_delete = self.resource_client.resource_groups.delete(self.group_name)
        self.assertEqual(result_get.status_code, HttpStatusCode.OK)

    @unittest.skip('missing model classes')
    @record
    def test_resources(self):
        self.create_resource_group()

        #TODO: error: ResourceIdentity doesn't exist!
        resource_identity = azure.mgmt.resource.ResourceIdentity();
        resource_identity.resource_name = self.group_name + "website1"
        resource_identity.resource_provider_api_version = "2014-04-01"
        resource_identity.resource_provider_namespace = "Microsoft.Web"
        resource_identity.resource_type = "sites"

        basic_resource = azure.mgmt.resource.GenericResource()
        basic_resource.location = group_create_parameter.location
        basic_resource.properties =  '{"name":"' + resource_identity.resource_name + '","siteMode": "Standard","computeMode":"Shared"}'

        self.resource_client.resources.create_or_update(self.group_name, resource_identity, basic_resource)

        self.resource_client.resource_groups.get(self.group_name)
        self.resource_client.resource_groups.delete(self.group_name);

    @unittest.skip('not ready')
    @record
    def test_deployments(self):
        self.create_resource_group()

        deployment_name = "pytestdeployment"

        deploy_parameter = azure.mgmt.resource.Deployment()
        deploy_parameter.mode = azure.mgmt.resource.DeploymentMode.incremental
        deploy_parameter.parameters = '{"siteName": {"value": "mctest0101"},"hostingPlanName": {"value": "mctest0101"},"siteMode": {"value": "Limited"},"computeMode": {"value": "Shared"},"siteLocation": {"value": "North Europe"},"sku": {"value": "Free"},"workerSize": {"value": "0"}}'

        template_uri = azure.mgmt.resource.TemplateLink()
        template_uri.uri = 'https://testtemplates.blob.core.windows.net/templates/good-website.js'
        deploy_parameter.template_link = template_uri

        result = self.resource_client.deployments.create_or_update(self.group_name, deployment_name, deploy_parameter);

        deployment_list_result = self.resource_client.deployments.list(self.group_name, None)
        deployment_get_result = self.resource_client.deployments.get(self.group_name, deployment_name)

        self.resource_client.resource_groups.delete(self.group_name);

    @record
    def test_providers(self):
        result_list = self.resource_client.providers.list(
            azure.mgmt.resource.ProviderListParameters(),
        )
        for provider in result_list.providers:
            print(provider.namespace)
            self.resource_client.providers.register(provider.namespace)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
