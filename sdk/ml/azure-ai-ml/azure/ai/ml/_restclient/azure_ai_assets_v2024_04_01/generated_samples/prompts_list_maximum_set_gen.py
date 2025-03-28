# coding=utf-8

from azure.identity import DefaultAzureCredential

from azure.ai.resources.autogen import MachineLearningServicesClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-ai-resources-autogen
# USAGE
    python prompts_list_maximum_set_gen.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = MachineLearningServicesClient(
        endpoint="ENDPOINT",
        subscription_id="SUBSCRIPTION_ID",
        resource_group_name="RESOURCE_GROUP_NAME",
        workspace_name="WORKSPACE_NAME",
        credential=DefaultAzureCredential(),
    )

    response = client.prompts.list(
        name="abcdefghijklmnopqrstuv",
        list_view_type="gsnfbluqlj",
    )
    for item in response:
        print(item)


# x-ms-original-file: 2024-05-01-preview/Prompts_List_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
