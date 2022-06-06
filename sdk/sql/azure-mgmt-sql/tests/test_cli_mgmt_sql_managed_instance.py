# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   ManagedInstances: 6/8
#   ManagedInstanceOperations: 1/3

import pytest

import azure.mgmt.sql
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, ResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = 'eastus'

class TestMgmtSql(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )
        # self.mgmt_client180601 = self.create_mgmt_client(
        #     azure.mgmt.sql.SqlManagementClient,
        #     api_version="2018-06-01-preview"
        # )

        # if self.is_live:
        #     from azure.mgmt.network import NetworkManagementClient
        #     self.network_client = self.create_mgmt_client(
        #         NetworkManagementClient
        #     )

    def create_virtual_network(self, group_name, location, security_group_name, route_table_name, network_name, subnet_name):

        # Create network security group
        network_security_group = self.network_client.network_security_groups.begin_create_or_update(
            group_name,
            security_group_name,
            {
                "location": location
            }
        ).result()

        # Create security rule
        security_rule = self.network_client.security_rules.begin_create_or_update(
            group_name,
            security_group_name,
            "allow_tds_inbound",
            {
                "protocol": "Tcp",
                "access": "Allow",
                "direction": "Inbound",
                "source_port_range": "*",
                "source_address_prefix": "10.0.0.0/16",
                "destination_address_prefix": "*",
                "destination_port_range": "1433",
                "priority": "1000"
            }
        ).result()
        
        # Create security rule
        security_rule = self.network_client.security_rules.begin_create_or_update(
            group_name,
            security_group_name,
            "allow_redirect_inbound",
            {
                "protocol": "Tcp",
                "access": "Allow",
                "direction": "Inbound",
                "source_port_range": "*",
                "source_address_prefix": "10.0.0.0/16",
                "destination_address_prefix": "*",
                "destination_port_range": "11000-11999",
                "priority": "1100"
            }
        ).result()

        # Create security rule
        security_rule = self.network_client.security_rules.begin_create_or_update(
            group_name,
            security_group_name,
            "deny_all_inbound",
            {
                "protocol": "*",
                "access": "Deny",
                "direction": "Inbound",
                "source_port_range": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "destination_port_range": "*",
                "priority": "4096"
            }
        ).result()

        # Create security rule
        security_rule = self.network_client.security_rules.begin_create_or_update(
            group_name,
            security_group_name,
            "deny_all_outbound",
            {
                "protocol": "*",
                "access": "Deny",
                "direction": "Outbound",
                "source_port_range": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "destination_port_range": "*",
                "priority": "4095"
            }
        ).result()

        # Create route table
        route_table = self.network_client.route_tables.begin_create_or_update(
            group_name,
            route_table_name,
            {
                "location": location
            }
        ).result()

        # create virtual network
        azure_operation_poller = self.network_client.virtual_networks.begin_create_or_update(
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

        # create subnet
        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {
                'address_prefix': '10.0.0.0/24',
                'network_security_group': network_security_group,
                'route_table': route_table,
                'delegations': [
                    {
                        "service_name": "Microsoft.Sql/managedInstances",
                        "name": "dgManagedInstancexxx"
                    }
                ]
            }
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @recorded_by_proxy
    def test_instance_operation(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/get/List the managed instance management operations[get]
#--------------------------------------------------------------------------
        # result = self.client.managed_instance_operations.list_by_managed_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)
        result = self.client.managed_instances.list()
        page_result = [item for item in result]

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/get/Gets the managed instance management operation[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instance_operations.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/post/Cancel the managed instance management operation[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instance_operations.cancel(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, operation_id=OPERATION_ID)

    @pytest.mark.skip("it will take a long time.")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_managed_instances(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mysubnet"
        NETWORK_SECURITY_GROUP = "mynetworksecuritygroup"
        ROUTE_TABLE = "myroutetable"
        MANAGED_INSTANCE_NAME = "mymanagedinstancexpnvcxxvx"
        INSTANCE_POOL_NAME = "myinstancepool"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, NETWORK_SECURITY_GROUP, ROUTE_TABLE, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/put/Create managed instance with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            # "name": "BC_Gen5",
            # "tier": "GeneralPurpose"
            "name": "MIGP8G4",
            "tier": "GeneralPurpose",
            "family": "Gen5"
          },
          "location": "westeurope",
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "storage_account_type": "GRS",
        #   "v_cores": "8",
        #   "storage_size_in_gb": "128",
        #   "collection": "Serbian_Cyrillic_100_CS_AS",
        #   "public_data_endpoint_enabled": True,
        #   "proxy_override": "Proxy",
        #   "timezone_id": "Central European Standard Time",
        #   "minimal_tls_version": "1.2",
        #   "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client180601.managed_instances.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        # [Kaihui] it will use 6 hours to complete creation, so comment it.
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances by instance pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list_by_instance_pool(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/Get managed instance[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instances.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list()

#--------------------------------------------------------------------------
        # /ManagedInstances/post/Failover a managed instance.[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.managed_instances.begin_failover(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, replica_type="Primary")
        # result = result.result()

# #--------------------------------------------------------------------------
#         # /ManagedInstances/patch/Update managed instance with minimal properties[patch]
# #--------------------------------------------------------------------------
#         BODY = {
#           "administrator_login": "dummylogin",
#           "administrator_login_password": "Un53cuRE!",
#           "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
#           "v_cores": "8",
#           "storage_size_in_gb": "128",
#           "collection": "Serbian_Cyrillic_100_CS_AS",
#           "public_data_endpoint_enabled": True,
#           "proxy_override": "Proxy",
#           "timezone_id": "Central European Standard Time",
#           "minimal_tls_version": "1.2"
#         }
#         result = self.mgmt_client.managed_instances.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/delete/Delete managed instance[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)
        result = result.result()
