# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 78
# Methods Covered : 70
# Examples Total  : 93
# Examples Tested : 93
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   PrivateEndpointConnections: 0/4
#   Registries: 14/15
#   Operations: 1/1
#   Replications: 5/5
#   AgentPools: 6/6
#   Webhooks: 8/8
#   ScopeMaps: 5/5
#   Tokens: 5/5

import unittest

import azure.mgmt.containerregistry
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'


class MgmtRegistryTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRegistryTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient,
            api_version="2019-12-01-preview"  # test the latest version
        )

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_replications(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        REPLICATION_NAME = "myReplication"

#--------------------------------------------------------------------------
        # /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": "westus",  # other location
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Premium"  # replications need Premium
          },
          "admin_user_enabled": True
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Replications/put/ReplicationCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          }
        }
        result = self.mgmt_client.replications.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, replication_name=REPLICATION_NAME, replication=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Replications/get/ReplicationGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replications.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, replication_name=REPLICATION_NAME)

#--------------------------------------------------------------------------
        # /Replications/get/ReplicationList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replications.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Replications/patch/ReplicationUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "key": "value"
          }
        }
        result = self.mgmt_client.replications.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, replication_name=REPLICATION_NAME, replication_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Replications/delete/ReplicationDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replications.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, replication_name=REPLICATION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_webhooks(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        WEBHOOK_NAME = "myWebhook"

#--------------------------------------------------------------------------
        # /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Standard"
          },
          "admin_user_enabled": True
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Webhooks/put/WebhookCreate[put] (TODO: add to swagger)
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "service_uri": "http://www.microsoft.com",
          "status": "enabled",
          "actions": [
            "push"
          ]
        }
        result = self.mgmt_client.webhooks.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME, webhook_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Webhooks/get/WebhookGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME)

#--------------------------------------------------------------------------
        # /Webhooks/get/WebhookList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Webhooks/post/WebhookGetCallbackConfig[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.get_callback_config(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME)

#--------------------------------------------------------------------------
        # /Webhooks/post/WebhookListEvents[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.list_events(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME)

#--------------------------------------------------------------------------
        # /Webhooks/post/WebhookPing[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.ping(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME)

#--------------------------------------------------------------------------
        # /Webhooks/patch/WebhookUpdate[patch] (TODO:)
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "service_uri": "http://www.microsoft.com",
          "status": "enabled",
          "actions": [
            "push"
          ]
        }
        result = self.mgmt_client.webhooks.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME, webhook_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Webhooks/delete/WebhookDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.webhooks.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, webhook_name=WEBHOOK_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_agent_pools(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        AGENT_POOL_NAME = "myagentpool"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Premium"  # agent pools need Premium
          },
          "admin_user_enabled": False
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/put/AgentPools_Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "count": "1",
          "tier": "S1",
          "os": "Linux"
        }
        result = self.mgmt_client.agent_pools.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, agent_pool_name=AGENT_POOL_NAME, agent_pool=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/get/AgentPools_Get[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.agent_pools.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, agent_pool_name=AGENT_POOL_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/get/AgentPools_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.agent_pools.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/post/AgentPools_GetQueueStatus[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.agent_pools.get_queue_status(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, agent_pool_name=AGENT_POOL_NAME)

#--------------------------------------------------------------------------
        # /AgentPools/patch/AgentPools_Update[patch]
#--------------------------------------------------------------------------
        BODY = {
          "count": "1"
        }
        result = self.mgmt_client.agent_pools.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, agent_pool_name=AGENT_POOL_NAME, update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /AgentPools/delete/AgentPools_Delete[delete]
#--------------------------------------------------------------------------
        try:
            result = self.mgmt_client.agent_pools.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, agent_pool_name=AGENT_POOL_NAME)
            result = result.result()
        except HttpResponseError as e:
            if not str(e).startswith("(ResourceNotFound)"):
                raise e

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_scope_maps_and_tokens(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        # UNIQUE = resource_group.name[-4:]
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        SCOPE_MAP_NAME = "myScopeMap"
        TOKEN_NAME = "myToken"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Premium"  # ScopeMap need Premium
          },
          "admin_user_enabled": False
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()
        
#--------------------------------------------------------------------------
# /ScopeMaps/put/ScopeMapCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "description": "Developer Scopes",
          "actions": [
            "repositories/foo/content/read",
            "repositories/foo/content/delete"
          ]
        }
        result = self.mgmt_client.scope_maps.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, scope_map_name=SCOPE_MAP_NAME, scope_map_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tokens/put/TokenCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "scope_map_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ContainerRegistry/registries/" + REGISTRY_NAME + "/scopeMaps/" + SCOPE_MAP_NAME,
          "status": "enabled",
        #   "credentials": {
        #     "certificates": [
        #       {
        #         "name": "certificate1",
        #         "encoded_pem_certificate": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUc3akNDQk5hZ0F3SUJBZ0lURmdBQlR3UVpyZGdmdmhxdzBnQUFBQUZQQkRBTkJna3Foa2lHOXcwQkFRc0YKQURDQml6RUxNQWtHQTFVRUJoTUNWVk14RXpBUkJnTlZCQWdUQ2xkaGMyaHBibWQwYjI0eEVEQU9CZ05WQkFjVApCMUpsWkcxdmJtUXhIakFjQmdOVkJBb1RGVTFwWTNKdmMyOW1kQ0JEYjNKd2IzSmhkR2x2YmpFVk1CTUdBMVVFCkN4TU1UV2xqY205emIyWjBJRWxVTVI0d0hBWURWUVFERXhWTmFXTnliM052Wm5RZ1NWUWdWRXhUSUVOQklEUXcKSGhjTk1UZ3dOREV5TWpJek1qUTRXaGNOTWpBd05ERXlNakl6TWpRNFdqQTVNVGN3TlFZRFZRUURFeTV6WlhKMgphV05sWTJ4cFpXNTBZMlZ5ZEMxd1lYSjBibVZ5TG0xaGJtRm5aVzFsYm5RdVlYcDFjbVV1WTI5dE1JSUJJakFOCkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTBSYjdJcHpxMmR4emhhbVpyS1ZDakMzeTQyYlYKUnNIY2pCUTFuSDBHZ1puUDhXeDZDSE1mWThybkVJQzRLeVRRYkJXVzhnNXlmc3NSQ0ZXbFpxYjR6SkRXS0pmTgpGSmNMUm9LNnhwTktZYVZVTkVlT25IdUxHYTM0ZlA0VjBFRjZybzdvbkRLME5zanhjY1dZVzRNVXVzc0xrQS94CkUrM2RwU1REdk1KcjJoWUpsVnFDcVR6blQvbmZaVUZzQUVEQnp5MUpOOHZiZDlIR2czc2Myd0x4dk95cFJOc0gKT1V3V2pmN2xzWWZleEVlcWkzY29EeHc2alpLVWEyVkdsUnBpTkowMjhBQitYSi9TU1FVNVBsd0JBbU9TT3ovRApGY0NKdGpPZlBqU1NKckFIQVV3SHU3RzlSV05JTFBwYU9zQ1J5eitETE5zNGpvNlEvUUg4d1lManJRSURBUUFCCm80SUNtakNDQXBZd0N3WURWUjBQQkFRREFnU3dNQjBHQTFVZEpRUVdNQlFHQ0NzR0FRVUZCd01DQmdnckJnRUYKQlFjREFUQWRCZ05WSFE0RUZnUVVlbEdkVVJrZzJoSFFOWEQ4WUc4L3drdjJVT0F3SHdZRFZSMGpCQmd3Rm9BVQplbnVNd2Mvbm9Nb2MxR3Y2KytFend3OGFvcDB3Z2F3R0ExVWRId1NCcERDQm9UQ0JucUNCbTZDQm1JWkxhSFIwCmNEb3ZMMjF6WTNKc0xtMXBZM0p2YzI5bWRDNWpiMjB2Y0d0cEwyMXpZMjl5Y0M5amNtd3ZUV2xqY205emIyWjAKSlRJd1NWUWxNakJVVEZNbE1qQkRRU1V5TURRdVkzSnNoa2xvZEhSd09pOHZZM0pzTG0xcFkzSnZjMjltZEM1agpiMjB2Y0d0cEwyMXpZMjl5Y0M5amNtd3ZUV2xqY205emIyWjBKVEl3U1ZRbE1qQlVURk1sTWpCRFFTVXlNRFF1ClkzSnNNSUdGQmdnckJnRUZCUWNCQVFSNU1IY3dVUVlJS3dZQkJRVUhNQUtHUldoMGRIQTZMeTkzZDNjdWJXbGoKY205emIyWjBMbU52YlM5d2Eya3ZiWE5qYjNKd0wwMXBZM0p2YzI5bWRDVXlNRWxVSlRJd1ZFeFRKVEl3UTBFbApNakEwTG1OeWREQWlCZ2dyQmdFRkJRY3dBWVlXYUhSMGNEb3ZMMjlqYzNBdWJYTnZZM053TG1OdmJUQStCZ2tyCkJnRUVBWUkzRlFjRU1UQXZCaWNyQmdFRUFZSTNGUWlIMm9aMWcrN1pBWUxKaFJ1QnRaNWhoZlRyWUlGZGhOTGYKUW9Mbmszb0NBV1FDQVIwd1RRWURWUjBnQkVZd1JEQkNCZ2tyQmdFRUFZSTNLZ0V3TlRBekJnZ3JCZ0VGQlFjQwpBUlluYUhSMGNEb3ZMM2QzZHk1dGFXTnliM052Wm5RdVkyOXRMM0JyYVM5dGMyTnZjbkF2WTNCek1DY0dDU3NHCkFRUUJnamNWQ2dRYU1CZ3dDZ1lJS3dZQkJRVUhBd0l3Q2dZSUt3WUJCUVVIQXdFd09RWURWUjBSQkRJd01JSXUKYzJWeWRtbGpaV05zYVdWdWRHTmxjblF0Y0dGeWRHNWxjaTV0WVc1aFoyVnRaVzUwTG1GNmRYSmxMbU52YlRBTgpCZ2txaGtpRzl3MEJBUXNGQUFPQ0FnRUFIVXIzbk1vdUI5WWdDUlRWYndUTllIS2RkWGJkSW1GUXNDYys4T1g1CjE5c0N6dFFSR05iSXEwVW1Ba01MbFVvWTIxckh4ZXdxU2hWczFhL2RwaFh5Tk1pcUdaU2QzU1BtYzZscitqUFQKNXVEREs0MUlWeXN0K2VUNlpyazFvcCtMVmdkeS9EU2lyNzVqcWZFY016bS82bU8rNnFNeWRLTWtVYmM5K3JHVwphUkpUcjRWUUdIRmEwNEIwZVZpNUd4MG9pL2RpZDNSaXg2aXJMMjFJSGEwYjN6c1hzZHpHU0R2K3hqL2Q2S0l4Ckdrd2FhYmZvU1NoQnFqaFNlQ0VyZXFlb1RpYjljdGw0MGRVdUp3THl4bjhHS2N6K3AvMEJUOEIxU3lYK01OQ2wKY0pkMjVtMjhLajY2TGUxOEVyeFlJYXZJVGVGa3Y2eGZjdkEvcHladDdPaU41QTlGQk1IUmpQK1kyZ2tvdjMrcQpISFRUZG4xNnlRajduNit3YlFHNGVleXc0YisyQkRLcUxNVFU2ZmlSQ3ZPM2FPZVBLSFVNN3R4b1FidWl6Z3NzCkNiMzl3QnJOTEZsMkJLQ1RkSCtkSU9oZVJiSkZvbmlwOGRPOUVFZWdSSG9lQW54ZUlYTFBrdXMzTzEvZjRhNkIKWHQ3RG5BUm8xSzJmeEp3VXRaU2MvR3dFSjU5NzlnRXlEa3pDZEVsLzdpWE9QZXVjTXhlM2xVM2pweUtsNERUaApjSkJqQytqNGpLWTFrK1U4b040aGdqYnJISUx6Vnd2eU15OU5KS290U3BMSjQxeHdPOHlGangxalFTT3Bxc0N1ClFhUFUvTjhSZ0hxWjBGTkFzS3dNUmZ6WmdXanRCNzRzYUVEdk5jVmNuNFhCQnFNSG0ydHo2Uzk3d3kxZGt0cTgKSE5BPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="
        #       }
        #     ]
        #   }
        }
        result = self.mgmt_client.tokens.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, token_name=TOKEN_NAME, token_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tokens/get/TokenGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tokens.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, token_name=TOKEN_NAME)

#--------------------------------------------------------------------------
        # /ScopeMaps/get/ScopeMapGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.scope_maps.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, scope_map_name=SCOPE_MAP_NAME)

#--------------------------------------------------------------------------
        # /Tokens/get/TokenList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tokens.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /ScopeMaps/get/ScopeMapList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.scope_maps.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /ScopeMaps/patch/ScopeMapUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "description": "Developer Scopes",
          "actions": [
            "repositories/foo/content/read",
            "repositories/foo/content/delete"
          ]
        }
        result = self.mgmt_client.scope_maps.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, scope_map_name=SCOPE_MAP_NAME, scope_map_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tokens/patch/TokenUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "scope_map_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ContainerRegistry/registries/" + REGISTRY_NAME + "/scopeMaps/" + SCOPE_MAP_NAME,
        #   "credentials": {
        #     "certificates": [
        #       {
        #         "name": "certificate1",
        #         "encoded_pem_certificate": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUc3akNDQk5hZ0F3SUJBZ0lURmdBQlR3UVpyZGdmdmhxdzBnQUFBQUZQQkRBTkJna3Foa2lHOXcwQkFRc0YKQURDQml6RUxNQWtHQTFVRUJoTUNWVk14RXpBUkJnTlZCQWdUQ2xkaGMyaHBibWQwYjI0eEVEQU9CZ05WQkFjVApCMUpsWkcxdmJtUXhIakFjQmdOVkJBb1RGVTFwWTNKdmMyOW1kQ0JEYjNKd2IzSmhkR2x2YmpFVk1CTUdBMVVFCkN4TU1UV2xqY205emIyWjBJRWxVTVI0d0hBWURWUVFERXhWTmFXTnliM052Wm5RZ1NWUWdWRXhUSUVOQklEUXcKSGhjTk1UZ3dOREV5TWpJek1qUTRXaGNOTWpBd05ERXlNakl6TWpRNFdqQTVNVGN3TlFZRFZRUURFeTV6WlhKMgphV05sWTJ4cFpXNTBZMlZ5ZEMxd1lYSjBibVZ5TG0xaGJtRm5aVzFsYm5RdVlYcDFjbVV1WTI5dE1JSUJJakFOCkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQTBSYjdJcHpxMmR4emhhbVpyS1ZDakMzeTQyYlYKUnNIY2pCUTFuSDBHZ1puUDhXeDZDSE1mWThybkVJQzRLeVRRYkJXVzhnNXlmc3NSQ0ZXbFpxYjR6SkRXS0pmTgpGSmNMUm9LNnhwTktZYVZVTkVlT25IdUxHYTM0ZlA0VjBFRjZybzdvbkRLME5zanhjY1dZVzRNVXVzc0xrQS94CkUrM2RwU1REdk1KcjJoWUpsVnFDcVR6blQvbmZaVUZzQUVEQnp5MUpOOHZiZDlIR2czc2Myd0x4dk95cFJOc0gKT1V3V2pmN2xzWWZleEVlcWkzY29EeHc2alpLVWEyVkdsUnBpTkowMjhBQitYSi9TU1FVNVBsd0JBbU9TT3ovRApGY0NKdGpPZlBqU1NKckFIQVV3SHU3RzlSV05JTFBwYU9zQ1J5eitETE5zNGpvNlEvUUg4d1lManJRSURBUUFCCm80SUNtakNDQXBZd0N3WURWUjBQQkFRREFnU3dNQjBHQTFVZEpRUVdNQlFHQ0NzR0FRVUZCd01DQmdnckJnRUYKQlFjREFUQWRCZ05WSFE0RUZnUVVlbEdkVVJrZzJoSFFOWEQ4WUc4L3drdjJVT0F3SHdZRFZSMGpCQmd3Rm9BVQplbnVNd2Mvbm9Nb2MxR3Y2KytFend3OGFvcDB3Z2F3R0ExVWRId1NCcERDQm9UQ0JucUNCbTZDQm1JWkxhSFIwCmNEb3ZMMjF6WTNKc0xtMXBZM0p2YzI5bWRDNWpiMjB2Y0d0cEwyMXpZMjl5Y0M5amNtd3ZUV2xqY205emIyWjAKSlRJd1NWUWxNakJVVEZNbE1qQkRRU1V5TURRdVkzSnNoa2xvZEhSd09pOHZZM0pzTG0xcFkzSnZjMjltZEM1agpiMjB2Y0d0cEwyMXpZMjl5Y0M5amNtd3ZUV2xqY205emIyWjBKVEl3U1ZRbE1qQlVURk1sTWpCRFFTVXlNRFF1ClkzSnNNSUdGQmdnckJnRUZCUWNCQVFSNU1IY3dVUVlJS3dZQkJRVUhNQUtHUldoMGRIQTZMeTkzZDNjdWJXbGoKY205emIyWjBMbU52YlM5d2Eya3ZiWE5qYjNKd0wwMXBZM0p2YzI5bWRDVXlNRWxVSlRJd1ZFeFRKVEl3UTBFbApNakEwTG1OeWREQWlCZ2dyQmdFRkJRY3dBWVlXYUhSMGNEb3ZMMjlqYzNBdWJYTnZZM053TG1OdmJUQStCZ2tyCkJnRUVBWUkzRlFjRU1UQXZCaWNyQmdFRUFZSTNGUWlIMm9aMWcrN1pBWUxKaFJ1QnRaNWhoZlRyWUlGZGhOTGYKUW9Mbmszb0NBV1FDQVIwd1RRWURWUjBnQkVZd1JEQkNCZ2tyQmdFRUFZSTNLZ0V3TlRBekJnZ3JCZ0VGQlFjQwpBUlluYUhSMGNEb3ZMM2QzZHk1dGFXTnliM052Wm5RdVkyOXRMM0JyYVM5dGMyTnZjbkF2WTNCek1DY0dDU3NHCkFRUUJnamNWQ2dRYU1CZ3dDZ1lJS3dZQkJRVUhBd0l3Q2dZSUt3WUJCUVVIQXdFd09RWURWUjBSQkRJd01JSXUKYzJWeWRtbGpaV05zYVdWdWRHTmxjblF0Y0dGeWRHNWxjaTV0WVc1aFoyVnRaVzUwTG1GNmRYSmxMbU52YlRBTgpCZ2txaGtpRzl3MEJBUXNGQUFPQ0FnRUFIVXIzbk1vdUI5WWdDUlRWYndUTllIS2RkWGJkSW1GUXNDYys4T1g1CjE5c0N6dFFSR05iSXEwVW1Ba01MbFVvWTIxckh4ZXdxU2hWczFhL2RwaFh5Tk1pcUdaU2QzU1BtYzZscitqUFQKNXVEREs0MUlWeXN0K2VUNlpyazFvcCtMVmdkeS9EU2lyNzVqcWZFY016bS82bU8rNnFNeWRLTWtVYmM5K3JHVwphUkpUcjRWUUdIRmEwNEIwZVZpNUd4MG9pL2RpZDNSaXg2aXJMMjFJSGEwYjN6c1hzZHpHU0R2K3hqL2Q2S0l4Ckdrd2FhYmZvU1NoQnFqaFNlQ0VyZXFlb1RpYjljdGw0MGRVdUp3THl4bjhHS2N6K3AvMEJUOEIxU3lYK01OQ2wKY0pkMjVtMjhLajY2TGUxOEVyeFlJYXZJVGVGa3Y2eGZjdkEvcHladDdPaU41QTlGQk1IUmpQK1kyZ2tvdjMrcQpISFRUZG4xNnlRajduNit3YlFHNGVleXc0YisyQkRLcUxNVFU2ZmlSQ3ZPM2FPZVBLSFVNN3R4b1FidWl6Z3NzCkNiMzl3QnJOTEZsMkJLQ1RkSCtkSU9oZVJiSkZvbmlwOGRPOUVFZWdSSG9lQW54ZUlYTFBrdXMzTzEvZjRhNkIKWHQ3RG5BUm8xSzJmeEp3VXRaU2MvR3dFSjU5NzlnRXlEa3pDZEVsLzdpWE9QZXVjTXhlM2xVM2pweUtsNERUaApjSkJqQytqNGpLWTFrK1U4b040aGdqYnJISUx6Vnd2eU15OU5KS290U3BMSjQxeHdPOHlGangxalFTT3Bxc0N1ClFhUFUvTjhSZ0hxWjBGTkFzS3dNUmZ6WmdXanRCNzRzYUVEdk5jVmNuNFhCQnFNSG0ydHo2Uzk3d3kxZGt0cTgKSE5BPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg=="
        #       }
        #     ]
        #   }
        }
        result = self.mgmt_client.tokens.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, token_name=TOKEN_NAME, token_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/post/RegistryGenerateCredentials[post]
#--------------------------------------------------------------------------
        BODY = {
          "token_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ContainerRegistry/registries/" + REGISTRY_NAME + "/tokens/" + TOKEN_NAME,
          "expiry": "2020-12-31T15:59:59.0707808Z"
        }
        result = self.mgmt_client.registries.begin_generate_credentials(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, generate_credentials_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tokens/delete/TokenDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tokens.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, token_name=TOKEN_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ScopeMaps/delete/ScopeMapDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.scope_maps.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, scope_map_name=SCOPE_MAP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_registries(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        # UNIQUE = resource_group.name[-4:]
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        TOKEN_NAME = "myToken"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Standard"
          },
          "admin_user_enabled": True
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/get/RegistryListPrivateLinkResources[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.list_private_link_resources(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Registries/get/RegistryListUsages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.list_usages(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Registries/get/RegistryGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Registries/get/RegistryListByResourceGroup[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Registries/get/RegistryList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.list()

#--------------------------------------------------------------------------
        # /Registries/post/Registries_GetBuildSourceUploadUrl[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.get_build_source_upload_url(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Registries/post/RegistryRegenerateCredential[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "password"
        }
        result = self.mgmt_client.registries.regenerate_credential(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, regenerate_credential_parameters=BODY)

#--------------------------------------------------------------------------
        # /Registries/post/RegistryListCredentials[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.list_credentials(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Registries/post/ImportImageByManifestDigest[post]
#--------------------------------------------------------------------------
        BODY = {
          "source": {
            "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ContainerRegistry/registries/" + REGISTRY_NAME,
            "source_image": "sourceRepository@sha256:0000000000000000000000000000000000000000000000000000000000000000"
          },
          "target_tags": [
            "targetRepository:targetTag"
          ],
          "untagged_target_repositories": [
            "targetRepository1"
          ],
          "mode": "Force"
        }
        # result = self.mgmt_client.registries.begin_import_image(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Registries/post/Registries_ScheduleRun_EncodedTaskRun[post]
#--------------------------------------------------------------------------
        BODY = {
          "type": "EncodedTaskRunRequest",
          "values": [
            {
              "name": "mytestargument",
              "value": "mytestvalue",
              "is_secret": False
            },
            {
              "name": "mysecrettestargument",
              "value": "mysecrettestvalue",
              "is_secret": True
            }
          ],
          "platform": {
            "os": "Linux"
          },
          "agent_configuration": {
            "cpu": "2"
          },
          "encoded_task_content": "c3RlcHM6Cnt7IGlmIFZhbHVlcy5lbnZpcm9ubWVudCA9PSAncHJvZCcgfX0KICAtIHJ1bjogcHJvZCBzZXR1cAp7eyBlbHNlIGlmIFZhbHVlcy5lbnZpcm9ubWVudCA9PSAnc3RhZ2luZycgfX0KICAtIHJ1bjogc3RhZ2luZyBzZXR1cAp7eyBlbHNlIH19CiAgLSBydW46IGRlZmF1bHQgc2V0dXAKe3sgZW5kIH19CgogIC0gcnVuOiBidWlsZCAtdCBGYW5jeVRoaW5nOnt7LlZhbHVlcy5lbnZpcm9ubWVudH19LXt7LlZhbHVlcy52ZXJzaW9ufX0gLgoKcHVzaDogWydGYW5jeVRoaW5nOnt7LlZhbHVlcy5lbnZpcm9ubWVudH19LXt7LlZhbHVlcy52ZXJzaW9ufX0nXQ==",
          "encoded_values_content": "ZW52aXJvbm1lbnQ6IHByb2QKdmVyc2lvbjogMQ=="
        }
        result = self.mgmt_client.registries.begin_schedule_run(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_request=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/patch/RegistryUpdate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Standard"
          },
          "admin_user_enabled": True
        }
        result = self.mgmt_client.registries.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/post/RegistryCheckNameAvailable[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "myRegistry",
          "type": "Microsoft.ContainerRegistry/registries"
        }
        result = self.mgmt_client.registries.check_name_availability(registry_name_check_request=BODY)

#--------------------------------------------------------------------------
        # /Operations/get/Operations_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.operations.list()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()
