# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 26
# Methods Covered : 26
# Examples Total  : 26
# Examples Tested : 20
# Coverage %      : 77
# ----------------------

# Current Operation Coverage:
#   Operations: 1/1
#   Redis: 10/13
#   FirewallRules: 4/4
#   PatchSchedules: 4/4
#   LinkedServer: 1/4

import time
import unittest

import azure.mgmt.redis
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtRedisTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRedisTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.redis.RedisManagementClient
        )


        if self.is_live:
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

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

        async_subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_redis(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "myosgkxy"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        # CACHE_NAME = "myCache"
        CACHE_NAME = NAME
        RULE_NAME = "myRule"
        DEFAULT = "default"
        LINKED_SERVER_NAME = "myLinkedServer"
        REDIS_NAME = "myRedis"

        if self.is_live:
            self.create_virtual_network(RESOURCE_GROUP, AZURE_LOCATION, VIRTUAL_NETWORK_NAME, SUBNET_NAME)

#--------------------------------------------------------------------------
        # /Redis/put/RedisCacheCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "zones": [
            "1"
          ],
          "sku": {
            "name": "Premium",
            "family": "P",
            "capacity": "1"
          },
          "enable_non_ssl_port": True,
          "shard_count": "2",
        #   "replicas_per_master": "2",
          "redis_configuration": {
            "maxmemory-policy": "allkeys-lru"
          },
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "static_ip": "10.0.0.5",
          "minimum_tls_version": "1.2"
        }
        result = self.mgmt_client.redis.begin_create(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PatchSchedules/put/RedisCachePatchSchedulesCreateOrUpdate[put]
#--------------------------------------------------------------------------
        BODY = {
          "schedule_entries": [
            {
              "day_of_week": "Monday",
              "start_hour_utc": "12",
              "maintenance_window": "PT5H"
            },
            {
              "day_of_week": "Tuesday",
              "start_hour_utc": "12"
            }
          ]
        }
        result = self.mgmt_client.patch_schedules.create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, default=DEFAULT, parameters=BODY)

        if self.is_live:
            time.sleep(1800)

#--------------------------------------------------------------------------
        # /FirewallRules/put/RedisCacheFirewallRuleCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "start_ip": "10.0.1.1",
          "end_ip": "10.0.1.4"
        }
        result = self.mgmt_client.firewall_rules.create_or_update(resource_group_name=RESOURCE_GROUP, cache_name=CACHE_NAME, rule_name=RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /LinkedServer/put/LinkedServer_Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "linked_redis_cache_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Cache/Redis/" + REDIS_NAME,
          "linked_redis_cache_location": "West US",
          "server_role": "Secondary"
        }
        # result = self.mgmt_client.linked_server.begin_create(resource_group_name=RESOURCE_GROUP, name=NAME, linked_server_name=LINKED_SERVER_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /LinkedServer/get/LinkedServer_Get[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.linked_server.get(resource_group_name=RESOURCE_GROUP, name=NAME, linked_server_name=LINKED_SERVER_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/get/RedisCacheFirewallRuleGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.get(resource_group_name=RESOURCE_GROUP, cache_name=CACHE_NAME, rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /PatchSchedules/get/RedisCachePatchSchedulesGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.patch_schedules.get(resource_group_name=RESOURCE_GROUP, name=NAME, default=DEFAULT)

#--------------------------------------------------------------------------
        # /Redis/get/RedisCacheGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.redis.list_upgrade_notifications(resource_group_name=RESOURCE_GROUP, name=NAME, history="5000")

#--------------------------------------------------------------------------
        # /PatchSchedules/get/RedisCachePatchSchedulesList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.patch_schedules.list_by_redis_resource(resource_group_name=RESOURCE_GROUP, cache_name=CACHE_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/get/RedisCacheFirewallRulesList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.list_by_redis_resource(resource_group_name=RESOURCE_GROUP, cache_name=CACHE_NAME)

#--------------------------------------------------------------------------
        # /LinkedServer/get/LinkedServer_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.linked_server.list(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Redis/get/RedisCacheGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.redis.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Redis/get/RedisCacheListByResourceGroup[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.redis.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Redis/get/RedisCacheList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.redis.list()

#--------------------------------------------------------------------------
        # /Operations/get/Operations_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheRegenerateKey[post]
#--------------------------------------------------------------------------
        BODY = {
          "key_type": "Primary"
        }
        result = self.mgmt_client.redis.regenerate_key(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheForceReboot[post]
#--------------------------------------------------------------------------
        BODY = {
          "shard_id": "0",
          "reboot_type": "AllNodes"
        }
        result = self.mgmt_client.redis.force_reboot(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheListKeys[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.redis.list_keys(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheImport[post]
#--------------------------------------------------------------------------
        BODY = {
          "format": "RDB",
          "files": [
            "http://fileuris.contoso.com/pathtofile1"
          ]
        }
        # result = self.mgmt_client.redis.begin_import_data(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheExport[post]
#--------------------------------------------------------------------------
        BODY = {
          "format": "RDB",
          "prefix": "datadump1",
          "container": "https://contosostorage.blob.core.window.net/urltoBlobContainer?sasKeyParameters"
        }
        # result = self.mgmt_client.redis.begin_export_data(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Redis/patch/RedisCacheUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "enable_non_ssl_port": True
        }
        result = self.mgmt_client.redis.update(resource_group_name=RESOURCE_GROUP, name=NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Redis/post/RedisCacheList[post]
#--------------------------------------------------------------------------
        BODY = {
          "type": "Microsoft.Cache/Redis",
          "name": "cacheName"
        }
        result = self.mgmt_client.redis.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /LinkedServer/delete/LinkedServerDelete[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.linked_server.delete(resource_group_name=RESOURCE_GROUP, name=NAME, linked_server_name=LINKED_SERVER_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/delete/RedisCacheFirewallRuleDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.delete(resource_group_name=RESOURCE_GROUP, cache_name=CACHE_NAME, rule_name=RULE_NAME)

#--------------------------------------------------------------------------
        # /PatchSchedules/delete/RedisCachePatchSchedulesDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.patch_schedules.delete(resource_group_name=RESOURCE_GROUP, name=NAME, default=DEFAULT)

#--------------------------------------------------------------------------
        # /Redis/delete/RedisCacheDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.redis.begin_delete(resource_group_name=RESOURCE_GROUP, name=NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
