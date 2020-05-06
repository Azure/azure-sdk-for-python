# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 18
# Methods Covered : 18
# Examples Total  : 22
# Examples Tested : 22
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.sqlvirtualmachine
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlVirtualMachineTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlVirtualMachineTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sqlvirtualmachine.SqlVirtualMachineManagementClient
        )
        if self.is_live:
            from azure.mgmt.compute import ComputeManagementClient
                self.compute_client = self.create_mgmt_client(
                ComputeManagementClient
            )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sqlvirtualmachine(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        SQL_VIRTUAL_MACHINE_GROUP_NAME = "mySqlVirtualMachineGroup"
        AVAILABILITY_GROUP_LISTENER_NAME = "myAvailabilityGroupListener"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        LOAD_BALANCER_NAME = "myLoadBalancer"
        SQL_VIRTUAL_MACHINE_NAME = "myVirtualMachine"
        VIRTUAL_MACHINE_NAME = "myVirtualMachine"


        if self.is_live:



        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine for Storage Configuration Settings to EXTEND Data, Log or TempDB storage pool.[put]
        BODY = {
          "location": "northeurope",
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "storage_configuration_settings": {
            "disk_configuration_type": "EXTEND",
            "sql_data_settings": {
              "luns": [
                "2"
              ]
            }
          }
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine for Storage Configuration Settings to NEW Data, Log and TempDB storage pool.[put]
        BODY = {
          "location": "northeurope",
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "storage_configuration_settings": {
            "disk_configuration_type": "NEW",
            "storage_workload_type": "OLTP",
            "sql_data_settings": {
              "default_file_path": "F:\\folderpath\\",
              "luns": [
                "0"
              ]
            },
            "sql_log_settings": {
              "default_file_path": "G:\\folderpath\\",
              "luns": [
                "1"
              ]
            },
            "sql_temp_db_settings": {
              "default_file_path": "D:\\TEMP"
            }
          }
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine and joins it to a SQL virtual machine group.[put]
        BODY = {
          "location": "northeurope",
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "sql_virtual_machine_group_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachineGroups/" + SQL_VIRTUAL_MACHINE_GROUP_NAME + "",
          "wsfc_domain_credentials": {
            "cluster_bootstrap_account_password": "<Password>",
            "cluster_operator_account_password": "<Password>",
            "sql_service_account_password": "<Password>"
          }
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine with max parameters.[put]
        BODY = {
          "location": "northeurope",
          "sql_server_license_type": "PAYG",
          "sql_image_sku": "Enterprise",
          "sql_management": "Full",
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "server_configurations_management_settings": {
            "sql_connectivity_update_settings": {
              "connectivity_type": "PRIVATE",
              "port": "1433",
              "sql_auth_update_user_name": "sqllogin",
              "sql_auth_update_password": "<password>"
            },
            "sql_storage_update_settings": {
              "disk_count": "1",
              "starting_device_id": "2",
              "disk_configuration_type": "NEW"
            },
            "sql_workload_type_update_settings": {
              "sql_workload_type": "OLTP"
            },
            "additional_features_server_configurations": {
              "is_rservices_enabled": False
            }
          },
          "key_vault_credential_settings": {
            "enable": False
          },
          "auto_patching_settings": {
            "enable": True,
            "day_of_week": "Sunday",
            "maintenance_window_starting_hour": "2",
            "maintenance_window_duration": "60"
          },
          "auto_backup_settings": {
            "enable": True,
            "retention_period": "17",
            "enable_encryption": True,
            "password": "<Password>",
            "backup_schedule_type": "Manual",
            "backup_system_dbs": True,
            "storage_account_url": "https://teststorage.blob.core.windows.net/",
            "storage_access_key": "<primary storage access key>",
            "full_backup_frequency": "Daily",
            "full_backup_start_time": "6",
            "full_backup_window_hours": "11",
            "log_backup_frequency": "10"
          }
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine with min parameters.[put]
        BODY = {
          "location": "northeurope",
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachineGroups/put/Creates or updates a SQL virtual machine group.[put]
        BODY = {
          "location": "northeurope",
          "tags": {
            "mytag": "myval"
          },
          "sql_image_offer": "SQL2016-WS2016",
          "sql_image_sku": "Enterprise",
          "wsfc_domain_profile": {
            "domain_fqdn": "testdomain.com",
            "ou_path": "OU=WSCluster,DC=testdomain,DC=com",
            "cluster_bootstrap_account": "testrpadmin",
            "cluster_operator_account": "testrp@testdomain.com",
            "sql_service_account": "sqlservice@testdomain.com",
            "storage_account_url": "https://storgact.blob.core.windows.net/",
            "storage_account_primary_key": "<primary storage access key>"
          }
        }
        result = self.mgmt_client.sql_virtual_machine_groups.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, parameters=BODY)
        result = result.result()

        # /AvailabilityGroupListeners/put/Creates or updates an availability group listener.[put]
        BODY = {
          "availability_group_name": "ag-test",
          "load_balancer_configurations": [
            {
              "private_ip_address": {
                "ip_address": "10.1.0.112",
                "subnet_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
              },
              "load_balancer_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/loadBalancers/" + LOAD_BALANCER_NAME + "",
              "probe_port": "59983",
              "sql_virtual_machine_instances": [
                "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm2",
                "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm3"
              ]
            }
          ],
          "port": "1433"
        }
        result = self.mgmt_client.availability_group_listeners.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME, parameters=BODY)
        result = result.result()

        # /AvailabilityGroupListeners/get/Gets an availability group listener.[get]
        result = self.mgmt_client.availability_group_listeners.get(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME)

        # /AvailabilityGroupListeners/get/Lists all availability group listeners in a SQL virtual machine group.[get]
        result = self.mgmt_client.availability_group_listeners.list_by_group(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)

        # /SqlVirtualMachines/get/Gets the list of sql virtual machines in a SQL virtual machine group.[get]
        result = self.mgmt_client.sql_virtual_machines.list_by_sql_vm_group(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)

        # /SqlVirtualMachineGroups/get/Gets a SQL virtual machine group.[get]
        result = self.mgmt_client.sql_virtual_machine_groups.get(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)

        # /SqlVirtualMachines/get/Gets a SQL virtual machine.[get]
        result = self.mgmt_client.sql_virtual_machines.get(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME)

        # /SqlVirtualMachineGroups/get/Gets all SQL virtual machine groups in a resource group.[get]
        result = self.mgmt_client.sql_virtual_machine_groups.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /SqlVirtualMachines/get/Gets all SQL virtual machines in a resource group.[get]
        result = self.mgmt_client.sql_virtual_machines.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

        # /SqlVirtualMachineGroups/get/Gets all SQL virtual machine groups in a subscription.[get]
        result = self.mgmt_client.sql_virtual_machine_groups.list()

        # /SqlVirtualMachines/get/Gets all SQL virtual machines in a subscription.[get]
        result = self.mgmt_client.sql_virtual_machines.list()

        # /Operations/get/Lists all of the available SQL Rest API operations.[get]
        result = self.mgmt_client.operations.list()

        # /SqlVirtualMachineGroups/patch/Updates a SQL virtual machine group tags.[patch]
        BODY = {
          "tags": {
            "mytag": "myval"
          }
        }
        result = self.mgmt_client.sql_virtual_machine_groups.update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/patch/Updates a SQL virtual machine tags.[patch]
        BODY = {
          "tags": {
            "mytag": "myval"
          }
        }
        result = self.mgmt_client.sql_virtual_machines.update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /AvailabilityGroupListeners/delete/Deletes an availability group listener.[delete]
        result = self.mgmt_client.availability_group_listeners.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME)
        result = result.result()

        # /SqlVirtualMachineGroups/delete/Deletes a SQL virtual machine group.[delete]
        result = self.mgmt_client.sql_virtual_machine_groups.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)
        result = result.result()

        # /SqlVirtualMachines/delete/Deletes a SQL virtual machine.[delete]
        result = self.mgmt_client.sql_virtual_machines.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
