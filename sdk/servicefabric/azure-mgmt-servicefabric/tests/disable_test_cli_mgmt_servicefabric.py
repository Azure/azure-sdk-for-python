# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 29
# Methods Covered : 28
# Examples Total  : 31
# Examples Tested : 31
# Coverage %      : 96.55172413793103
# ----------------------

import os
import unittest

import azure.mgmt.servicefabric
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtServiceFabricTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtServiceFabricTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.servicefabric.ServiceFabricManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_servicefabric(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        RESOURCE_GROUP = resource_group.name
        SUBSCRIPTION_ID = None
        if self.is_live:
            SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
        if not SUBSCRIPTION_ID:
            SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        CLUSTER_NAME = "cluster"
        APPLICATION_NAME = "application"
        APPLICATION_TYPE_NAME = "apptype"
        SERVICE_NAME = "service"
        VERSION_NAME = "1.0"

        # Put a cluster with minimum parameters[put]
        BODY = {
          "type": "Microsoft.ServiceFabric/clusters",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "",
          "name": "myCluster",
          "management_endpoint": "http://myCluster.eastus.cloudapp.azure.com:19080",
          "fabric_settings": [
            {
              "name": "UpgradeService",
              "parameters": [
                {
                  "name": "AppPollIntervalInSeconds",
                  "value": "60"
                }
              ]
            }
          ],
          "diagnostics_storage_account_config": {
            "storage_account_name": "diag",
            "protected_account_key_name": "StorageAccountKey1",
            "blob_endpoint": "https://diag.blob.core.windows.net/",
            "queue_endpoint": "https://diag.queue.core.windows.net/",
            "table_endpoint": "https://diag.table.core.windows.net/"
          },
          "node_types": [
            {
              "name": "nt1vm",
              "client_connection_endpoint_port": "19000",
              "http_gateway_endpoint_port": "19007",
              "application_ports": {
                "start_port": "20000",
                "end_port": "30000"
              },
              "ephemeral_ports": {
                "start_port": "49000",
                "end_port": "64000"
              },
              "is_primary": True,
              "vm_instance_count": "5",
              "durability_level": "Bronze"
            }
          ],
          "reliability_level": "Silver",
          "upgrade_mode": "Automatic"
        }
        result = self.mgmt_client.clusters.create_or_update(resource_group.name, CLUSTER_NAME, BODY)
        result = result.result()

        """
        # Put a cluster with maximum parameters[put]
        BODY = {
          "type": "Microsoft.ServiceFabric/clusters",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "",
          "name": "myCluster",
          # "cluster_code_version": "6.1.480.9494",
          "cluster_code_version": "6.5.639.9590",
          "management_endpoint": "https://myCluster.eastus.cloudapp.azure.com:19080",
          # "certificate_common_names": {
          #   "common_names": [
          #     {
          #       "certificate_common_name": "abc.com",
          #       "certificate_issuer_thumbprint": "12599211F8F14C90AFA9532AD79A6F2CA1C00622"
          #     }
          #   ],
          #   "x509store_name": "My"
          # },
          # "client_certificate_thumbprints": [
          #   {
          #     "is_admin": True,
          #     "certificate_thumbprint": "5F3660C715EBBDA31DB1FFDCF508302348DE8E7A"
          #   }
          # ],
          # "client_certificate_common_names": [
          #   {
          #     "is_admin": True,
          #     "certificate_common_name": "abc.com",
          #     "certificate_issuer_thumbprint": "5F3660C715EBBDA31DB1FFDCF508302348DE8E7A"
          #   }
          # ],
          "fabric_settings": [
            {
              "name": "UpgradeService",
              "parameters": [
                {
                  "name": "AppPollIntervalInSeconds",
                  "value": "60"
                }
              ]
            }
          ],
          "upgrade_description": {
            "force_restart": False,
            "upgrade_replica_set_check_timeout": "00:10:00",
            "health_check_wait_duration": "00:00:30",
            "health_check_stable_duration": "00:00:30",
            "health_check_retry_timeout": "00:05:00",
            "upgrade_timeout": "01:00:00",
            "upgrade_domain_timeout": "00:15:00",
            "health_policy": {
              "max_percent_unhealthy_nodes": "0",
              "max_percent_unhealthy_applications": "0",
              "application_health_policies": {
                "fabric:/my_app1": {
                  "default_service_type_health_policy": {
                    "max_percent_unhealthy_services": "0"
                  },
                  "service_type_health_policies": {
                    "my_service_type1": {
                      "max_percent_unhealthy_services": "100"
                    }
                  }
                }
              }
            },
            "delta_health_policy": {
              "max_percent_delta_unhealthy_nodes": "0",
              "max_percent_upgrade_domain_delta_unhealthy_nodes": "0",
              "max_percent_delta_unhealthy_applications": "0",
              "application_delta_health_policies": {
                "fabric:/my_app1": {
                  "default_service_type_delta_health_policy": {
                    "max_percent_delta_unhealthy_services": "0"
                  },
                  "service_type_delta_health_policies": {
                    "my_service_type1": {
                      "max_percent_delta_unhealthy_services": "0"
                    }
                  }
                }
              }
            },
          },
          "diagnostics_storage_account_config": {
            "storage_account_name": "diag",
            "protected_account_key_name": "StorageAccountKey1",
            "blob_endpoint": "https://diag.blob.core.windows.net/",
            "queue_endpoint": "https://diag.queue.core.windows.net/",
            "table_endpoint": "https://diag.table.core.windows.net/"
          },
          "node_types": [
            {
              "name": "nt1vm",
              "client_connection_endpoint_port": "19000",
              "http_gateway_endpoint_port": "19007",
              "application_ports": {
                "start_port": "20000",
                "end_port": "30000"
              },
              "ephemeral_ports": {
                "start_port": "49000",
                "end_port": "64000"
              },
              "is_primary": True,
              "vm_instance_count": "5",
              "durability_level": "Bronze"
            }
          ],
          "vm_image": "Windows",
          "azure_active_directory": {
            "tenant_id": "6abcc6a0-8666-43f1-87b8-172cf86a9f9c",
            "cluster_application": "5886372e-7bf4-4878-a497-8098aba608ae",
            "client_application": "d151ad89-4bce-4ae8-b3d1-1dc79679fa75"
          },
          "reliability_level": "Silver",
          "reverse_proxy_certificate_common_names": {
            "common_names": [
              {
                "certificate_common_name": "abc.com",
                "certificate_issuer_thumbprint": "12599211F8F14C90AFA9532AD79A6F2CA1C00622"
              }
            ],
            "x509store_name": "My"
          },
          "upgrade_mode": "Manual",
          "add_on_features": [
            "RepairManager",
            "DnsService",
            "BackupRestoreService",
            "ResourceMonitorService"
          ],
          "event_store_service_enabled": True
        }
        result = self.mgmt_client.clusters.create_or_update(resource_group.name, CLUSTER_NAME, BODY)
        result = result.result()

        # Put an application with maximum parameters[put]
        BODY = {
          "type": "applications",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "",
          "name": "myCluster",
          "type_name": "myAppType",
          "type_version": "1.0",
          "parameters": {
            "param1": "value1"
          },
          "upgrade_policy": {
            "application_health_policy": {
              "consider_warning_as_error": True,
              "max_percent_unhealthy_deployed_applications": "0",
              "default_service_type_health_policy": {
                "max_percent_unhealthy_services": "0",
                "max_percent_unhealthy_partitions_per_service": "0",
                "max_percent_unhealthy_replicas_per_partition": "0"
              }
            },
            "rolling_upgrade_monitoring_policy": {
              "failure_action": "Rollback",
              "health_check_retry_timeout": "00:10:00",
              "health_check_wait_duration": "00:02:00",
              "health_check_stable_duration": "00:05:00",
              "upgrade_domain_timeout": "1.06:00:00",
              "upgrade_timeout": "01:00:00"
            },
            "upgrade_replica_set_check_timeout": "01:00:00",
            "force_restart": False
          },
          "maximum_nodes": "3",
          "minimum_nodes": "1",
          "remove_application_capacity": False,
          "metrics": [
            {
              "name": "metric1",
              "reservation_capacity": "1",
              "maximum_capacity": "3",
              "total_application_capacity": "5"
            }
          ]
        }
        result = self.mgmt_client.applications.create_or_update(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Put an application with minimum parameters[put]
        BODY = {
          # "type": "applications",
          "type": "Microsoft.Compute",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "",
          "name": "myCluster",
          "type_name": "myAppType",
          "type_version": "1.0",
          "remove_application_capacity": False
        }
        result = self.mgmt_client.applications.create_or_update(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, BODY)
        result = result.result()


        # Put an application type[put]
        BODY = {
          "type": "applicationTypes",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applicationTypes/" + APPLICATION_TYPE_NAME + "",
          "name": "myCluster"
        }
        result = self.mgmt_client.application_types.create_or_update(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME, BODY)

        # Put a service with minimum parameters[put]
        BODY = {
          "type": "services",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "/services/" + SERVICE_NAME + "",
          "name": "myCluster",
          "properties": {
            "service_kind": "Stateless",
            "service_type_name": "myServiceType",
            "partition_description": {
              "partition_scheme": "Singleton"
            },
            "instance_count": "1"
          }
        }
        result = self.mgmt_client.services.create(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, SERVICE_NAME, BODY)
        result = result.result()

        # Put a service with maximum parameters[put]
        BODY = {
          "type": "services",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "/services/" + SERVICE_NAME + "",
          "name": "myCluster",
          "properties": {
            "service_kind": "Stateless",
            "placement_constraints": "NodeType==frontend",
            "service_type_name": "myServiceType",
            "partition_description": {
              "partition_scheme": "Singleton"
            },
            "service_load_metrics": [
              {
                "name": "metric1",
                "weight": "Low"
              }
            ],
            "correlation_scheme": [
              {
                "service_name": "fabric:/app1/app1~svc1",
                "scheme": "Affinity"
              }
            ],
            "service_placement_policies": [],
            "default_move_cost": "Medium",
            "instance_count": "5",
            "service_package_activation_mode": "SharedProcess"
          }
        }
        result = self.mgmt_client.services.create(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, SERVICE_NAME, BODY)
        result = result.result()

        # Put an application type version[put]
        BODY = {
          "type": "versions",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applicationTypes/" + APPLICATION_TYPE_NAME + "/versions/" + VERSION_NAME + "",
          "name": "myCluster",
          "properties": {
            "app_package_url": "http://fakelink.test.com/MyAppType"
          }
        }
        result = self.mgmt_client.application_type_versions.create(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME, VERSION_NAME, BODY)
        result = result.result()

        # Get an application type version[get]
        result = self.mgmt_client.application_type_versions.get(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME, VERSION_NAME)

        # Get a service[get]
        result = self.mgmt_client.services.get(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, SERVICE_NAME)

        # Get a list of application type version resources[get]
        result = self.mgmt_client.application_type_versions.list(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME)

        # Get a list of service resources[get]
        result = self.mgmt_client.services.list(resource_group.name, CLUSTER_NAME, APPLICATION_NAME)

        # Get cluster version by environment[get]
        result = self.mgmt_client.cluster_versions.get_by_environment(LOCATION_NAME, ENVIRONMENT_NAME, CLUSTER_VERSION_NAME)

        # Get an application type[get]
        result = self.mgmt_client.application_types.get(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME)

        # Get an application[get]
        result = self.mgmt_client.applications.get(resource_group.name, CLUSTER_NAME, APPLICATION_NAME)

        # List cluster versions by environment[get]
        result = self.mgmt_client.cluster_versions.list_by_environment(LOCATION_NAME, ENVIRONMENT_NAME)

        # Get a list of application type name resources[get]
        result = self.mgmt_client.application_types.list(resource_group.name, CLUSTER_NAME)

        # Get a list of application resources[get]
        result = self.mgmt_client.applications.list(resource_group.name, CLUSTER_NAME)

        # Get cluster version[get]
        result = self.mgmt_client.cluster_versions.get(LOCATION_NAME, CLUSTER_VERSION_NAME)

        # Get a cluster[get]
        result = self.mgmt_client.clusters.get(resource_group.name, CLUSTER_NAME)

        # List cluster versions[get]
        result = self.mgmt_client.cluster_versions.list(LOCATION_NAME)

        # List cluster by resource group[get]
        result = self.mgmt_client.clusters.list_by_resource_group(resource_group.name)

        # List clusters[get]
        result = self.mgmt_client.clusters.list()

        # Patch a service[patch]
        BODY = {
          "type": "services",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "/services/" + SERVICE_NAME + "",
          "name": "myCluster",
          "properties": {
            "service_kind": "Stateless",
            "service_load_metrics": [
              {
                "name": "metric1",
                "weight": "Low"
              }
            ]
          }
        }
        result = self.mgmt_client.services.update(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, SERVICE_NAME, BODY)
        result = result.result()

        # Patch an application[patch]
        BODY = {
          "type": "applications",
          "location": "eastus",
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ServiceFabric/clusters/" + CLUSTER_NAME + "/applications/" + APPLICATION_NAME + "",
          "name": "myCluster",
          "properties": {
            "type_version": "1.0",
            "remove_application_capacity": False,
            "metrics": [
              {
                "name": "metric1",
                "reservation_capacity": "1",
                "maximum_capacity": "3",
                "total_application_capacity": "5"
              }
            ]
          }
        }
        result = self.mgmt_client.applications.update(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, BODY)
        result = result.result()

        # Patch a cluster[patch]
        BODY = {
          "tags": {
            "a": "b"
          },
          "properties": {
            "node_types": [
              {
                "name": "nt1vm",
                "client_connection_endpoint_port": "19000",
                "http_gateway_endpoint_port": "19007",
                "application_ports": {
                  "start_port": "20000",
                  "end_port": "30000"
                },
                "ephemeral_ports": {
                  "start_port": "49000",
                  "end_port": "64000"
                },
                "is_primary": True,
                "vm_instance_count": "5",
                "durability_level": "Bronze"
              },
              {
                "name": "testnt1",
                "client_connection_endpoint_port": "0",
                "http_gateway_endpoint_port": "0",
                "application_ports": {
                  "start_port": "1000",
                  "end_port": "2000"
                },
                "ephemeral_ports": {
                  "start_port": "3000",
                  "end_port": "4000"
                },
                "is_primary": False,
                "vm_instance_count": "3",
                "durability_level": "Bronze"
              }
            ],
            "reliability_level": "Bronze",
            "upgrade_mode": "Automatic",
            "event_store_service_enabled": True
          }
        }
        result = self.mgmt_client.clusters.update(resource_group.name, CLUSTER_NAME, BODY)
        result = result.result()

        # Delete an application type version[delete]
        result = self.mgmt_client.application_type_versions.delete(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME, VERSION_NAME)
        result = result.result()

        # Delete a service[delete]
        result = self.mgmt_client.services.delete(resource_group.name, CLUSTER_NAME, APPLICATION_NAME, SERVICE_NAME)
        result = result.result()

        # Delete an application type[delete]
        result = self.mgmt_client.application_types.delete(resource_group.name, CLUSTER_NAME, APPLICATION_TYPE_NAME)
        result = result.result()

        # Delete an application[delete]
        result = self.mgmt_client.applications.delete(resource_group.name, CLUSTER_NAME, APPLICATION_NAME)
        result = result.result()
        """

        # Delete a cluster[delete]
        result = self.mgmt_client.clusters.delete(resource_group.name, CLUSTER_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
