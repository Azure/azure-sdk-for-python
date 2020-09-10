# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   WebApps: 33/372

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web_app(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "myname"
        APP_SERVICE_PLAN_NAME = "myappserviceplan"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "kind": "app",
          "location": AZURE_LOCATION,
          "sku": {
            "name": "P1",
            "tier": "Premium",
            "size": "P1",
            "family": "P",
            "capacity": "1"
          }
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=APP_SERVICE_PLAN_NAME, app_service_plan=BODY)
        service_farm = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": "East US 2",
        #   "serverFarmId": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/clitest.rg000001/providers/Microsoft.Web/serverfarms/webapp-linux-plan000002",
          "server_farm_id": service_farm.id,
          "reserved": False,
          "is_xenon": False,
          "hyper_v": False,
          "site_config": {
            "net_framework_version":"v4.6",
            "linux_fx_version": "node|10.16",
            "app_settings": [],
            "always_on": True,
            "local_my_sql_enabled": False,
            "http20_enabled": True
          },
          "scm_site_also_stopped": False,
          "https_only": False
        }
        result = self.mgmt_client.web_apps.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, site_envelope=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Approves or rejects a private endpoint connection for a site.[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Approved by admin.",
            "actions_required": ""
          }
        }
        # result = self.mgmt_client.web_apps.begin_approve_or_reject_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, private_endpoint_wrapper=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Update SCM Allowed[put]
#--------------------------------------------------------------------------
        BODY = {
          "allow": True
        }
        result = self.mgmt_client.web_apps.update_scm_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, csm_publishing_access_policies_entity=BODY)

#--------------------------------------------------------------------------
        # /WebApps/put/Update FTP Allowed[put]
#--------------------------------------------------------------------------
        BODY = {
          "allow": True
        }
        result = self.mgmt_client.web_apps.update_ftp_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, csm_publishing_access_policies_entity=BODY)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get FTP Allowed[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_ftp_allowed(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get SCM Allowed[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_scm_allowed(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get a private endpoint connection for a site.[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get Azure Key Vault app setting reference[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_app_setting_key_vault_reference(resource_group_name=RESOURCE_GROUP, name=NAME, config_name=CONFIG_NAME, app_setting_key=APP_SETTING_KEY)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get site instance info[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_instance_info(resource_group_name=RESOURCE_GROUP, name=NAME, instance_id=INSTANCE_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get Azure Key Vault references for app settings[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_app_settings_key_vault_references(resource_group_name=RESOURCE_GROUP, name=NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/List Publishing Credentials Policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_basic_publishing_credentials_policies(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get site instance info[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.get_instance_info(resource_group_name=RESOURCE_GROUP, name=NAME, instance_id=INSTANCE_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get private link resources of a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_private_link_resources(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        # result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        # result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        # result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/List backups[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_site_backups(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Copy slot[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_slot": "staging",
          "site_config": {
            "number_of_workers": "1",
            "http_logging_enabled": True
          }
        }
        result = self.mgmt_client.web_apps.begin_copy_production_slot(resource_group_name=RESOURCE_GROUP, name=NAME, copy_slot_entity=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        # result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/List backups[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_site_backups(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Copy slot[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_slot": "staging",
          "site_config": {
            "number_of_workers": "1",
            "http_logging_enabled": True
          }
        }
        result = self.mgmt_client.web_apps.begin_copy_production_slot(resource_group_name=RESOURCE_GROUP, name=NAME, copy_slot_entity=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/delete/Delete a private endpoint connection for a site.[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.web_apps.begin_delete_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        # result = result.result()
