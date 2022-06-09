# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   deployment_scripts: 8/8

import unittest

import azure.core.exceptions
import azure.mgmt.resource
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

class TestMgmtResourceDeploymentScript(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.script_client = self.create_mgmt_client(
            azure.mgmt.resource.DeploymentScriptsClient,
            api_version="2019-10-01-preview"
        )

        if self.is_live:
            from azure.mgmt.msi import ManagedServiceIdentityClient
            self.msi_client = self.create_mgmt_client(
                ManagedServiceIdentityClient
            )

    @RandomNameResourceGroupPreparer()
    @recorded_by_proxy
    def test_deployment_scripts(self, **kwargs):
        resource_group = kwargs.pop("resource_group")
        location = kwargs.pop("location")
        SUBSCRIPTION = self.get_settings_value("SUBSCRIPTION_ID")
        script_name = "scripttest"
        identity_name = "uai"

        # Create identity
        if self.is_live:
            self.msi_client.user_assigned_identities.create_or_update(
                resource_group.name,
                identity_name,
                "westus",
                {"key1": "value1"}
            )

        # Create script
        result = self.script_client.deployment_scripts.begin_create(
            resource_group.name,
            script_name,
            {
                "kind": "AzurePowerShell",
                "location": "westus",
                "identity": {
                    "type": "UserAssigned",
                    "user_assigned_identities": {
                        "/subscriptions/" + SUBSCRIPTION + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.ManagedIdentity/userAssignedIdentities/uai": {}
                    }
                },
                "azPowerShellVersion": "3.0",
                "scriptContent": "Param([string]$Location,[string]$Name) $deploymentScriptOutputs['test'] = 'value' Get-AzResourceGroup -Location $Location -Name $Name",
                "arguments": "-Location 'westus' -Name \"*rg2\"",
                # "supportingScriptUris": [
                # "https://uri1.to.supporting.script",
                # "https://uri2.to.supporting.script"
                # ],
                "retentionInterval": "PT26H",
                "timeout": "PT30M",
                "cleanupPreference": "Always"
            }
        )

        # azure.core.exceptions.HttpResponseError: Operation returned an invalid status 'OK'
        try:
            result.result()
        except azure.core.exceptions.HttpResponseError:
            pass

        # Update script tags
        BODY = {
          'tags': {"key1": "value1"}
        }
        self.script_client.deployment_scripts.update(
            resource_group.name,
            script_name,
            BODY
        )

        # Get script
        self.script_client.deployment_scripts.get(
            resource_group.name,
            script_name
        )

        # List scripts by subscription
        self.script_client.deployment_scripts.list_by_subscription()

        # List scripts by resource group
        self.script_client.deployment_scripts.list_by_resource_group(
            resource_group.name
        )

        # Get script logs default
        self.script_client.deployment_scripts.get_logs_default(
            resource_group.name,
            script_name
        )

        # Get script logs
        self.script_client.deployment_scripts.get_logs(
            resource_group.name,
            script_name
        )

        # Delete script
        self.script_client.deployment_scripts.delete(
            resource_group.name,
            script_name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
