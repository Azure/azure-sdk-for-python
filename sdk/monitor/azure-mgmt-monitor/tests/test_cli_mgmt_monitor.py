# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 63
# Methods Covered : 63
# Examples Total  : 87
# Examples Tested : 87
# Coverage %      : 100
# ----------------------

# covered ops:
#   action_groups: 7/7
#   activity_log_alerts: 6/6
#   activity_logs: 1/1
#   autoscale_settings: 6/6
#   baselines: 1/1
#   alert_rule_incidents: 0/2  # TODO: cannot test it in this sub
#   alert_rules: 0/6  # TODO: cannot test it in this sub
#   baseline: 0/1  # TODO: need check whether it is outdated
#   diagnostic_settings: 4/4
#   diagnostic_settings_category: 2/2
#   guest_diagnostics_settings: 0/6  TODO: InvalidResourceType, it seems like outdated
#   guest_diagnostics_settings_association: 0/6  TODO: InvalidResourceType, it seems like outdated
#   event_categories: 1/1
#   log_profiles: 5/5
#   metric_alerts: 6/6
#   metric_alerts_status: 2/2
#   metric_baseline: 0/2  TODO: bad request
#   metric_definitions: 1/1
#   metric_namespaces: 1/1
#   metrics: 1/1
#   operations: 1/1
#   scheduled_query_rules: 6/6
#   service_diagnostic_settings: 0/3 TODO: InvalidResourceType, it seems like outdated
#   tenant_activity_logs: 1/1
#   vm_insights: 1/1

import time
import unittest

import azure.mgmt.monitor
import azure.mgmt.monitor.models
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMonitorClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMonitorClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.monitor.MonitorManagementClient
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
            from azure.mgmt.web import WebSiteManagementClient
            self.web_client = self.create_mgmt_client(
                WebSiteManagementClient
            )
            from azure.mgmt.compute import ComputeManagementClient
            self.vm_client = self.create_mgmt_client(
                ComputeManagementClient
            )
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )
            from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
            self.insight_client = self.create_mgmt_client(
                ApplicationInsightsManagementClient
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
    def create_site(self, group_name, location, site_name, app_service_plan_name):
        # server_farm_async_operation = self.web_client.app_service_plans.create_or_update(
        #     group_name,
        #     app_service_plan_name,
        #     azure.mgmt.web.models.AppServicePlan(
        #         location=location,
        #         sku=azure.mgmt.web.models.SkuDescription(
        #             name='S1',
        #             capacity=1,
        #             tier='Standard'
        #         )
        #     )
        # )
        # server_farm = server_farm_async_operation.result()

        # Create a Site to be hosted in the Server Farm
        site_async_operation = self.web_client.web_apps.create_or_update(
            group_name,
            site_name,
            azure.mgmt.web.models.Site(
                location=self.region,
                # server_farm_id=server_farm.id
            )
        )
        site = site_async_operation.result()
        return site

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

    # use track 1 version
    def create_vm(
        self,
        group_name,
        location,
        vm_name,
        network_name,
        subnet_name,
        interface_name
    ):

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

    # use track 1 version
    def create_vmss(
        self,
        group_name,
        location,
        vmss_name,
        network_name,
        subnet_name,
        interface_name
    ):
        subnet = self.create_virtual_network(group_name, location, network_name, subnet_name)
        NIC_ID = self.create_network_interface(group_name, location, interface_name, subnet)

        # Create a scale set with empty data disks on each vm.[put]
        BODY = {
          "sku": {
            "tier": "Standard",
            "capacity": "2",
            "name": "Standard_D1_v2"
          },
          "location": location,
          "overprovision": True,
          "virtual_machine_profile": {
            "storage_profile": {
              "image_reference": {
                  "offer": "UbuntuServer",
                  "publisher": "Canonical",
                  "sku": "18.04-LTS",
                  "version": "latest"
              },
              "os_disk": {
                "caching": "ReadWrite",
                "managed_disk": {
                  "storage_account_type": "Standard_LRS"
                },
                "create_option": "FromImage",
                "disk_size_gb": "512"
              }
            },
            "os_profile": {
              "computer_name_prefix": "testPC",
              "admin_username": "testuser",
              "admin_password": "Aa!1()-xyz"
            },
            "network_profile": {
              "network_interface_configurations": [
                {
                  "name": "testPC",
                  "primary": True,
                  "enable_ipforwarding": True,
                  "ip_configurations": [
                    {
                      "name": "testPC",
                      "properties": {
                        "subnet": {
                          # "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
                          "id": subnet.id
                        }
                      }
                    }
                  ]
                }
              ]
            }
          },
          "upgrade_policy": {
            "mode": "Manual"
          },
          "upgrade_mode": "Manual"
        }
        result = self.vm_client.virtual_machine_scale_sets.create_or_update(group_name, vmss_name, BODY)
        vmss = result.result()

        return vmss

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
          # "workspace_id": "",
          "workspace_id": workspace_id,
          # "event_hub_authorization_rule_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/microsoft.eventhub/namespaces/" + NAMESPACE_NAME + "/eventhubs/" + EVENTHUB_NAME + "/authorizationrules/" + AUTHORIZATIONRULE_NAME + "",
          "event_hub_authorization_rule_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/microsoft.eventhub/namespaces/" + NAMESPACE_NAME + "/authorizationrules/" + AUTHORIZATIONRULE_NAME,
          "event_hub_name": EVENTHUB_NAME,
          "metrics": [
            # {
            #   "category": "WorkflowMetrics",
            #   "enabled": True,
            #   "retention_policy": {
            #     "enabled": False,
            #     "days": "0"
            #   }
            # }
          ],
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
          # "log_analytics_destination_type": "Dedicated"
        }
        diagnostic_settings = self.mgmt_client.diagnostic_settings.create_or_update(RESOURCE_URI, INSIGHT_NAME, BODY)

        # TODO: resourceGroups has been changed to resourcegroups
        RESOURCE_URI = "subscriptions/{sub}/resourcegroups/{group}/providers/microsoft.logic/workflows/{workflow}".format(
            sub=SUBSCRIPTION_ID,
            group=RESOURCE_GROUP,
            workflow=WORKFLOW_NAME
        )

        # List diagnostic settings categories
        categories = self.mgmt_client.diagnostic_settings_category.list(RESOURCE_URI) 

        # List diagnostic settings[get]
        result = self.mgmt_client.diagnostic_settings.list(RESOURCE_URI)

        # Gets the diagnostic setting[get]
        result = self.mgmt_client.diagnostic_settings.get(RESOURCE_URI, INSIGHT_NAME)

        # Get diagnostic settings category
        self.mgmt_client.diagnostic_settings_category.get(RESOURCE_URI, categories.value[0].name) 

        # Deletes the diagnostic setting[delete]
        result = self.mgmt_client.diagnostic_settings.delete(RESOURCE_URI, INSIGHT_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_log_profiles(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        LOGPROFILE_NAME  = self.get_resource_name("logprofilex")
        STORAGE_ACCOUNT_NAME = self.get_resource_name("storageaccountx")

        if self.is_live:
            storage_account_id = self.create_storage_account(RESOURCE_GROUP, AZURE_LOCATION, STORAGE_ACCOUNT_NAME)
        else:
            storage_account_id = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME

        # Create or update a log profile[put]
        BODY = {
          "location": "",
          "locations": [
            "global"
          ],
          "categories": [
            "Write",
            "Delete",
            "Action"
          ],
          "retention_policy": {
            "enabled": True,
            "days": "3"
          },
          # "storage_account_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "storage_account_id": storage_account_id,
          # "service_bus_rule_id": ""
        }
        result = self.mgmt_client.log_profiles.create_or_update(LOGPROFILE_NAME, BODY)

        if self.is_live:
            time.sleep(30)

        # Get log profile[get]
        result = self.mgmt_client.log_profiles.get(LOGPROFILE_NAME)

        # List log profiles[get]
        result = self.mgmt_client.log_profiles.list()

        # TODO: azure.core.exceptions.HttpResponseError: (Method not allowed) Exception of type 'Microsoft.WindowsAzure.Management.Monitoring.MonitoringServiceException' was thrown.
        # Update a log profile[patch]
        # BODY = {
        #   "locations": [
        #     "global"
        #   ],
        #   "categories": [
        #     "Write",
        #     "Delete",
        #     "Action"
        #   ],
        #   "retention_policy": {
        #     "enabled": True,
        #     "days": "3"
        #   }
        # }
        # result = self.mgmt_client.log_profiles.update(LOGPROFILE_NAME, BODY)

        # Delete log profile[delete]
        result = self.mgmt_client.log_profiles.delete(LOGPROFILE_NAME)

    @unittest.skip("cannot create or modify classic metric alerts")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_alert_rule(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        APP_SERVICE_PLAN_NAME = self.get_resource_name('pyarmappserviceplan')
        SITE_NAME = self.get_resource_name('pyarmsite')
        ALERTRULE_NAME = rule_name = self.get_resource_name('alertrule')
        # site = self.create_site(RESOURCE_GROUP, AZURE_LOCATION, SITE_NAME, APP_SERVICE_PLAN_NAME)
        VM_NAME = "vm_name"
        NETWORK_NAME = "networkxx"
        SUBNET_NAME = "subnetx"
        INTERFACE_NAME = "interfacexx"

        if self.is_live:
            vm = self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VM_NAME, NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
            resource_id = vm.id
        else:
            resource_id = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VM_NAME

        # I need a subclass of "RuleDataSource"
        data_source = azure.mgmt.monitor.models.RuleMetricDataSource(
            resource_uri=resource_id,
            metric_name='CPU Credits Consumed'
        )

        # I need a subclasses of "RuleCondition"
        rule_condition = azure.mgmt.monitor.models.ThresholdRuleCondition(
            data_source=data_source,
            operator='GreaterThanOrEqual',
            threshold=90,
            window_size='PT5M',
            time_aggregation='Average'
        )

        # I need a subclass of "RuleAction"
        rule_action = azure.mgmt.monitor.models.RuleEmailAction(
            send_to_service_owners=True,
            custom_emails=[
                'monitoringemail@microsoft.com'
            ]
        )

        # TODO: You cannot create or modify classic metric alerts for this subscription as this subscription 92f95d8f-3c67-4124-91c7-8cf07cdbf241 is being migrated or has been migrated to use new metric alerts. Learn more - aka.ms/alertclassicretirement
        my_alert = self.mgmt_client.alert_rules.create_or_update(
            resource_group.name,
            rule_name,
            {
                'location': AZURE_LOCATION,
                'name_properties_name': rule_name,
                'description': 'Testing Alert rule creation',
                'is_enabled': True,
                'condition': rule_condition,
                'actions': [
                    # rule_action
                ]
            }
        )

        # Get an alert rule[get]
        result = self.mgmt_client.alert_rules.get(resource_group.name, ALERTRULE_NAME)

        # List alert rules[get]
        result = self.mgmt_client.alert_rules.list_by_resource_group(resource_group.name)

        # List alert rule incidents
        incidents = self.mgmt_client.alert_rule_incidents.list_by_alert_rule(resource_group.name, ALERTRULE_NAME)

        # Get alert rule incident
        result = self.mgmt_client.alert_rule_incidents.get(resource_group.name, ALERTRULE_NAME, incidents.value[0].name)

        # List alert rules[get]
        result = self.mgmt_client.alert_rules.list_by_subscription(resource_group.name)

        # TODO: fix later
        # Patch an alert rule[patch]
        # BODY = {
        #   "name": "chiricutin",
        #   "description": "Pura Vida",
        #   "is_enabled": True,
        #   "condition": {
        #     "odata.type": "Microsoft.Azure.Management.Insights.Models.ThresholdRuleCondition",
        #     # "data_source": {
        #     #   "odata.type": "Microsoft.Azure.Management.Insights.Models.RuleMetricDataSource",
        #     #   # "resource_uri": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Web/sites/" + SITE_NAME + "",
        #     #   "resource_uri": site.id,
        #     #   "metric_name": "Requests"
        #     # },
        #     "operator": "GreaterThan",
        #     "threshold": "3",
        #     "window_size": "PT5M",
        #     "time_aggregation": "Total"
        #   },
        #   # "last_updated_time": "2016-11-23T21:23:52.0221265Z",
        #   "actions": []
        # }
        # result = self.mgmt_client.alert_rules.update(resource_group.name, ALERTRULE_NAME, BODY)

        # Delete an alert rulte[delete]
        result = self.mgmt_client.alert_rules.delete(resource_group.name, ALERTRULE_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_metric_alerts(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        METRIC_ALERT_NAME = "metricnamexx"
        VM_NAME = "vm_name"
        NETWORK_NAME = "networkxx"
        SUBNET_NAME = "subnetx"
        INTERFACE_NAME = "interfacexx"
        INSIGHT_NAME = "PercentageCPU"

        if self.is_live:
            vm = self.create_vm(RESOURCE_GROUP, AZURE_LOCATION, VM_NAME, NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
            RESOURCE_URI = vm.id
        else:
            RESOURCE_URI = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachines/" + VM_NAME

        # Get a list of operations for a resource provider[get]
        result = self.mgmt_client.operations.list()

        # Create or update a metric alert[put]
        BODY = {
          "location": "global",
          "description": "This is the description of the rule1",
          "severity": "3",
          "enabled": True,
          "scopes": [
            # "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/gigtest/providers/Microsoft.Compute/virtualMachines/gigwadme"
            RESOURCE_URI
          ],
          "evaluation_frequency": "PT1M",
          "window_size": "PT15M",
          "target_resource_type": "Microsoft.Compute/virtualMachines",
          "target_resource_region": "southcentralus",
          "criteria": {
            "odata.type": "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria",
            "all_of": [
              {
                "criterion_type": "DynamicThresholdCriterion",
                "name": "High_CPU_80",
                "metric_name": "Percentage CPU",
                "metric_namespace": "microsoft.compute/virtualmachines",
                "operator": "GreaterOrLessThan",
                "time_aggregation": "Average",
                "dimensions": [],
                "alert_sensitivity": "Medium",
                "failing_periods": {
                  "number_of_evaluation_periods": "4",
                  "min_failing_periods_to_alert": "4"
                },
                # "ignore_data_before": "2019-04-04T21:00:00Z"
              }
            ]
          },
          "auto_mitigate": False,
          "actions": [
            # {
            #   "action_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/microsoft.insights/notificationgroups/" + NOTIFICATIONGROUP_NAME + "",
            #   "web_hook_properties": {
            #     "key11": "value11",
            #     "key12": "value12"
            #   }
            # }
          ]
        }
        result = self.mgmt_client.metric_alerts.create_or_update(resource_group.name, METRIC_ALERT_NAME, BODY)

        if self.is_live:
            time.sleep(30)

        # Get a web test alert rule[get]
        result = self.mgmt_client.metric_alerts.get(resource_group.name, METRIC_ALERT_NAME)

        # List metric alerts status
        alerts_status = self.mgmt_client.metric_alerts_status.list(resource_group.name, METRIC_ALERT_NAME)

        # Get an alert rule status[get]
        STATUS_NAME = alerts_status.value[0].name
        result = self.mgmt_client.metric_alerts_status.list_by_name(resource_group.name, METRIC_ALERT_NAME, STATUS_NAME)

        # List metric alert rules[get]
        result = self.mgmt_client.metric_alerts.list_by_resource_group(resource_group.name)
    
        # List metric alert rules[get]
        result = self.mgmt_client.metric_alerts.list_by_subscription()

        # Get Metric Definitions without filter[get]
        result = self.mgmt_client.metric_definitions.list(RESOURCE_URI, INSIGHT_NAME)

        # Get Metric Namespaces without filter[get]
        result = self.mgmt_client.metric_namespaces.list(RESOURCE_URI, INSIGHT_NAME)

        # Get onboarding status
        result = self.mgmt_client.vm_insights.get_onboarding_status(RESOURCE_URI)

        # Get event categories[get]
        result = self.mgmt_client.event_categories.list()

        # List metrics
        result = self.mgmt_client.metrics.list(RESOURCE_URI)

        # Get metric baselines[get]
        result = self.mgmt_client.baselines.list(RESOURCE_URI, INSIGHT_NAME)

        # TODO: outdated
        # Get metric baseline[get]
        # result = self.mgmt_client.baseline.get(RESOURCE_URI)

        # TODO: Operation returned an invalid status 'Bad Request'
        # Get Metric for data[get]
        # result = self.mgmt_client.metric_baseline.get(RESOURCE_URI, INSIGHT_NAME)

        # TODO: outdated
        # Calculate baseline[post]
        # BODY = {
        #   "sensitivities": [
        #     # "Low",
        #     INSIGHT_NAME
        #   ],
        #   "values": [
        #     "0",
        #     "62"
        #   ]
        # }
        # result = self.mgmt_client.metric_baseline.calculate_baseline(RESOURCE_URI, BODY)

        # TODO: fix later
        # Update a metric alert[put]
        # BODY = {
        #   "location": "global",
        #   "description": "This is the description of the rule1",
        #   "severity": "3",
        #   "enabled": True,
        #   "scopes": [
        #     vm.id
        #   ],
        #   "evaluation_frequency": "PT1M",
        #   "window_size": "PT15M",
        #   "target_resource_type": "Microsoft.Compute/virtualMachines",
        #   "target_resource_region": "southcentralus",
        #   "criteria": {
        #     "odata.type": "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria",
        #     "all_of": [
        #       {
        #         "criterion_type": "DynamicThresholdCriterion",
        #         "name": "High_CPU_80",
        #         "metric_name": "Percentage CPU",
        #         "metric_namespace": "microsoft.compute/virtualmachines",
        #         "operator": "GreaterOrLessThan",
        #         "time_aggregation": "Average",
        #         "dimensions": [],
        #         "alert_sensitivity": "Medium",
        #         "failing_periods": {
        #           "number_of_evaluation_periods": "4",
        #           "min_failing_periods_to_alert": "4"
        #         }
        #       }
        #     ]
        #   },
        #   "auto_mitigate": False,
        #   "actions": []
        # }
        # result = self.mgmt_client.metric_alerts.update(resource_group.name, METRIC_ALERT_NAME, BODY)

        # Delete an alert rule[delete]
        result = self.mgmt_client.metric_alerts.delete(resource_group.name, METRIC_ALERT_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_action_groups(self, resource_group):

        ACTION_GROUP_NAME = self.get_resource_name("actiongroup")
        
        # Create or update an action group[put]
        BODY = {
          "location": "Global",
          "group_short_name": "sample",
          "enabled": True,
          "email_receivers": [
            {
              "name": "John Doe's email",
              "email_address": "johndoe@email.com",
              "use_common_alert_schema": False
            }
          ],
          "sms_receivers": [
            {
              "name": "John Doe's mobile",
              "country_code": "1",
              "phone_number": "1234567890"
            }
          ]
        }
        result = self.mgmt_client.action_groups.create_or_update(resource_group.name, ACTION_GROUP_NAME, BODY)

        # Get an action group[get]
        result = self.mgmt_client.action_groups.get(resource_group.name, ACTION_GROUP_NAME)

        # List action groups[get]
        result = self.mgmt_client.action_groups.list_by_resource_group(resource_group.name)

        # List action groups[get]
        result = self.mgmt_client.action_groups.list_by_subscription_id()

        # Enable the receiver[post]
        BODY = {
          "receiver_name": "John Doe's mobile"
        }
        result = self.mgmt_client.action_groups.enable_receiver(resource_group.name, ACTION_GROUP_NAME, BODY)

        # Patch an action group[patch]
        BODY = {
          "tags": {
            "key1": "value1",
            "key2": "value2"
          },
          "properties": {
            "enabled": False
          }
        }
        result = self.mgmt_client.action_groups.update(resource_group.name, ACTION_GROUP_NAME, BODY)

        # Delete an action group[delete]
        result = self.mgmt_client.action_groups.delete(resource_group.name, ACTION_GROUP_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_activity_log_alerts(self, resource_group):
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        ACTIVITY_LOG_ALERT_NAME = self.get_resource_name("activitylogalertx")

        # Create or update an activity log alert[put]
        BODY = {
          "location": "Global",
          "scopes": [
            "subscriptions/" + SUBSCRIPTION_ID
          ],
          "enabled": True,
          "condition": {
            "all_of": [
              {
                "field": "category",
                "equals": "Administrative"
              },
              {
                "field": "level",
                "equals": "Error"
              }
            ]
          },
          "actions": {
            "action_groups": [
              # {
              #   "action_group_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/microsoft.insights/actionGroups/" + ACTION_GROUP_NAME + "",
              #   "webhook_properties": {
              #     "sample_webhook_property": "samplePropertyValue"
              #   }
              # }
            ]
          },
          "description": "Sample activity log alert description"
        }
        result = self.mgmt_client.activity_log_alerts.create_or_update(resource_group.name, ACTIVITY_LOG_ALERT_NAME, BODY)

        # Get an activity log alert[get]
        result = self.mgmt_client.activity_log_alerts.get(resource_group.name, ACTIVITY_LOG_ALERT_NAME)

        # List activity log alerts[get]
        result = self.mgmt_client.activity_log_alerts.list_by_resource_group(resource_group.name)

        # List activity log alerts by subscription[get]
        result = self.mgmt_client.activity_log_alerts.list_by_subscription_id()

        # List activity_logs[get]
        FILTER = "resourceGroupName eq '{}'".format(resource_group.name)
        result = self.mgmt_client.activity_logs.list(FILTER)

        
        # List tenant activity logs
        FILTER = "resourceGroupName eq '{}'".format(resource_group.name)
        result = self.mgmt_client.tenant_activity_logs.list(FILTER)

        # Patch an activity log alert[patch]
        BODY = {
          "tags": {
            "key1": "value1",
            "key2": "value2"
          },
          "properties": {
            "enabled": False
          }
        }
        result = self.mgmt_client.activity_log_alerts.update(resource_group.name, ACTIVITY_LOG_ALERT_NAME, BODY)

        # Delete an activity log alert[delete]
        result = self.mgmt_client.activity_log_alerts.delete(resource_group.name, ACTIVITY_LOG_ALERT_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_autoscale_settings(self, resource_group):
        
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        AUTOSCALESETTING_NAME = "autoscalesetting"
        VMSS_NAME = "vmss_name"
        NETWORK_NAME = "networkxx"
        SUBNET_NAME = "subnetx"
        INTERFACE_NAME = "interfacexx"

        if self.is_live:
            vmss = self.create_vmss(RESOURCE_GROUP, AZURE_LOCATION, VMSS_NAME, NETWORK_NAME, SUBNET_NAME, INTERFACE_NAME)
            vmss_id = vmss.id
        else:
            vmss_id = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Compute/virtualMachineScaleSets/" + VMSS_NAME

        # Create or update an autoscale setting[put]
        BODY = {
          "location": "West US",
          "profiles": [
            {
              "name": "adios",
              "capacity": {
                "minimum": "1",
                "maximum": "10",
                "default": "1"
              },
              "rules": [
              ]
            }
          ],
          "enabled": True,
          "target_resource_uri": vmss_id,
          "notifications": [
            {
              "operation": "Scale",
              "email": {
                "send_to_subscription_administrator": True,
                "send_to_subscription_co_administrators": True,
                "custom_emails": [
                  "gu@ms.com",
                  "ge@ns.net"
                ]
              },
              "webhooks": [
              ]
            }
          ]
        }
        result = self.mgmt_client.autoscale_settings.create_or_update(resource_group.name, AUTOSCALESETTING_NAME, BODY)
   
        # Get an autoscale setting[get]
        result = self.mgmt_client.autoscale_settings.get(resource_group.name, AUTOSCALESETTING_NAME)

        # List autoscale settings[get]
        result = self.mgmt_client.autoscale_settings.list_by_resource_group(resource_group.name)

        # List autoscale settings[get]
        result = self.mgmt_client.autoscale_settings.list_by_subscription()

        # Update an autoscale setting[put]
        BODY = {
          "location": "West US",
          "profiles": [
            {
              "name": "adios",
              "capacity": {
                "minimum": "1",
                "maximum": "10",
                "default": "1"
              },
              "rules": [
              ]
            }
          ],
          "enabled": True,
          "target_resource_uri": vmss_id,
          "notifications": [
            {
              "operation": "Scale",
              "email": {
                "send_to_subscription_administrator": True,
                "send_to_subscription_co_administrators": True,
                "custom_emails": [
                  "gu@ms.com",
                  "ge@ns.net"
                ]
              },
              "webhooks": [
              ]
            }
          ]
        }
        result = self.mgmt_client.autoscale_settings.update(resource_group.name, AUTOSCALESETTING_NAME, BODY)

        # Delete an autoscale setting[delete]
        result = self.mgmt_client.autoscale_settings.delete(resource_group.name, AUTOSCALESETTING_NAME)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_scheduled_query_rules(self, resource_group):
        RESOURCE_GROUP = resource_group.name
        WORKSPACE_NAME = self.get_resource_name("workspacex")
        SCHEDULED_QUERY_RULE_NAME = self.get_resource_name("scheduledqueryrule")
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID

        if self.is_live:
            workspace = self.create_workspace(RESOURCE_GROUP, AZURE_LOCATION, WORKSPACE_NAME)
            workspace_id = workspace.id
        else:
            workspace_id = "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.OperationalInsights/workspaces/" + WORKSPACE_NAME

        # Create or Update rule - AlertingAction[put]
        BODY = {
          "location": "eastus",
          "description": "log alert description",
          "enabled": "true",
          # "last_updated_time": "2017-06-23T21:23:52.0221265Z",
          "provisioning_state": "Succeeded",
          "source": {
            "query": "Heartbeat | summarize AggregatedValue = count() by bin(TimeGenerated, 5m)",
            # "data_source_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.OperationalInsights/workspaces/" + WORKSPACE_NAME + "",
            "data_source_id": workspace_id,
            "query_type": "ResultCount"
          },
          "schedule": {
            "frequency_in_minutes": "15",
            "time_window_in_minutes": "15"
          },
          "action": {
            "odata.type": "Microsoft.WindowsAzure.Management.Monitoring.Alerts.Models.Microsoft.AppInsights.Nexus.DataContracts.Resources.ScheduledQueryRules.AlertingAction",
            "severity": "1",
            "azns_action": {
              "action_group": [],
              "email_subject": "Email Header",
              "custom_webhook_payload": "{}"
            },
            "trigger": {
              "threshold_operator": "GreaterThan",
              "threshold": "3",
              "metric_trigger": {
                "threshold_operator": "GreaterThan",
                "threshold": "5",
                "metric_trigger_type": "Consecutive",
                "metric_column": "Computer"
              }
            }
          }
        }
        result = self.mgmt_client.scheduled_query_rules.create_or_update(resource_group.name, SCHEDULED_QUERY_RULE_NAME, BODY)

        # Get rule[get]
        result = self.mgmt_client.scheduled_query_rules.get(resource_group.name, SCHEDULED_QUERY_RULE_NAME)

        # List rules[get]
        result = self.mgmt_client.scheduled_query_rules.list_by_resource_group(resource_group.name)

        # List rules[get]
        result = self.mgmt_client.scheduled_query_rules.list_by_subscription()

        # Patch Log Search Rule[patch]
        BODY = {
          "enabled": "true"
        }
        result = self.mgmt_client.scheduled_query_rules.update(resource_group.name, SCHEDULED_QUERY_RULE_NAME, BODY)

        # Delete rule[delete]
        result = self.mgmt_client.scheduled_query_rules.delete(resource_group.name, SCHEDULED_QUERY_RULE_NAME)
        
    @unittest.skip("(InvalidResourceType) The resource type could not be found in the namespace 'microsoft.insights' for api version '2018-06-01-preview'.")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_guest_diagnostics_settings(self, resource_group):
        DIAGNOSTIC_SETTINGS_NAME = self.get_resource_name("diagnosticsettings")

        BODY = {
          "location": AZURE_LOCATION
        }
        self.mgmt_client.guest_diagnostics_settings.create_or_update(resource_group.name, DIAGNOSTIC_SETTINGS_NAME, BODY)

        self.mgmt_client.guest_diagnostics_settings.list_by_resource_group(resource_group.name)

        self.mgmt_client.guest_diagnostics_settings.list()

        self.mgmt_client.guest_diagnostics_settings.get(resource_group.name, DIAGNOSTIC_SETTINGS_NAME)

        BODY = {
          "location": AZURE_LOCATION
        }
        self.mgmt_client.guest_diagnostics_settings.update(resource_group.name, DIAGNOSTIC_SETTINGS_NAME, BODY)

        self.mgmt_client.guest_diagnostics_settings.delete(resource_group.name, DIAGNOSTIC_SETTINGS_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
