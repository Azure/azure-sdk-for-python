# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.communication.jobrouter import JobRouterAdministrationClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-communication-jobrouter
# USAGE
    python classification_policies_get_classification_policy.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = JobRouterAdministrationClient(
        endpoint="https://contoso.westus.communications.azure.com",
        credential=DefaultAzureCredential(),
    )

    response = client.get_classification_policy(
        classification_policy_id="MainClassificationPolicy",
    )
    print(response)


# x-ms-original-file: 2024-01-18-preview/ClassificationPolicies_GetClassificationPolicy.json
if __name__ == "__main__":
    main()
