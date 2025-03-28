# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.mgmt.deviceregistry import DeviceRegistryMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-deviceregistry
# USAGE
    python delete_asset_endpoint_profile.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = DeviceRegistryMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    client.asset_endpoint_profiles.begin_delete(
        resource_group_name="myResourceGroup",
        asset_endpoint_profile_name="my-assetendpointprofile",
    ).result()


# x-ms-original-file: 2024-11-01/Delete_AssetEndpointProfile.json
if __name__ == "__main__":
    main()
