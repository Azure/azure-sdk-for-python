# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import azure.mgmt.resource.deploymentscripts.models
from devtools_testutils import AzureMgmtTestCase

class MgmtResourceDeploymentScriptsTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceDeploymentScriptsTest, self).setUp()
        
        self.deploymentscripts_client = self.create_basic_client(
            azure.mgmt.resource.DeploymentScriptsClient,
            subscription_id="00000000-0000-0000-0000-000000000000"
        )

    def test_create_deploymentscript(self):
        
        async_operation = \
            self.deploymentscripts_client.deployment_scripts.create(
                resource_group_name="python_sdk_test",
                script_name="inlineSampleScript01",
                deployment_script={
                    'location': 'West US2',
                    'kind': 'AzureCLI',
                    'cleanup_preference': 'OnExpiration',
                    'script_content': 'echo foo',
                    'arguments': 'foo bar',
                    'force_update_tag': '123456',
                    'az_cli_version': '2.0.80',
                    'retention_interval': 'P1D',
                    'identity': {
                        'type': 'UserAssigned',
                        'user_assigned_identities': {
                            'subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/python_sdk_test/providers/Microsoft.ManagedIdentity/userAssignedIdentities/python_test_sdk_msi': {}
                        }
                    }
                }
            )
        # Wait for the resource provisioning to complete
        async_operation.wait()
        result = \
            async_operation.result()

    def test_get_deploymentscript(self):
        self.deploymentscripts_client.deployment_scripts.get(
            resource_group_name="python_sdk_test",
            script_name="bashSampleScript"
        )

    def test_delete_deploymentscript(self):
        self.deploymentscripts_client.deployment_scripts.delete(
            resource_group_name="python_sdk_test",
            script_name="inlineSampleScript"
        )

    def test_list_by_subscription_deploymentscript(self):
        self.deploymentscripts_client.deployment_scripts.list_by_subscription()

    def test_get_logs_deploymentscript(self):
        self.deploymentscripts_client.deployment_scripts.get_logs(
            resource_group_name="python_sdk_test",
            script_name="bashSampleScript"
        )

    def test_list_by_resource_group_deploymentscript(self):
        self.deploymentscripts_client.deployment_scripts.list_by_resource_group(
            resource_group_name="python_sdk_test")