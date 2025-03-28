# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.health.deidentification import DeidentificationClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-health-deidentification
# USAGE
    python deidentify_text.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = DeidentificationClient(
        endpoint="ENDPOINT",
        credential=DefaultAzureCredential(),
    )

    response = client.deidentify_text(
        body={
            "customizations": {"redactionFormat": "[{type}]"},
            "inputText": "Hello my name is John Smith.",
            "operation": "Redact",
        },
    )
    print(response)


# x-ms-original-file: 2024-11-15/DeidentifyText.json
if __name__ == "__main__":
    main()
