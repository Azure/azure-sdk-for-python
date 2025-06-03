# coding=utf-8
"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-planetarycomputer
# USAGE
    python geo_catalog_auth_config_operations_get.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient
from azure.core.exceptions import HttpResponseError

def main():
    endpoint = "https://testcatalog-3480.a5cwawdkcbdfgtcw.uksouth.geocatalog.spatio-ppe.azure-test.net"
    client = MicrosoftPlanetaryComputerProClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    try:
        response = client.geo_catalog_auth_config_operations.get()
        try:
            print("JSON Response:", response)
        except Exception as decode_err:
            print("Response received but could not decode as JSON.")
            print("Raw response object:", response)

    except HttpResponseError as http_err:
        print("HTTP Error:", http_err.message)
        if http_err.response:
            print("Status Code:", http_err.response.status_code)
            try:
                print("Error Response Text:", http_err.response.text())
            except Exception:
                print("Could not decode error response text.")
    except Exception as err:
        print("Unhandled exception occurred:", err)

if __name__ == "__main__":
    main()
