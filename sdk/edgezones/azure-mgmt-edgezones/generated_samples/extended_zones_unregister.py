# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.mgmt.edgezones import EdgeZonesMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-edgezones
# USAGE
    python extended_zones_unregister.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = EdgeZonesMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    response = client.extended_zones.unregister(
        extended_zone_name="losangeles",
    )
    print(response)


# x-ms-original-file: 2024-04-01-preview/ExtendedZones_Unregister.json
if __name__ == "__main__":
    main()
