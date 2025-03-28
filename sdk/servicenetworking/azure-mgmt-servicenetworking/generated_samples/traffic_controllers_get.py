# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.mgmt.servicenetworking import ServiceNetworkingMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-servicenetworking
# USAGE
    python traffic_controllers_get.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = ServiceNetworkingMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    response = client.traffic_controller_interface.list_by_resource_group(
        resource_group_name="rg1",
    )
    for item in response:
        print(item)


# x-ms-original-file: 2025-03-01-preview/TrafficControllersGet.json
if __name__ == "__main__":
    main()
