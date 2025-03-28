# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.mgmt.trustedsigning import TrustedSigningMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-trustedsigning
# USAGE
    python code_signing_accounts_list_by_subscription.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = TrustedSigningMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    response = client.code_signing_accounts.list_by_subscription()
    for item in response:
        print(item)


# x-ms-original-file: 2024-09-30-preview/CodeSigningAccounts_ListBySubscription.json
if __name__ == "__main__":
    main()
