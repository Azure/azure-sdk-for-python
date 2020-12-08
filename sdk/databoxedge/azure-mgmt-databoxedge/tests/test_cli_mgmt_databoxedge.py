# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 49
# Methods Covered : 49
# Examples Total  : 49
# Examples Tested : 49
# Coverage %      : 100
# ----------------------

import unittest

import azure.mgmt.databoxedge
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtDataBoxEdgeTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtDataBoxEdgeTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.databoxedge.DataBoxEdgeManagementClient
        )
    
    @unittest.skip("skip test")
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_databoxedge(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        DATA_BOX_EDGE_DEVICE_NAME = "mydivicename"
        USER_NAME = "username"
        ROLE_NAME = "rolename"
        SHARE_NAME = "sharename"
        ORDER_NAME = "ordername"
        TRIGGER_NAME = "triggername"
        STORAGE_ACCOUNT_NAME = "storageaccountname"
        STORAGE_ACCOUNT_CREDENTIAL_NAME = "storageaccountcredentialname"
        BANDWIDTH_SCHEDULE_NAME = "bandwidthschedulename"
        CONTAINER_NAME = "containername"
        OPERATIONS_STATUS_NAME = "operationsstatusname"
        NETWORK_SETTING_NAME = "networksettingname"
        UPDATE_SUMMARY_NAME = "updatesummaryname"
        ALERT_NAME = "alertname"
        JOB_NAME = "jobname"
        SECURITY_SETTING_NAME = "securitysettingname"

        # DataBoxEdgeDevicePut[put]
        BODY = {
          "location": "eastus",
          "sku": {
            "name": "Edge",
            "tier": "Standard"
          }
        }
        result = self.mgmt_client.devices.create_or_update(DATA_BOX_EDGE_DEVICE_NAME, BODY, resource_group.name)
        result = result.result()

        """
        # UserPut[put]
        BODY = {
          "encrypted_password": {
            "value": "Password@1",
            "encryption_algorithm": "None",
            "encryption_cert_thumbprint": "blah"
          },
          "share_access_rights": []
        }
        result = self.mgmt_client.users.create_or_update(DATA_BOX_EDGE_DEVICE_NAME, USER_NAME, BODY, resource_group.name)
        result = result.result()

        # RolePut[put]
        BODY = {
          "kind": "IOT",
          "host_platform": "Linux",
          "io_tdevice_details": {
            "device_id": "iotdevice",
            "io_thost_hub": "iothub.azure-devices.net",
            "authentication": {
              "symmetric_key": {
                "connection_string": {
                  "value": "Encrypted<<HostName=iothub.azure-devices.net;DeviceId=iotDevice;SharedAccessKey=2C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>",
                  "encryption_cert_thumbprint": "348586569999244",
                  "encryption_algorithm": "AES256"
                }
              }
            }
          },
          "io_tedge_device_details": {
            "device_id": "iotEdge",
            "io_thost_hub": "iothub.azure-devices.net",
            "authentication": {
              "symmetric_key": {
                "connection_string": {
                  "value": "Encrypted<<HostName=iothub.azure-devices.net;DeviceId=iotEdge;SharedAccessKey=2C750FscEas3JmQ8Bnui5yQWZPyml0/UiRt1bQwd8=>>",
                  "encryption_cert_thumbprint": "1245475856069999244",
                  "encryption_algorithm": "AES256"
                }
              }
            }
          },
          "share_mappings": [],
          "role_status": "Enabled"
        }
        result = self.mgmt_client.roles.create_or_update(DATA_BOX_EDGE_DEVICE_NAME, ROLE_NAME, BODY, resource_group.name)
        result = result.result()

        # SharePut[put]
        BODY = {
          "description": "",
          "share_status": "Online",
          "monitoring_status": "Enabled",
          "azure_container_info": {
            "storage_account_credential_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/" + DATA_BOX_EDGE_DEVICE_NAME + "/storageAccountCredentials/" + STORAGE_ACCOUNT_CREDENTIAL_NAME + "",
            "container_name": "testContainerSMB",
            "data_format": "BlockBlob"
          },
          "access_protocol": "SMB",
          "user_access_rights": [
            {
              "user_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + resource_group.name + "/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/" + DATA_BOX_EDGE_DEVICE_NAME + "/users/" + USER_NAME + "",
              "access_type": "Change"
            }
          ],
          "data_policy": "Cloud"
        }
        result = self.mgmt_client.shares.create_or_update(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, SHARE_NAME, BODY)
        result = result.result()

        # OrderPut[put]
        BODY = {
          "contact_information": {
            "contact_person": "John Mcclane",
            "company_name": "Microsoft",
            "phone": "(800) 426-9400",
            "email_list": [
              "john@microsoft.com"
            ]
          },
          "shipping_address": {
            "address_line1": "Microsoft Corporation",
            "address_line2": "One Microsoft Way",
            "address_line3": "Redmond",
            "postal_code": "98052",
            "city": "WA",
            "state": "WA",
            "country": "USA"
          }
        }
        result = self.mgmt_client.orders.create_or_update(DATA_BOX_EDGE_DEVICE_NAME, BODY, resource_group.name)
        result = result.result()

        # TriggerPut[put]
        BODY = {
          "properties": {
            "custom_context_tag": "CustomContextTags-1235346475",
            "source_info": {
              "share_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/" + DATA_BOX_EDGE_DEVICE_NAME + "/shares/" + SHARE_NAME + ""
            },
            "sink_info": {
              "role_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DataBoxEdge/dataBoxEdgeDevices/" + DATA_BOX_EDGE_DEVICE_NAME + "/roles/" + ROLE_NAME + ""
            }
          },
          "kind": "FileEvent"
        }
        result = self.mgmt_client.triggers.create_or_update(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, TRIGGER_NAME, BODY)
        result = result.result()

        # BandwidthSchedulePut[put]
        BODY = {
          "start": "0:0:0",
          "stop": "13:59:0",
          "rate_in_mbps": "100",
          "days": [
            "Sunday",
            "Monday"
          ]
        }
        result = self.mgmt_client.bandwidth_schedules.create_or_update(DATA_BOX_EDGE_DEVICE_NAME, BANDWIDTH_SCHEDULE_NAME, BODY, resource_group.name)
        result = result.result()

        # SACPut[put]
        BODY = {
          "properties": {
            "alias": "sac1",
            "user_name": "cisbvt",
            "account_key": {
              "value": "lAeZEYi6rNP1/EyNaVUYmTSZEYyaIaWmwUsGwek0+xiZj54GM9Ue9/UA2ed/ClC03wuSit2XzM/cLRU5eYiFBwks23rGwiQOr3sruEL2a74EjPD050xYjA6M1I2hu/w2yjVHhn5j+DbXS4Xzi+rHHNZK3DgfDO3PkbECjPck+PbpSBjy9+6Mrjcld5DIZhUAeMlMHrFlg+WKRKB14o/og56u5/xX6WKlrMLEQ+y6E18dUwvWs2elTNoVO8PBE8SM/CfooX4AMNvaNdSObNBPdP+F6Lzc556nFNWXrBLRt0vC7s9qTiVRO4x/qCNaK/B4y7IqXMllwQFf4Np9UQ2ECA==",
              "encryption_cert_thumbprint": "2A9D8D6BE51574B5461230AEF02F162C5F01AD31",
              "encryption_algorithm": "AES256"
            },
            "ssl_status": "Disabled",
            "account_type": "BlobStorage"
          }
        }
        result = self.mgmt_client.storage_account_credentials.create_or_update(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, STORAGE_ACCOUNT_CREDENTIAL_NAME, BODY)
        result = result.result()

        # SACGet[get]
        result = self.mgmt_client.storage_account_credentials.get(DATA_BOX_EDGE_DEVICE_NAME, STORAGE_ACCOUNT_CREDENTIAL_NAME, resource_group.name)

        # BandwidthScheduleGet[get]
        result = self.mgmt_client.bandwidth_schedules.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, BANDWIDTH_SCHEDULE_NAME)

        # OperationsStatusGet[get]
        result = self.mgmt_client.operations_status.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, OPERATIONS_STATUS_NAME)

        # NetworkSettingsGet[get]
        result = self.mgmt_client.devices.get_network_settings(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, NETWORK_SETTING_NAME)

        # UpdateSummaryGet[get]
        result = self.mgmt_client.devices.get_update_summary(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, UPDATE_SUMMARY_NAME)

        # TriggerGet[get]
        result = self.mgmt_client.triggers.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, TRIGGER_NAME)

        # SACGetAllInDevice[get]
        result = self.mgmt_client.storage_account_credentials.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # AlertGet[get]
        result = self.mgmt_client.alerts.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, ALERT_NAME)

        # ShareGet[get]
        result = self.mgmt_client.shares.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, SHARE_NAME)

        # OrderGet[get]
        result = self.mgmt_client.orders.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, ORDER_NAME)

        # UserGet[get]
        result = self.mgmt_client.users.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, USER_NAME)

        # RoleGet[get]
        result = self.mgmt_client.roles.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, ROLE_NAME)

        # JobsGet[get]
        result = self.mgmt_client.jobs.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, JOB_NAME)

        # BandwidthScheduleGetAllInDevice[get]
        result = self.mgmt_client.bandwidth_schedules.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # TriggerGetAllInDevice[get]
        result = self.mgmt_client.triggers.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # OrderGetAllInDevice[get]
        result = self.mgmt_client.orders.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # AlertGetAllInDevice[get]
        result = self.mgmt_client.alerts.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # ShareGetAllInDevice[get]
        result = self.mgmt_client.shares.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # NodesGetAllInDevice[get]
        result = self.mgmt_client.nodes.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # RoleGetAllInDevice[get]
        result = self.mgmt_client.roles.list_by_data_box_edge_device(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # DataBoxEdgeDeviceGetByName[get]
        result = self.mgmt_client.devices.get(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # DataBoxEdgeDeviceGetByResourceGroup[get]
        result = self.mgmt_client.devices.list_by_resource_group(resource_group.name)

        # DataBoxEdgeDeviceGetBySubscription[get]
        result = self.mgmt_client.devices.list_by_subscription()

        # OperationsGet[get]
        result = self.mgmt_client.operations.list()

        # CreateOrUpdateSecuritySettings[post]
        BODY = {
          "properties": {
            "device_admin_password": {
              "value": "jJ5MvXa/AEWvwxviS92uCjatCXeyLYTy8jx/k105MjQRXT7i6Do8qpEcQ8d+OBbwmQTnwKW0CYyzzVRCc0uZcPCf6PsWtP4l6wvcKGAP66PwK68eEkTUOmp+wUHc4hk02kWmTWeAjBZkuDBP3xK1RnZo95g2RE4i1UgKNP5BEKCLd71O104DW3AWW41mh9XLWNOaxw+VjQY7wmvlE6XkvpkMhcGuha2u7lx8zi9ZkcMvJVYDYK36Fb/K3KhBAmDjjDmVq04jtBlcSTXQObt0nlj4BwGGtdrpeIpr67zqr5i3cPm6e6AleIaIhp6sI/uyGSMiT3oev2eg49u2ii7kVA==",
              "encryption_algorithm": "AES256",
              "encryption_cert_thumbprint": "7DCBDFC44ED968D232C9A998FC105B5C70E84BE0"
            }
          }
        }
        result = self.mgmt_client.devices.create_or_update_security_settings(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, SECURITY_SETTING_NAME, BODY)
        result = result.result()

        # ShareRefreshPost[post]
        result = self.mgmt_client.shares.refresh(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, SHARE_NAME)
        result = result.result()

        # ExtendedInfoPost[post]
        result = self.mgmt_client.devices.get_extended_information(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)

        # UploadCertificatePost[post]
        BODY = {
          "properties": {
            "certificate": "MIIC9DCCAdygAwIBAgIQWJae7GNjiI9Mcv/gJyrOPTANBgkqhkiG9w0BAQUFADASMRAwDgYDVQQDDAdXaW5kb3dzMB4XDTE4MTEyNzAwMTA0NVoXDTIxMTEyODAwMTA0NVowEjEQMA4GA1UEAwwHV2luZG93czCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKxkRExqxf0qH1avnyORptIbRC2yQwqe3EIbJ2FPKr5jtAppGeX/dGKrFSnX+7/0HFr77aJHafdpEAtOiLyJ4zCAVs0obZCCIq4qJdmjYUTU0UXH/w/YzXfQA0d9Zh9AN+NJBX9xj05NzgsT24fkgsK2v6mWJQXT7YcWAsl5sEYPnx1e+MrupNyVSL/RUJmrS+etJSysHtFeWRhsUhVAs1DD5ExJvBLU3WH0IsojEvpXcjrutB5/MDQNrd/StGI6WovoSSPH7FyT9tgERx+q+Yg3YUGzfaIPCctlrRGehcdtzdNoKd0rsX62yCq0U6POoSfwe22NJu41oAUMd7e6R8cCAwEAAaNGMEQwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0OBBYEFDd0VxnS3LnMIfwc7xW4b4IZWG5GMA4GA1UdDwEB/wQEAwIFIDANBgkqhkiG9w0BAQUFAAOCAQEAPQRby2u9celvtvL/DLEb5Vt3/tPStRQC5MyTD62L5RT/q8E6EMCXVZNkXF5WlWucLJi/18tY+9PNgP9xWLJh7kpSWlWdi9KPtwMqKDlEH8L2TnQdjimt9XuiCrTnoFy/1X2BGLY/rCaUJNSd15QCkz2xeW+Z+YSk2GwAc/A/4YfNpqSIMfNuPrT76o02VdD9WmJUA3fS/HY0sU9qgQRS/3F5/0EPS+HYQ0SvXCK9tggcCd4O050ytNBMJC9qMOJ7yE0iOrFfOJSCfDAuPhn/rHFh79Kn1moF+/CE+nc0/2RPiLC8r54/rt5dYyyxJDfXg0a3VrrX39W69WZGW5OXiw=="
          }
        }
        result = self.mgmt_client.devices.upload_certificate(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, BODY)

        # DownloadUpdatesPost[post]
        result = self.mgmt_client.devices.download_updates(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)
        result = result.result()

        # ScanForUpdatesPost[post]
        result = self.mgmt_client.devices.scan_for_updates(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)
        result = result.result()

        # InstallUpdatesPost[post]
        result = self.mgmt_client.devices.install_updates(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME)
        result = result.result()
        """

        # DataBoxEdgeDevicePatch[patch]
        BODY = {
          "tags": {
            "key1": "value1",
            "key2": "value2"
          }
        }
        result = self.mgmt_client.devices.update(DATA_BOX_EDGE_DEVICE_NAME, BODY, resource_group.name)

        """
        # SACDelete[delete]
        result = self.mgmt_client.storage_account_credentials.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, STORAGE_ACCOUNT_CREDENTIAL_NAME)
        result = result.result()

        # BandwidthScheduleDelete[delete]
        result = self.mgmt_client.bandwidth_schedules.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, BANDWIDTH_SCHEDULE_NAME)
        result = result.result()

        # TriggerDelete[delete]
        result = self.mgmt_client.triggers.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, TRIGGER_NAME)
        result = result.result()

        # ShareDelete[delete]
        result = self.mgmt_client.shares.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, SHARE_NAME)
        result = result.result()

        # OrderDelete[delete]
        result = self.mgmt_client.orders.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, ORDER_NAME)
        result = result.result()

        # UserDelete[delete]
        result = self.mgmt_client.users.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, USER_NAME)
        result = result.result()

        # RoleDelete[delete]
        result = self.mgmt_client.roles.delete(resource_group.name, DATA_BOX_EDGE_DEVICE_NAME, ROLE_NAME)
        result = result.result()
        """

        # DataBoxEdgeDeviceDelete[delete]
        result = self.mgmt_client.devices.delete(DATA_BOX_EDGE_DEVICE_NAME, resource_group.name)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
