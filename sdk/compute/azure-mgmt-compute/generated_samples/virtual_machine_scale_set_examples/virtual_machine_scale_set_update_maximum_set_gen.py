# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential

from azure.mgmt.compute import ComputeManagementClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-compute
# USAGE
    python virtual_machine_scale_set_update_maximum_set_gen.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = ComputeManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id="{subscription-id}",
    )

    response = client.virtual_machine_scale_sets.begin_update(
        resource_group_name="rgcompute",
        vm_scale_set_name="aaaaaaaaaaaaa",
        parameters={
            "identity": {"type": "SystemAssigned", "userAssignedIdentities": {"key3951": {}}},
            "plan": {
                "name": "windows2016",
                "product": "windows-data-science-vm",
                "promotionCode": "aaaaaaaaaa",
                "publisher": "microsoft-ads",
            },
            "properties": {
                "additionalCapabilities": {"hibernationEnabled": True, "ultraSSDEnabled": True},
                "automaticRepairsPolicy": {"enabled": True, "gracePeriod": "PT30M"},
                "doNotRunExtensionsOnOverprovisionedVMs": True,
                "overprovision": True,
                "proximityPlacementGroup": {
                    "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                },
                "scaleInPolicy": {"forceDeletion": True, "rules": ["OldestVM"]},
                "singlePlacementGroup": True,
                "upgradePolicy": {
                    "automaticOSUpgradePolicy": {
                        "disableAutomaticRollback": True,
                        "enableAutomaticOSUpgrade": True,
                        "osRollingUpgradeDeferral": True,
                    },
                    "mode": "Manual",
                    "rollingUpgradePolicy": {
                        "enableCrossZoneUpgrade": True,
                        "maxBatchInstancePercent": 49,
                        "maxSurge": True,
                        "maxUnhealthyInstancePercent": 81,
                        "maxUnhealthyUpgradedInstancePercent": 98,
                        "pauseTimeBetweenBatches": "aaaaaaaaaaaaaaa",
                        "prioritizeUnhealthyInstances": True,
                        "rollbackFailedInstancesOnPolicyBreach": True,
                    },
                },
                "virtualMachineProfile": {
                    "billingProfile": {"maxPrice": -1},
                    "diagnosticsProfile": {
                        "bootDiagnostics": {
                            "enabled": True,
                            "storageUri": "http://{existing-storage-account-name}.blob.core.windows.net",
                        }
                    },
                    "extensionProfile": {
                        "extensions": [
                            {
                                "name": "{extension-name}",
                                "properties": {
                                    "autoUpgradeMinorVersion": True,
                                    "enableAutomaticUpgrade": True,
                                    "forceUpdateTag": "aaaaaaaaa",
                                    "protectedSettings": {},
                                    "provisionAfterExtensions": ["aa"],
                                    "publisher": "{extension-Publisher}",
                                    "settings": {},
                                    "suppressFailures": True,
                                    "type": "{extension-Type}",
                                    "typeHandlerVersion": "{handler-version}",
                                },
                            }
                        ],
                        "extensionsTimeBudget": "PT1H20M",
                    },
                    "licenseType": "aaaaaaaaaaaa",
                    "networkProfile": {
                        "healthProbe": {
                            "id": "/subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/disk123"
                        },
                        "networkApiVersion": "2020-11-01",
                        "networkInterfaceConfigurations": [
                            {
                                "name": "aaaaaaaa",
                                "properties": {
                                    "deleteOption": "Delete",
                                    "dnsSettings": {"dnsServers": []},
                                    "enableAcceleratedNetworking": True,
                                    "enableFpga": True,
                                    "enableIPForwarding": True,
                                    "ipConfigurations": [
                                        {
                                            "name": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                            "properties": {
                                                "applicationGatewayBackendAddressPools": [
                                                    {
                                                        "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                                                    }
                                                ],
                                                "applicationSecurityGroups": [
                                                    {
                                                        "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                                                    }
                                                ],
                                                "loadBalancerBackendAddressPools": [
                                                    {
                                                        "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                                                    }
                                                ],
                                                "loadBalancerInboundNatPools": [
                                                    {
                                                        "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                                                    }
                                                ],
                                                "primary": True,
                                                "privateIPAddressVersion": "IPv4",
                                                "publicIPAddressConfiguration": {
                                                    "name": "a",
                                                    "properties": {
                                                        "deleteOption": "Delete",
                                                        "dnsSettings": {"domainNameLabel": "aaaaaaaaaaaaaaaaaa"},
                                                        "idleTimeoutInMinutes": 3,
                                                    },
                                                },
                                                "subnet": {
                                                    "id": "/subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/disks/disk123"
                                                },
                                            },
                                        }
                                    ],
                                    "networkSecurityGroup": {
                                        "id": "subscriptions/{subscription-id}/resourceGroups/myResourceGroup/providers/Microsoft.Compute/snapshots/mySnapshot"
                                    },
                                    "primary": True,
                                },
                            }
                        ],
                    },
                    "osProfile": {
                        "customData": "aaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "linuxConfiguration": {
                            "disablePasswordAuthentication": True,
                            "patchSettings": {"assessmentMode": "ImageDefault", "patchMode": "ImageDefault"},
                            "provisionVMAgent": True,
                            "ssh": {
                                "publicKeys": [
                                    {
                                        "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCeClRAk2ipUs/l5voIsDC5q9RI+YSRd1Bvd/O+axgY4WiBzG+4FwJWZm/mLLe5DoOdHQwmU2FrKXZSW4w2sYE70KeWnrFViCOX5MTVvJgPE8ClugNl8RWth/tU849DvM9sT7vFgfVSHcAS2yDRyDlueii+8nF2ym8XWAPltFVCyLHRsyBp5YPqK8JFYIa1eybKsY3hEAxRCA+/7bq8et+Gj3coOsuRmrehav7rE6N12Pb80I6ofa6SM5XNYq4Xk0iYNx7R3kdz0Jj9XgZYWjAHjJmT0gTRoOnt6upOuxK7xI/ykWrllgpXrCPu3Ymz+c+ujaqcxDopnAl2lmf69/J1",
                                        "path": "/home/{your-username}/.ssh/authorized_keys",
                                    }
                                ]
                            },
                        },
                        "secrets": [
                            {
                                "sourceVault": {
                                    "id": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/availabilitySets/{availabilitySetName}"
                                },
                                "vaultCertificates": [
                                    {"certificateStore": "aaaaaaaaaaaaaaaaaaaaaaaaa", "certificateUrl": "aaaaaaa"}
                                ],
                            }
                        ],
                        "windowsConfiguration": {
                            "additionalUnattendContent": [
                                {
                                    "componentName": "Microsoft-Windows-Shell-Setup",
                                    "content": "aaaaaaaaaaaaaaaaaaaa",
                                    "passName": "OobeSystem",
                                    "settingName": "AutoLogon",
                                }
                            ],
                            "enableAutomaticUpdates": True,
                            "patchSettings": {
                                "assessmentMode": "ImageDefault",
                                "automaticByPlatformSettings": {"rebootSetting": "Never"},
                                "enableHotpatching": True,
                                "patchMode": "AutomaticByPlatform",
                            },
                            "provisionVMAgent": True,
                            "timeZone": "aaaaaaaaaaaaaaaa",
                            "winRM": {"listeners": [{"certificateUrl": "aaaaaaaaaaaaaaaaaaaaaa", "protocol": "Http"}]},
                        },
                    },
                    "scheduledEventsProfile": {
                        "terminateNotificationProfile": {"enable": True, "notBeforeTimeout": "PT10M"}
                    },
                    "securityProfile": {
                        "encryptionAtHost": True,
                        "securityType": "TrustedLaunch",
                        "uefiSettings": {"secureBootEnabled": True, "vTpmEnabled": True},
                    },
                    "storageProfile": {
                        "dataDisks": [
                            {
                                "caching": "None",
                                "createOption": "Empty",
                                "diskIOPSReadWrite": 28,
                                "diskMBpsReadWrite": 15,
                                "diskSizeGB": 1023,
                                "lun": 26,
                                "managedDisk": {
                                    "diskEncryptionSet": {"id": "aaaaaaaaaaaa"},
                                    "storageAccountType": "Standard_LRS",
                                },
                                "name": "aaaaaaaaaaaaaaaaaaaaaaaaaa",
                                "writeAcceleratorEnabled": True,
                            }
                        ],
                        "imageReference": {
                            "id": "aaaaaaaaaaaaaaaaaaa",
                            "offer": "WindowsServer",
                            "publisher": "MicrosoftWindowsServer",
                            "sharedGalleryImageId": "aaaaaa",
                            "sku": "2016-Datacenter",
                            "version": "latest",
                        },
                        "osDisk": {
                            "caching": "ReadWrite",
                            "diffDiskSettings": {"option": "Local", "placement": "CacheDisk"},
                            "diskSizeGB": 6,
                            "image": {
                                "uri": "http://{existing-storage-account-name}.blob.core.windows.net/{existing-container-name}/myDisk.vhd"
                            },
                            "managedDisk": {
                                "diskEncryptionSet": {"id": "aaaaaaaaaaaa"},
                                "storageAccountType": "Standard_LRS",
                            },
                            "vhdContainers": ["aa"],
                            "writeAcceleratorEnabled": True,
                        },
                    },
                    "userData": "aaaaaaaaaaaaa",
                },
            },
            "sku": {"capacity": 7, "name": "DSv3-Type1", "tier": "aaa"},
            "tags": {"key246": "aaaaaaaaaaaaaaaaaaaaaaaa"},
            "zones": ["1", "2", "3"],
        },
    ).result()
    print(response)


# x-ms-original-file: specification/compute/resource-manager/Microsoft.Compute/ComputeRP/stable/2024-11-01/examples/virtualMachineScaleSetExamples/VirtualMachineScaleSet_Update_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
