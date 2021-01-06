# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   WebApps: 31/372

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

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web_app_slot(self, resource_group):
        # covered: 15

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "mysitexxyzz"
        SLOT_NAME = "staging"
        APP_SERVICE_PLAN_NAME = "myappserviceplan"
        SITE_SOURCE_CONTROL = "web"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S1",
            "tier": "STANDARD",
            "capacity": "1"
          },
          "per_site_scaling": False,
          "is_xenon": False
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=APP_SERVICE_PLAN_NAME, app_service_plan=BODY)
        service_farm = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "server_farm_id": service_farm.id,
          "reserved": False,
          "is_xenon": False,
          "hyper_v": False,
          "site_config": {
            "net_framework_version":"v4.6",
            "app_settings": [
              {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "10.14"}
            ],
            "local_my_sql_enabled": False,
            "http20_enabled": True
          },
          "scm_site_also_stopped": False,
          "https_only": False
        }
        result = self.mgmt_client.web_apps.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, site_envelope=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/CreateSlot[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "properties": {
            "server_farm_id": service_farm.id,
            "reserved": False,
            "is_xenon": False,
            "hyper_v": False,
            "site_config": {
              "net_framework_version": "v4.6",
              "local_my_sql_enabled": False,
              "http20_enabled": True
            },
            "scm_site_also_stopped": False
          }
        }
        result = self.mgmt_client.web_apps.begin_create_or_update_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_envelope=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/CreateConfigurationSlot[put]
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "number_of_workers": 1,
            "default_documents": [
              "Default.htm",
              "Default.html",
              "Default.asp",
              "index.htm",
              "index.html",
              "iisstart.htm",
              "default.aspx",
              "index.php",
              "hostingstart.html"
            ],
            "net_framework_version": "v3.5",
            "php_version": "7.2",
            "python_version": "3.4",
            "node_version": "",
            "power_shell_version": "",
            "linux_fx_version": "",
            "request_tracing_enabled": False,
            "remote_debugging_enabled": False,
            "http_logging_enabled": False,
            "logs_directory_size_limit": 35,
            "detailed_error_logging_enabled": False,
            "publishing_username": "$webapp-config-test000002",
            "scm_type": "None",
            "use32_bit_worker_process": False,
            "webSocketsEnabled": True,
            "always_on": True,
            "app_command_line": "",
            "managed_pipeline_mode": "Integrated",
            "virtual_applications": [
              {
                "virtual_path": "/",
                "physical_path": "site\\wwwroot",
                "preload_enabled": True
              }
            ],
            "load_balancing": "LeastRequests",
            "experiments": {
              "ramp_up_rules": []
            },
            "auto_heal_enabled": True,
            "vnet_name": "",
            "local_my_sql_enabled": False,
            "ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions_use_main": False,
            "http20_enabled": True,
            "min_tls_version": "1.0",
            "ftps_state": "Disabled",
            "preWarmedInstanceCount": 0
          }
        }
        result = self.mgmt_client.web_apps.create_or_update_configuration_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_config=BODY)

#--------------------------------------------------------------------------
        # /WebApps/put/CreateSourceControlSlot[put]
#--------------------------------------------------------------------------
        BODY = {
          "repo_url": "https://github.com/00Kai0/azure-site-test",
          "branch": "staging",
          "is_manual_integration": True,
          "is_mercurial": False
        }
        result = self.mgmt_client.web_apps.begin_create_or_update_source_control_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_source_control=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/get/GetSlot[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/GetConfigurationSlot[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_configuration_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/GetSlot[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_slots(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/GetSourceControlSlot[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_source_control_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/patch/UpdateSlot[patch]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "properties": {
            "server_farm_id": service_farm.id,
            "reserved": False,
            "is_xenon": False,
            "hyper_v": False,
            "site_config": {
              "net_framework_version": "v4.6",
              "local_my_sql_enabled": False,
              "http20_enabled": True
            },
            "scm_site_also_stopped": False
          }
        }
        result = self.mgmt_client.web_apps.update_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_envelope=BODY)

#--------------------------------------------------------------------------
        # /WebApps/patch/UpdateConfigurationSlot
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "number_of_workers": 1,
            "default_documents": [
              "Default.htm",
              "Default.html",
              "Default.asp",
              "index.htm",
              "index.html",
              "iisstart.htm",
              "default.aspx",
              "index.php",
              "hostingstart.html"
            ],
            "net_framework_version": "v3.5",
            "php_version": "7.2",
            "python_version": "3.4",
            "node_version": "",
            "power_shell_version": "",
            "linux_fx_version": "",
            "request_tracing_enabled": False,
            "remote_debugging_enabled": False,
            "http_logging_enabled": False,
            "logs_directory_size_limit": 35,
            "detailed_error_logging_enabled": False,
            "publishing_username": "$webapp-config-test000002",
            "scm_type": "None",
            "use32_bit_worker_process": False,
            "webSocketsEnabled": True,
            "always_on": True,
            "app_command_line": "",
            "managed_pipeline_mode": "Integrated",
            "virtual_applications": [
              {
                "virtual_path": "/",
                "physical_path": "site\\wwwroot",
                "preload_enabled": True
              }
            ],
            "load_balancing": "LeastRequests",
            "experiments": {
              "ramp_up_rules": []
            },
            "auto_heal_enabled": True,
            "vnet_name": "",
            "local_my_sql_enabled": False,
            "ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions_use_main": False,
            "http20_enabled": True,
            "min_tls_version": "1.0",
            "ftps_state": "Disabled",
            "preWarmedInstanceCount": 0
          }
        }
        result = self.mgmt_client.web_apps.update_configuration_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_config=BODY)

#--------------------------------------------------------------------------
        # /WebApps/patch/UpdateSourceControlSlot[patch]
#--------------------------------------------------------------------------
        BODY ={
          "repo_url": "https://github.com/00Kai0/azure-site-test",
          "branch": "staging",
          "is_manual_integration": True,
          "is_mercurial": False
        }
        result = self.mgmt_client.web_apps.update_source_control_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME, site_source_control=BODY)

#--------------------------------------------------------------------------
        # /WebApps/post/StartSlot
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.start_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/RestartSlot
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.restart_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/StopSlot
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/delete/DeleteSourceControlSlot[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.delete_source_control_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/delete/DeleteSlot[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.delete_slot(resource_group_name=RESOURCE_GROUP, name=NAME, slot=SLOT_NAME)

#--------------------------------------------------------------------------
        # /WebApps/delete/Delete
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.delete(resource_group_name=RESOURCE_GROUP, name=NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web_app(self, resource_group):
        # coverd: 16

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "mysitexxyzz"
        APP_SERVICE_PLAN_NAME = "myappserviceplan"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "B1",
            "tier": "BASIC",
            "capacity": "1"
          },
          "per_site_scaling": False,
          "is_xenon": False
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=APP_SERVICE_PLAN_NAME, app_service_plan=BODY)
        service_farm = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "server_farm_id": service_farm.id,
          "reserved": False,
          "is_xenon": False,
          "hyper_v": False,
          "site_config": {
            "net_framework_version":"v4.6",
            "app_settings": [
              {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "10.14"}
            ],
            "local_my_sql_enabled": False,
            "http20_enabled": True
          },
          "scm_site_also_stopped": False,
          "https_only": False
        }
        result = self.mgmt_client.web_apps.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, site_envelope=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/CreateConfig[put]
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "number_of_workers": 1,
            "default_documents": [
              "Default.htm",
              "Default.html",
              "Default.asp",
              "index.htm",
              "index.html",
              "iisstart.htm",
              "default.aspx",
              "index.php",
              "hostingstart.html"
            ],
            "net_framework_version": "v3.5",
            "php_version": "7.2",
            "python_version": "3.4",
            "node_version": "",
            "power_shell_version": "",
            "linux_fx_version": "",
            "request_tracing_enabled": False,
            "remote_debugging_enabled": False,
            "http_logging_enabled": False,
            "logs_directory_size_limit": 35,
            "detailed_error_logging_enabled": False,
            "publishing_username": "$webapp-config-test000002",
            "scm_type": "None",
            "use32_bit_worker_process": False,
            "webSocketsEnabled": True,
            "always_on": True,
            "app_command_line": "",
            "managed_pipeline_mode": "Integrated",
            "virtual_applications": [
              {
                "virtual_path": "/",
                "physical_path": "site\\wwwroot",
                "preload_enabled": True
              }
            ],
            "load_balancing": "LeastRequests",
            "experiments": {
              "ramp_up_rules": []
            },
            "auto_heal_enabled": True,
            "vnet_name": "",
            "local_my_sql_enabled": False,
            "ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions_use_main": False,
            "http20_enabled": True,
            "min_tls_version": "1.0",
            "ftps_state": "Disabled",
            "preWarmedInstanceCount": 0
          }
        }
        result = self.mgmt_client.web_apps.create_or_update_configuration(resource_group_name=RESOURCE_GROUP, name=NAME, site_config=BODY)

#--------------------------------------------------------------------------
        # /WebApps/put/CreateSourceControl[put]
#--------------------------------------------------------------------------
        BODY = {
          "repo_url": "https://github.com/00Kai0/azure-site-test",
          "branch": "staging",
          "is_manual_integration": True,
          "is_mercurial": False
        }
        result = self.mgmt_client.web_apps.begin_create_or_update_source_control(resource_group_name=RESOURCE_GROUP, name=NAME, site_source_control=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/get/GetConfig
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_configuration(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/GetSourceControl
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_source_control(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/List
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list()

#--------------------------------------------------------------------------
        # /WebApps/get/ListConfig
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_configurations(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/patch/Update[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
        #   "serverFarmId": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/clitest.rg000001/providers/Microsoft.Web/serverfarms/webapp-linux-plan000002",
          "server_farm_id": service_farm.id,
          "reserved": False,
          "is_xenon": False,
          "hyper_v": False,
          "site_config": {
            "net_framework_version":"v4.6",
            "app_settings": [
              {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "10.14"}
            ],
            "local_my_sql_enabled": False,
            "http20_enabled": True
          },
          "scm_site_also_stopped": False,
          "https_only": False
        }
        result = self.mgmt_client.web_apps.update(resource_group_name=RESOURCE_GROUP, name=NAME, site_envelope=BODY)

#--------------------------------------------------------------------------
        # /WebApps/patch/UpdateConfig[put]
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "number_of_workers": 1,
            "default_documents": [
              "Default.htm",
              "Default.html",
              "Default.asp",
              "index.htm",
              "index.html",
              "iisstart.htm",
              "default.aspx",
              "index.php",
              "hostingstart.html"
            ],
            "net_framework_version": "v3.5",
            "php_version": "7.2",
            "python_version": "3.4",
            "node_version": "",
            "power_shell_version": "",
            "linux_fx_version": "",
            "request_tracing_enabled": False,
            "remote_debugging_enabled": False,
            "http_logging_enabled": False,
            "logs_directory_size_limit": 35,
            "detailed_error_logging_enabled": False,
            "publishing_username": "$webapp-config-test000002",
            "scm_type": "None",
            "use32_bit_worker_process": False,
            "webSocketsEnabled": True,
            "always_on": True,
            "app_command_line": "",
            "managed_pipeline_mode": "Integrated",
            "virtual_applications": [
              {
                "virtual_path": "/",
                "physical_path": "site\\wwwroot",
                "preload_enabled": True
              }
            ],
            "load_balancing": "LeastRequests",
            "experiments": {
              "ramp_up_rules": []
            },
            "auto_heal_enabled": True,
            "vnet_name": "",
            "local_my_sql_enabled": False,
            "ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions": [
              {
                "ip_address": "Any",
                "action": "Allow",
                "priority": 1,
                "name": "Allow all",
                "description": "Allow all access"
              }
            ],
            "scm_ip_security_restrictions_use_main": False,
            "http20_enabled": True,
            "min_tls_version": "1.0",
            "ftps_state": "Disabled",
            "preWarmedInstanceCount": 0
          }
        }
        result = self.mgmt_client.web_apps.update_configuration(resource_group_name=RESOURCE_GROUP, name=NAME, site_config=BODY)

 #--------------------------------------------------------------------------
        # /WebApps/patch/UpdateSourceControl[put]
#--------------------------------------------------------------------------
        BODY = {
          "repo_url": "https://github.com/00Kai0/azure-site-test",
          "branch": "staging",
          "is_manual_integration": True,
          "is_mercurial": False
        }
        result = self.mgmt_client.web_apps.update_source_control(resource_group_name=RESOURCE_GROUP, name=NAME, site_source_control=BODY)

#--------------------------------------------------------------------------
        # /WebApps/post/Start
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.start(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Restart
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.restart(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Stop
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/delete/DeleteSourceControl
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.delete_source_control(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/delete/Delete
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.delete(resource_group_name=RESOURCE_GROUP, name=NAME)

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web_app_backup(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "mysitexxyzz"
        APP_SERVICE_PLAN_NAME = "myappserviceplan"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "B1",
            "tier": "BASIC",
            "capacity": "1"
          },
          "per_site_scaling": False,
          "is_xenon": False
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=APP_SERVICE_PLAN_NAME, app_service_plan=BODY)
        service_farm = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Create[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
        #   "serverFarmId": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/clitest.rg000001/providers/Microsoft.Web/serverfarms/webapp-linux-plan000002",
          "server_farm_id": service_farm.id,
          "reserved": False,
          "is_xenon": False,
          "hyper_v": False,
          "site_config": {
            "net_framework_version":"v4.6",
            "app_settings": [
              {"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": "10.14"}
            ],
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

#--------------------------------------------------------------------------
        # /WebApps/delete/Delete
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_delete(resource_group_name=RESOURCE_GROUP, name=NAME)
        result = result.result()
