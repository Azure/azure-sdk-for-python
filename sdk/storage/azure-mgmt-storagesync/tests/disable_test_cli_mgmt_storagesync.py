# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 37
# Methods Covered : 37
# Examples Total  : 38
# Examples Tested : 38
# Coverage %      : 100
# ----------------------

import os
import unittest

import azure.mgmt.storagesync
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtMicrosoftStorageSyncTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMicrosoftStorageSyncTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.storagesync.StorageSyncManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_storagesync(self, resource_group):

        SUBSCRIPTION_ID = None
        if self.is_live:
            SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", None)
        if not SUBSCRIPTION_ID:
            SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID

        RESOURCE_GROUP = resource_group.name
        STORAGE_SYNC_SERVICE_NAME = "ssservicename"
        SYNC_GROUP_NAME = "groupname"
        REGISTERED_SERVER_NAME = "rservicename"
        STORAGE_ACCOUNT_NAME = "accountnamexyz"
        CLOUD_ENDPOINT_NAME = "cendpointname"
        SERVER_ENDPOINT_NAME = "sendpointname"
        LOCATION_NAME = AZURE_LOCATION

        # StorageSyncServices_Create[put]
        BODY = {
          "location": "WestUS",
          "tags": {}
        }
        result = self.mgmt_client.storage_sync_services.create(resource_group.name, STORAGE_SYNC_SERVICE_NAME, BODY)

        # SyncGroups_Create[put]
        BODY = {}
        result = self.mgmt_client.sync_groups.create(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, BODY)

        """
        # RegisteredServers_Create[put]
        BODY = {
          "server_role": "Standalone",
          "server_certificate": "\"MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjANBgkqhkiG9w0BAQ0FADAzMTEwLwYDVQQDEyhhbmt1c2hiLXByb2QzLnJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoXDTE4MDgwNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRtb25kLmNvcnAubWljcm9zb2Z0LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmYINHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gfe9PRZ0FmSOZnXMbLYgLiDFqLtut5gHcOuWMj03YnkfoBEKlFBxWbagvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHdLiQcMB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUsJpbB3Wocb0F5frn614D2pg14ERB5otjAMWw1m65csQWPI6dP8KIYe0+QPkCAwEAAaMmMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwwwDQYJKoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLokx1l2Z8+GFQkcG4xpZSt+UN6wLerdCbnNhtkCErWUDeaT0jxk4g71Ofex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO0SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexdfw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPOlooK2bjMUei9ANtEdXwwfVZGWvVh6tJjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzITaA/WsuujlM=\"",
          "last_heart_beat": "\"2017-08-08T18:29:06.470652Z\"",
          "server_osversion": "10.0.14393.0",
          "agent_version": "1.0.277.0"
        }
        result = self.mgmt_client.registered_servers.create(resource_group.name, STORAGE_SYNC_SERVICE_NAME, REGISTERED_SERVER_NAME, BODY)
        result = result.result()

        # CloudEndpoints_Create[put]
        BODY = {
          "storage_account_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Storage/storageAccounts/" + STORAGE_ACCOUNT_NAME + "",
          "azure_file_share_name": "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4",
          "storage_account_tenant_id": "\"72f988bf-86f1-41af-91ab-2d7cd011db47\"",
          "friendly_name": "ankushbsubscriptionmgmtmab"
        }
        result = self.mgmt_client.cloud_endpoints.create(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # ServerEndpoints_Create[put]
        BODY = {
          "server_local_path": "D:\\SampleServerEndpoint_1",
          "server_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.StorageSync/storageSyncServices/" + STORAGE_SYNC_SERVICE_NAME + "/registeredServers/" + REGISTERED_SERVER_NAME + "",
          "cloud_tiering": "off",
          "volume_free_space_percent": "100",
          "tier_files_older_than_days": "0",
          "offline_data_transfer": "on",
          "offline_data_transfer_share_name": "myfileshare"
        }
        result = self.mgmt_client.server_endpoints.create(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, SERVER_ENDPOINT_NAME, BODY)
        result = result.result()

        # ServerEndpoints_Get[get]
        result = self.mgmt_client.server_endpoints.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, SERVER_ENDPOINT_NAME)

        # CloudEndpoints_Get[get]
        result = self.mgmt_client.cloud_endpoints.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME)

        # ServerEndpoints_ListBySyncGroup[get]
        result = self.mgmt_client.server_endpoints.list_by_sync_group(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME)

        # CloudEndpoints_ListBySyncGroup[get]
        result = self.mgmt_client.cloud_endpoints.list_by_sync_group(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME)

        # RegisteredServers_Get[get]
        result = self.mgmt_client.registered_servers.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, REGISTERED_SERVER_NAME)

        # Workflows_Get[get]
        result = self.mgmt_client.workflows.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, WORKFLOW_NAME)
        """

        # SyncGroups_Get[get]
        result = self.mgmt_client.sync_groups.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME)

        """
        # Workflows_Get[get]
        result = self.mgmt_client.workflows.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME, WORKFLOW_NAME)

        # RegisteredServers_ListByStorageSyncService[get]
        result = self.mgmt_client.registered_servers.list_by_storage_sync_service(resource_group.name, STORAGE_SYNC_SERVICE_NAME)
        """

        # SyncGroups_ListByStorageSyncService[get]
        result = self.mgmt_client.sync_groups.list_by_storage_sync_service(resource_group.name, STORAGE_SYNC_SERVICE_NAME)

        # Workflows_ListByStorageSyncService[get]
        result = self.mgmt_client.workflows.list_by_storage_sync_service(resource_group.name, STORAGE_SYNC_SERVICE_NAME)

        # StorageSyncServices_Get[get]
        result = self.mgmt_client.storage_sync_services.get(resource_group.name, STORAGE_SYNC_SERVICE_NAME)

        # StorageSyncServices_ListByResourceGroup[get]
        result = self.mgmt_client.storage_sync_services.list_by_resource_group(resource_group.name)

        # StorageSyncServices_ListBySubscription[get]
        result = self.mgmt_client.storage_sync_services.list_by_subscription()

        # Operations_List[get]
        result = self.mgmt_client.operations.list()

        """
        # CloudEndpoints_TriggerChangeDetection[post]
        BODY = {
          "directory_path": "NewDirectory",
          "change_detection_mode": "Recursive"
        }
        result = self.mgmt_client.cloud_endpoints.trigger_change_detection(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # CloudEndpoints_restoreheartbeat[post]
        result = self.mgmt_client.cloud_endpoints.restoreheartbeat(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME)

        # ServerEndpoints_recallAction[post]
        BODY = {
          "pattern": "",
          "recall_path": ""
        }
        result = self.mgmt_client.server_endpoints.recall_action(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, SERVER_ENDPOINT_NAME, BODY)
        result = result.result()

        # CloudEndpoints_PostRestore[post]
        BODY = {
          "azure_file_share_uri": "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare",
          "source_azure_file_share_uri": "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare",
          "status": "Succeeded",
          "restore_file_spec": [
            {
              "path": "text1.txt",
              "isdir": False
            },
            {
              "path": "MyDir",
              "isdir": True
            },
            {
              "path": "MyDir/SubDir",
              "isdir": False
            },
            {
              "path": "MyDir/SubDir/File1.pdf",
              "isdir": False
            }
          ]
        }
        result = self.mgmt_client.cloud_endpoints.post_restore(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # CloudEndpoints_PreRestore[post]
        BODY = {
          "azure_file_share_uri": "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare",
          "restore_file_spec": [
            {
              "path": "text1.txt",
              "isdir": False
            },
            {
              "path": "MyDir",
              "isdir": True
            },
            {
              "path": "MyDir/SubDir",
              "isdir": False
            },
            {
              "path": "MyDir/SubDir/File1.pdf",
              "isdir": False
            }
          ]
        }
        result = self.mgmt_client.cloud_endpoints.pre_restore(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # CloudEndpoints_PostBackup[post]
        BODY = {
          "azure_file_share": "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"
        }
        result = self.mgmt_client.cloud_endpoints.post_backup(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # CloudEndpoints_PreBackup[post]
        BODY = {
          "azure_file_share": "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"
        }
        result = self.mgmt_client.cloud_endpoints.pre_backup(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME, BODY)
        result = result.result()

        # ServerEndpoints_Update[patch]
        BODY = {
          "cloud_tiering": "off",
          "volume_free_space_percent": "100",
          "tier_files_older_than_days": "0",
          "offline_data_transfer": "off"
        }
        result = self.mgmt_client.server_endpoints.update(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, SERVER_ENDPOINT_NAME, BODY)
        result = result.result()

        # RegisteredServers_triggerRollover[post]
        BODY = {
          "server_certificate": "\"MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjANBgkqhkiG9w0BAQ0FADAzMTEwLwYDVQQDEyhhbmt1c2hiLXByb2QzLnJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoXDTE4MDgwNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRtb25kLmNvcnAubWljcm9zb2Z0LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmYINHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gfe9PRZ0FmSOZnXMbLYgLiDFqLtut5gHcOuWMj03YnkfoBEKlFBxWbagvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHdLiQcMB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUsJpbB3Wocb0F5frn614D2pg14ERB5otjAMWw1m65csQWPI6dP8KIYe0+QPkCAwEAAaMmMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwwwDQYJKoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLokx1l2Z8+GFQkcG4xpZSt+UN6wLerdCbnNhtkCErWUDeaT0jxk4g71Ofex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO0SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexdfw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPOlooK2bjMUei9ANtEdXwwfVZGWvVh6tJjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzITaA/WsuujlM=\""
        }
        result = self.mgmt_client.registered_servers.trigger_rollover(resource_group.name, STORAGE_SYNC_SERVICE_NAME, REGISTERED_SERVER_NAME, BODY)
        result = result.result()

        # Workflows_Abort[post]
        result = self.mgmt_client.workflows.abort(resource_group.name, STORAGE_SYNC_SERVICE_NAME, WORKFLOW_NAME)
        """

        # StorageSyncServices_Update[patch]
        BODY = {
          "tags": {
            "environment": "Test",
            "dept": "IT"
          }
        }
        result = self.mgmt_client.storage_sync_services.update(resource_group.name, STORAGE_SYNC_SERVICE_NAME, BODY)

        # StorageSyncServiceCheckNameAvailability_AlreadyExists[post]
        BODY = {
          "name": "newstoragesyncservicename",
          "type": "Microsoft.StorageSync/storageSyncServices"
        }
        result = self.mgmt_client.storage_sync_services.check_name_availability(LOCATION_NAME, BODY)

        # StorageSyncServiceCheckNameAvailability_Available[post]
        BODY = {
          "name": "newstoragesyncservicename",
          "type": "Microsoft.StorageSync/storageSyncServices"
        }
        result = self.mgmt_client.storage_sync_services.check_name_availability(LOCATION_NAME, BODY)

        """
        # ServerEndpoints_Delete[delete]
        result = self.mgmt_client.server_endpoints.delete(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, SERVER_ENDPOINT_NAME)
        result = result.result()

        # CloudEndpoints_Delete[delete]
        result = self.mgmt_client.cloud_endpoints.delete(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME, CLOUD_ENDPOINT_NAME)
        result = result.result()

        # RegisteredServers_Delete[delete]
        result = self.mgmt_client.registered_servers.delete(resource_group.name, STORAGE_SYNC_SERVICE_NAME, REGISTERED_SERVER_NAME)
        result = result.result()
        """

        # SyncGroups_Delete[delete]
        result = self.mgmt_client.sync_groups.delete(resource_group.name, STORAGE_SYNC_SERVICE_NAME, SYNC_GROUP_NAME)

        # StorageSyncServices_Delete[delete]
        result = self.mgmt_client.storage_sync_services.delete(resource_group.name, STORAGE_SYNC_SERVICE_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
