# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import time
import unittest

import azure.mgmt.monitor.aio
import azure.mgmt.monitor.models
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

from _aio_testcase import AzureMgmtAsyncTestCase


AZURE_LOCATION = 'eastus'

class MgmtMonitorClientTest(AzureMgmtAsyncTestCase):

    def setUp(self):
        super(MgmtMonitorClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_aio_client(
            azure.mgmt.monitor.aio.MonitorManagementClient
        )

        if self.is_live:
            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
            )
            from azure.mgmt.eventhub import EventHubManagementClient
            self.eventhub_client = self.create_mgmt_client(
                azure.mgmt.eventhub.EventHubManagementClient
            )
            from azure.mgmt.loganalytics import LogAnalyticsManagementClient
            self.loganalytics_client = self.create_mgmt_client(
                LogAnalyticsManagementClient
            )
            from azure.mgmt.compute import ComputeManagementClient
            self.vm_client = self.create_mgmt_client(
                ComputeManagementClient
            )
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )
            from azure.mgmt.logic import LogicManagementClient
            self.logic_client = self.create_mgmt_client(
                LogicManagementClient
            )

    def create_workflow(self, group_name, location, workflow_name):
        workflow = self.logic_client.workflows.create_or_update(
            group_name,
            workflow_name,
            azure.mgmt.logic.models.Workflow(
                location=location,
                definition={ 
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "triggers": {},
                    "actions": {},
                    "outputs": {}
                }
            )
        )
        return workflow

    # use track 1 version
    def create_storage_account(self,
        group_name,
        location,
        storage_name
    ):
        from azure.mgmt.storage import models
        params_create = models.StorageAccountCreateParameters(
            sku=models.Sku(name=models.SkuName.standard_lrs),
            kind=models.Kind.storage,
            location=location
        )
        result_create = self.storage_client.storage_accounts.create(
            group_name,
            storage_name,
            params_create,
        )
        account = result_create.result()
        return account.id

    # use eventhub track 1 verison
    def create_event_hub_authorization_rule(
        self,
        group_name,
        location,
        name_space,
        eventhub,
        authorization_rule,
        storage_account_id
    ):
        # NamespaceCreate[put]
        BODY = {
          "sku": {
            "name": "Standard",
            "tier": "Standard"
          },
          "location": location,
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
        result = self.eventhub_client.namespaces.create_or_update(group_name, name_space, BODY)
        result.result()

        # NameSpaceAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send",
            "Manage"
          ]
        }
        result = self.eventhub_client.namespaces.create_or_update_authorization_rule(group_name, name_space, authorization_rule, BODY["rights"])

        # EventHubCreate[put]
        BODY = {
          "message_retention_in_days": "4",
          "partition_count": "4",
          "status": "Active",
          "capture_description": {
            "enabled": True,
            "encoding": "Avro",
            "interval_in_seconds": "120",
            "size_limit_in_bytes": "10485763",
            "destination": {
              "name": "EventHubArchive.AzureBlockBlob",
              "storage_account_resource_id": storage_account_id,
              "blob_container": "container",
              "archive_name_format": "{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}"
            }
          }
        }
        result = self.eventhub_client.event_hubs.create_or_update(group_name, name_space, eventhub, BODY)

        # EventHubAuthorizationRuleCreate[put]
        BODY = {
          "rights": [
            "Listen",
            "Send",
            "Manage"
          ]
        }
        result = self.eventhub_client.event_hubs.create_or_update_authorization_rule(group_name, name_space, eventhub, authorization_rule, BODY["rights"])

    # use track 1 version
    def create_workspace(
        self, 
        group_name,
        location,
        workspace_name
    ):
        BODY = {
          "sku": {
            "name": "PerNode"
          },
          "retention_in_days": 30,
          "location": location,
          "tags": {
            "tag1": "val1"
          }
        }
        result = self.loganalytics_client.workspaces.create_or_update(
            group_name,
            workspace_name,
            BODY
        )
        return result.result()

    # use track 1 version
    def create_virtual_network(self, group_name, location, network_name, subnet_name):
      
      azure_operation_poller = self.network_client.virtual_networks.create_or_update(
          group_name,
          network_name,
          {
              'location': location,
              'address_space': {
                  'address_prefixes': ['10.0.0.0/16']
              }
          },
      )
      result_create = azure_operation_poller.result()
      async_subnet_creation = self.network_client.subnets.create_or_update(
          group_name,
          network_name,
          subnet_name,
          {'address_prefix': '10.0.0.0/24'}
      )
      subnet_info = async_subnet_creation.result()
      return subnet_info
   
    # use track 1 version
    def create_network_interface(self, group_name, location, nic_name, subnet):

        async_nic_creation = self.network_client.network_interfaces.create_or_update(
            group_name,
            nic_name,
            {
                'location': location,
                'ip_configurations': [{
                    'name': 'MyIpConfig',
                    'subnet': {
                        'id': subnet.id
                    }
                }]
            }
        )
        nic_info = async_nic_creation.result()

        return nic_info.id

        subnet = self.create_virtual_network(group_name, location, network_name, subnet_name)
        NIC_ID = self.create_network_interface(group_name, location, interface_name, subnet)

        # Create a vm with empty data disks.[put]
        BODY = {
          "location": "eastus",
          "hardware_profile": {
            "vm_size": "Standard_D2_v2"
          },
          "storage_profile": {
            "image_reference": {
              "sku": "2016-Datacenter",
              "publisher": "MicrosoftWindowsServer",
              "version": "latest",
              "offer": "WindowsServer"
            },
            "os_disk": {
              "caching": "ReadWrite",
              "managed_disk": {
                "storage_account_type": "Standard_LRS"
              },
              "name": "myVMosdisk",
              "create_option": "FromImage"
            },
            "data_disks": [
              {
                "disk_size_gb": "1023",
                "create_option": "Empty",
                "lun": "0"
              },
              {
                "disk_size_gb": "1023",
                "create_option": "Empty",
                "lun": "1"
              }
            ]
          },
          "os_profile": {
            "admin_username": "testuser",
            "computer_name": "myVM",
            "admin_password": "Aa1!zyx_",
            "windows_configuration": {
              "enable_automatic_updates": True  # need automatic update for reimage
            }
          },
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NIC_ID + "",
                "id": NIC_ID,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.vm_client.virtual_machines.create_or_update(group_name, vm_name, BODY)
        return result.result()

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_monitor_diagnostic_settings(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        # RESOURCE_URI = "subscriptions/{}/resourcegroups/{}".format(SUBSCRIPTION_ID, RESOURCE_GROUP)
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storageaccountx")
        NAMESPACE_NAME = self.get_resource_name("namespacex")
        EVENTHUB_NAME = self.get_resource_name("eventhubx")
        AUTHORIZATIONRULE_NAME = self.get_resource_name("authorizationrulex")
        INSIGHT_NAME = self.get_resource_name("insightx")
        WORKSPACE_NAME = self.get_resource_name("workspacex")
        WORKFLOW_NAME = self.get_resource_name("workflow")

        if self.is_live:
            storage_account_id = self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)
            self.create_event_hub_authorization_rule(RESOURCE_GROUP, AZURE_LOCATION, NAMESPACE_NAME, EVENTHUB_NAME, AUTHORIZATIONRULE_NAME, storage_account_id)
            workspace = self.create_workspace(RESOURCE_GROUP, AZURE_LOCATION, WORKSPACE_NAME)
            workflow = self.create_workflow(RESOURCE_GROUP, AZURE_LOCATION, WORKFLOW_NAME)
            RESOURCE_URI = workflow.id
            workspace_id = workspace.id
        else:
            RESOURCE_URI = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Logic/workflows/" + WORKFLOW_NAME
            workspace_id = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.OperationalInsights/workspaces/" + WORKSPACE_NAME

        # Creates or Updates the diagnostic setting[put]
        BODY = {
          "storage_account_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "workspace_id": workspace_id,
          "event_hub_authorization_rule_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/microsoft.eventhub/namespaces/" + NAMESPACE_NAME + "/authorizationrules/" + AUTHORIZATIONRULE_NAME,
          "event_hub_name": EVENTHUB_NAME,
          "metrics": [],
          "logs": [
            {
              "category": "WorkflowRuntime",
              "enabled": True,
              "retention_policy": {
                "enabled": False,
                "days": "0"
              }
            }
          ],
        }
        diagnostic_settings = self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings.create_or_update(RESOURCE_URI, INSIGHT_NAME, BODY)
        )

        # TODO: resourceGroups has been changed to resourcegroups
        RESOURCE_URI = "subscriptions/{sub}/resourcegroups/{group}/providers/microsoft.logic/workflows/{workflow}".format(
            sub=SUBSCRIPTION_ID,
            group=RESOURCE_GROUP,
            workflow=WORKFLOW_NAME
        )

        # List diagnostic settings categories
        categories = self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings_category.list(RESOURCE_URI) 
        )

        # List diagnostic settings[get]
        result = self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings.list(RESOURCE_URI)
        )

        # Gets the diagnostic setting[get]
        diagnostic_settings = self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings.get(RESOURCE_URI, INSIGHT_NAME)
        )

        # Get diagnostic settings category
        result = self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings_category.get(RESOURCE_URI, categories.value[0].name) 
        )

        # Deletes the diagnostic setting[delete]
        self.event_loop.run_until_complete(
            self.mgmt_client.diagnostic_settings.delete(RESOURCE_URI, INSIGHT_NAME)
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
