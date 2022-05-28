# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 43
# Methods Covered : 43
# Examples Total  : 43
# Examples Tested : 19
# Coverage %      : 44
# ----------------------

import unittest

import azure.mgmt.appplatform
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAppPlatformTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAppPlatformTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.appplatform.AppPlatformManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_appplatform(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        SERVICE_NAME = "myservice"
        LOCATION = "myLocation"
        APP_NAME = "myapp"
        BINDING_NAME = "mybinding"
        DATABASE_ACCOUNT_NAME = "myDatabaseAccount"
        CERTIFICATE_NAME = "myCertificate"
        DOMAIN_NAME = "myDomain"
        DEPLOYMENT_NAME = "mydeployment"

        # /Services/put/Services_CreateOrUpdate[put]
        BODY = {
          "properties": {
            "config_server_properties": {
              "config_server": {
                "git_property": {
                  "uri": "https://github.com/fake-user/fake-repository.git",
                  "label": "master",
                  "search_paths": [
                    "/"
                  ]
                }
              }
            },
            "trace": {
              "enabled": True,
              "app_insight_instrumentation_key": "00000000-0000-0000-0000-000000000000"
            }
          },
          "tags": {
            "key1": "value1"
          },
          "location": "eastus"
        }
        result = self.mgmt_client.services.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, resource=BODY)
        result = result.result()

        # /Apps/put/Apps_CreateOrUpdate[put]
        PROPERTIES = {
          "public": True,
          "active_deployment_name": "mydeployment1",
          "fqdn": "myapp.mydomain.com",
          "https_only": False,
          "temporary_disk": {
            "size_in_gb": "2",
            "mount_path": "/mytemporarydisk"
          },
          "persistent_disk": {
            "size_in_gb": "2",
            "mount_path": "/mypersistentdisk"
          }
        }
        result = self.mgmt_client.apps.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, properties= PROPERTIES, location="eastus")
        result = result.result()

        # Not available/tested yet
        # /Certificates/put/Certificates_CreateOrUpdate[put]
        PROPERTIES = {
          "vault_uri": "https://myvault.vault.azure.net",
          "key_vault_cert_name": "mycert",
          "cert_version": "08a219d06d874795a96db47e06fbb01e"
        }
        # result = self.mgmt_client.certificates.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, certificate_name=CERTIFICATE_NAME, properties= PROPERTIES)

        # Not available/tested yet
        # /CustomDomains/put/CustomDomains_CreateOrUpdate[put]
        PROPERTIES = {
          "thumbprint": "934367bf1c97033f877db0f15cb1b586957d3133",
          "app_name": "myapp",
          "cert_name": "mycert"
        }
        # result = self.mgmt_client.custom_domains.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, domain_name=DOMAIN_NAME, properties= PROPERTIES)

        # Not available/tested yet
        # /Bindings/put/Bindings_CreateOrUpdate[put]
        PROPERTIES = {
          "resource_name": "my-cosmosdb-1",
          "resource_type": "Microsoft.DocumentDB",
          "resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DocumentDB/databaseAccounts/" + DATABASE_ACCOUNT_NAME + "",
          "key": "xxxx",
          "binding_parameters": {
            "database_name": "db1",
            "api_type": "SQL"
          }
        }
        # result = self.mgmt_client.bindings.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, binding_name=BINDING_NAME, properties= PROPERTIES)

        # Not available/tested yet
        # /Deployments/put/Deployments_CreateOrUpdate[put]
        PROPERTIES = {
          "source": {
            "type": "Source",
            "relative_path": "resources/a172cedcae47474b615c54d510a5d84a8dea3032e958587430b413538be3f333-2019082605-e3095339-1723-44b7-8b5e-31b1003978bc",
            "version": "1.0",
            "artifact_selector": "sub-module-1"
          },
          "deployment_settings": {
            "cpu": "1",
            "memory_in_gb": "3",
            "jvm_options": "-Xms1G -Xmx3G",
            "instance_count": "1",
            "environment_variables": {
              "env": "test"
            },
            "runtime_version": "Java_8"
          }
        }
        # result = self.mgmt_client.deployments.create_or_update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME, properties= PROPERTIES)
        # result = result.result()

        # Not available/tested yet
        # /Deployments/get/Deployments_Get[get]
        # result = self.mgmt_client.deployments.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME)

        # Not available/tested yet
        # /Bindings/get/Bindings_Get[get]
        # result = self.mgmt_client.bindings.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, binding_name=BINDING_NAME)

        # Not available/tested yet
        # /CustomDomains/get/CustomDomains_Get[get]
        # result = self.mgmt_client.custom_domains.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, domain_name=DOMAIN_NAME)

        # Not available/tested yet
        # /Certificates/get/Certificates_Get[get]
        # result = self.mgmt_client.certificates.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, certificate_name=CERTIFICATE_NAME)

        # /Deployments/get/Deployments_List[get]
        result = self.mgmt_client.deployments.list(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # /Bindings/get/Bindings_List[get]
        result = self.mgmt_client.bindings.list(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # Not available/tested yet
        # /CustomDomains/get/CustomDomains_List[get]
        # result = self.mgmt_client.custom_domains.list(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # /Apps/get/Apps_Get[get]
        result = self.mgmt_client.apps.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # Not available/tested yet
        # /Certificates/get/Certificates_List[get]
        # result = self.mgmt_client.certificates.list(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Deployments/get/Deployments_ListClusterAllDeployments[get]
        result = self.mgmt_client.deployments.list_cluster_all_deployments(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Apps/get/Apps_List[get]
        result = self.mgmt_client.apps.list(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Services/get/Services_Get[get]
        result = self.mgmt_client.services.get(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Services/get/Services_List[get]
        result = self.mgmt_client.services.list(resource_group_name=RESOURCE_GROUP)

        # /Services/get/Services_ListBySubscription[get]
        result = self.mgmt_client.services.list_by_subscription()

        # /Operations/get/Operations_List[get]
        result = self.mgmt_client.operations.list()

        # Not available/tested yet
        # /Deployments/post/Deployments_GetLogFileUrl[post]
        # result = self.mgmt_client.deployments.get_log_file_url(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME)

        # Not available/tested yet
        # /Deployments/post/Deployments_Restart[post]
        # result = self.mgmt_client.deployments.restart(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME)
        # result = result.result()

        # Not available/tested yet
        # /Deployments/post/Deployments_Start[post]
        # result = self.mgmt_client.deployments.start(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME)
        # result = result.result()

        # Not available/tested yet
        # /Deployments/post/Deployments_Stop[post]
        # result = self.mgmt_client.deployments.stop(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME)
        # result = result.result()

        # Not available/tested yet
        # /Deployments/patch/Deployments_Update[patch]
        PROPERTIES = {
          "source": {
            "type": "Source",
            "relative_path": "resources/a172cedcae47474b615c54d510a5d84a8dea3032e958587430b413538be3f333-2019082605-e3095339-1723-44b7-8b5e-31b1003978bc",
            "version": "1.0",
            "artifact_selector": "sub-module-1"
          }
        }
        # result = self.mgmt_client.deployments.update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, deployment_name=DEPLOYMENT_NAME, properties= PROPERTIES)
        # result = result.result()

        # Not available/tested yet
        # /Bindings/patch/Bindings_Update[patch]
        PROPERTIES = {
          "key": "xxxx",
          "binding_parameters": {
            "database_name": "db1",
            "api_type": "SQL"
          }
        }
        # result = self.mgmt_client.bindings.update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, binding_name=BINDING_NAME, properties= PROPERTIES)

        # Not available/tested yet
        # /CustomDomains/patch/CustomDomains_Patch[patch]
        PROPERTIES = {
          "thumbprint": "934367bf1c97033f877db0f15cb1b586957d3133",
          "app_name": "myapp",
          "cert_name": "mycert"
        }
        # result = self.mgmt_client.custom_domains.patch(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, domain_name=DOMAIN_NAME, properties= PROPERTIES)

        # Not available/tested yet
        # /CustomDomains/post/CustomDomains_Validate[post]
        # result = self.mgmt_client.custom_domains.validate(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, domain_name=DOMAIN_NAME, name="mydomain.io")

        # /Apps/post/Apps_GetResourceUploadUrl[post]
        result = self.mgmt_client.apps.get_resource_upload_url(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # Not available/tested yet
        # /Apps/patch/Apps_Update[patch]
        PROPERTIES = {
          "public": True,
          "active_deployment_name": "mydeployment1",
          "fqdn": "myapp.mydomain.com",
          "https_only": False,
          "temporary_disk": {
            "size_in_gb": "2",
            "mount_path": "/mytemporarydisk"
          },
          "persistent_disk": {
            "size_in_gb": "2",
            "mount_path": "/mypersistentdisk"
          }
        }
        # result = self.mgmt_client.apps.update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, properties= PROPERTIES, location="eastus")
        # result = result.result()

        # /Services/post/Services_DisableTestEndpoint[post]
        result = self.mgmt_client.services.disable_test_endpoint(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Services/post/Services_EnableTestEndpoint[post]
        result = self.mgmt_client.services.enable_test_endpoint(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # /Services/post/Services_RegenerateTestKey[post]
        result = self.mgmt_client.services.regenerate_test_key(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, key_type="Primary")

        # /Services/post/Services_ListTestKeys[post]
        result = self.mgmt_client.services.list_test_keys(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)

        # Not available/tested yet
        # /Services/patch/Services_Update[patch]
        BODY = {
          "properties": {
            "config_server_properties": {
              "config_server": {
                "git_property": {
                  "uri": "https://github.com/fake-user/fake-repository.git",
                  "label": "master",
                  "search_paths": [
                    "/"
                  ]
                }
              }
            },
            "trace": {
              "enabled": True,
              "app_insight_instrumentation_key": "00000000-0000-0000-0000-000000000000"
            }
          },
          "location": "eastus",
          "tags": {
            "key1": "value1"
          }
        }
        # result = self.mgmt_client.services.update(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, resource=BODY)
        # result = result.result()

        # /Services/post/Services_CheckNameAvailability[post]
        result = self.mgmt_client.services.check_name_availability(azure_location=AZURE_LOCATION, type="Microsoft.AppPlatform/Spring", name="myservice")

        # Not available/tested yet
        # /Bindings/delete/Bindings_Delete[delete]
        # result = self.mgmt_client.bindings.delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, binding_name=BINDING_NAME)

        # Not available/tested yet
        # /CustomDomains/delete/CustomDomains_Delete[delete]
        # result = self.mgmt_client.custom_domains.delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME, domain_name=DOMAIN_NAME)

        # Not available/tested yet
        # /Certificates/delete/Certificates_Delete[delete]
        # result = self.mgmt_client.certificates.delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, certificate_name=CERTIFICATE_NAME)

        # /Apps/delete/Apps_Delete[delete]
        result = self.mgmt_client.apps.delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME, app_name=APP_NAME)

        # /Services/delete/Services_Delete[delete]
        result = self.mgmt_client.services.delete(resource_group_name=RESOURCE_GROUP, service_name=SERVICE_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
