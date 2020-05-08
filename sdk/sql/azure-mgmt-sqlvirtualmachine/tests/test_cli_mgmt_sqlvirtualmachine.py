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
# Examples Tested : 16
# Coverage %      : 55
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
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )
            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
            )


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

    def create_network_interface(self, group_name, location, nic_name, subnet_id):
        async_nic_creation = self.network_client.network_interfaces.create_or_update(
            group_name,
            nic_name,
            {
                'location': location,
                'ip_configurations': [{
                    'name': 'MyIpConfig',
                    'subnet': {
                        'id': subnet_id
                    }
                }]
            }
        )
        nic_info = async_nic_creation.result()
        return nic_info.id

    def create_vm(self, group_name, location, vm_name, nic_id):
        # Create a vm with empty data disks.[put]
        BODY = {
          "location": location,
          "hardware_profile": {
            "vm_size": "Standard_D2_v2"
          },
          "storage_profile": {
            "image_reference": {
              "sku": "enterprise",
              "publisher": "microsoftsqlserver",
              "version": "latest",
              "offer": "sql2019-ws2019"
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
            "admin_password": "Password1!!!",
            "computer_name" : "myvm"
          },
          "network_profile": {
            "network_interfaces": [
              {
                # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/networkInterfaces/" + NIC_ID + "",
                "id": nic_id,
                "properties": {
                  "primary": True
                }
              }
            ]
          }
        }
        result = self.compute_client.virtual_machines.create_or_update(group_name, vm_name, BODY)
        result = result.result()

    def create_storage_account(self, group_name, location, storage_name):
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "StorageV2",
          "location": AZURE_LOCATION,
          "encryption": {
            "services": {
              "file": {
                "key_type": "Account",
                "enabled": True
              },
              "blob": {
                "key_type": "Account",
                "enabled": True
              }
            },
            "key_source": "Microsoft.Storage"
          }
        }
        result_create = self.storage_client.storage_accounts.create(
            group_name,
            storage_name,
            BODY
        )
        result = result_create.result()
        print(result)
    
    def get_storage_key(self, group_name, storage_name):
        result = self.storage_client.storage_accounts.list_keys(group_name, storage_name)
        print(result)
        return result.keys[0].value

 
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sqlvirtualmachine(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        SQL_VIRTUAL_MACHINE_GROUP_NAME = "mySqlVMGroup"
        AVAILABILITY_GROUP_LISTENER_NAME = "myAvailabilityGroupListener"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        LOAD_BALANCER_NAME = "myLoadBalancer"
        SQL_VIRTUAL_MACHINE_NAME = "myVirtualMachine"
        VIRTUAL_MACHINE_NAME = "myVirtualMachine"

        if self.is_live:
            subnet = self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, "myVirtualNetwork", "mySubnet")
            nic_id = self.create_network_interface(RESOURCE_GROUP, AZURE_LOCATION, "myNetworkInterface", subnet.id)
            self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_MACHINE_NAME, nic_id)
            self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, "tempstorageaccountxysdtr")
            storage_key = self.get_storage_key(RESOURCE_GROUP, "tempstorageaccountxysdtr")
        else:
            storage_key = "xxxx"

        # /SqlVirtualMachineGroups/put/Creates or updates a SQL virtual machine group.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "mytag": "myval"
          },
          "sql_image_offer": "sql2019-ws2019",
          "sql_image_sku": "Enterprise",
          "wsfc_domain_profile": {
            "domain_fqdn": "testdomain.com",
            "ou_path": "OU=WSCluster,DC=testdomain,DC=com",
            "cluster_bootstrap_account": "testrpadmin",
            "cluster_operator_account": "testrp@testdomain.com",
            "sql_service_account": "sqlservice@testdomain.com",
            "storage_account_url": "https://" + "tempstorageaccountxysdtr" + ".blob.core.windows.net/",
            "storage_account_primary_key": storage_key
          }
        }
        result = self.mgmt_client.sql_virtual_machine_groups.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine for Storage Configuration Settings to EXTEND Data, Log or TempDB storage pool.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "sql_server_license_type": "PAYG",
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
          "location": AZURE_LOCATION,
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

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine with max parameters.[put]
        BODY = {
          "location": AZURE_LOCATION,
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
            "storage_account_url": "https://" + "tempstorageaccountxysdtr" + ".blob.core.windows.net/",
            "storage_access_key": storage_key,
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
          "location": AZURE_LOCATION,
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + ""
        }
        result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        result = result.result()

        # /SqlVirtualMachines/put/Creates or updates a SQL virtual machine and joins it to a SQL virtual machine group.[put]
        BODY = {
          "location": AZURE_LOCATION,
          "virtual_machine_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VIRTUAL_MACHINE_NAME + "",
          "sql_virtual_machine_group_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachineGroups/" + SQL_VIRTUAL_MACHINE_GROUP_NAME + "",
          "wsfc_domain_credentials": {
            "cluster_bootstrap_account_password": "<Password>",
            "cluster_operator_account_password": "<Password>",
            "sql_service_account_password": "<Password>"
          }
        }
        # result = self.mgmt_client.sql_virtual_machines.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        # result = result.result()

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
        # result = self.mgmt_client.availability_group_listeners.create_or_update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME, parameters=BODY)
        # result = result.result()

        # /AvailabilityGroupListeners/get/Gets an availability group listener.[get]
        # result = self.mgmt_client.availability_group_listeners.get(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME)

        # /AvailabilityGroupListeners/get/Lists all availability group listeners in a SQL virtual machine group.[get]
        # result = self.mgmt_client.availability_group_listeners.list_by_group(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)

        # /SqlVirtualMachines/get/Gets the list of sql virtual machines in a SQL virtual machine group.[get]
        # result = self.mgmt_client.sql_virtual_machines.list_by_sql_vm_group(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)

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
        # result = self.mgmt_client.sql_virtual_machine_groups.update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, parameters=BODY)
        # result = result.result()

        # /SqlVirtualMachines/patch/Updates a SQL virtual machine tags.[patch]
        BODY = {
          "tags": {
            "mytag": "myval"
          }
        }
        # result = self.mgmt_client.sql_virtual_machines.update(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME, parameters=BODY)
        # result = result.result()

        # /AvailabilityGroupListeners/delete/Deletes an availability group listener.[delete]
        # result = self.mgmt_client.availability_group_listeners.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME, availability_group_listener_name=AVAILABILITY_GROUP_LISTENER_NAME)
        # result = result.result()

        # /SqlVirtualMachineGroups/delete/Deletes a SQL virtual machine group.[delete]
        result = self.mgmt_client.sql_virtual_machine_groups.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_group_name=SQL_VIRTUAL_MACHINE_GROUP_NAME)
        result = result.result()

        # /SqlVirtualMachines/delete/Deletes a SQL virtual machine.[delete]
        result = self.mgmt_client.sql_virtual_machines.delete(resource_group_name=RESOURCE_GROUP, sql_virtual_machine_name=SQL_VIRTUAL_MACHINE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
