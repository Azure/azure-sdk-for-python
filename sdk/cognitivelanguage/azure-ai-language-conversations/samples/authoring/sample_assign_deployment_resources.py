# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assign_deployment_resources.py

DESCRIPTION:
    This sample demonstrates how to assign deployment resources to a project and deploy a project to specific deployment resources. Assigning resources allow you to train your model in one resource and deploy them to other assigned resources.

USAGE:
    python sample_assign_deployment_resources.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT             - endpoint for your CLU resource.
    2) AZURE_CLIENT_ID                          - the client ID of your active directory application.
    3) AZURE_TENANT_ID                          - the tenant ID of your active directory application.
    4) AZURE_CLIENT_SECRET                      - the secret of your active directory application.
"""

"""
Assigning deployment resources requires you to authenticate with AAD, you cannot assign deployment resources with key based authentication. 
"""
def sample_assign_resources():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.language.conversations.authoring import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    
    client = ConversationAuthoringClient(
        clu_endpoint, credential=credential
    )
    
    project_name = "test_project"

    credential = DefaultAzureCredential()

    poller = client.begin_assign_resource(
        project_name=project_name,
        resourcesMetadata: [
          {
            "azureResourceId": "/subscriptions/80000000-0000-4e8a-0000-7ce285849735/resourceGroups/test-rg/providers/Microsoft.CognitiveServices/accounts/LangTestWeu",
            "customDomain": "lang-test-weu.cognitiveservices.azure.com",
            "region": "westeurope"
          },
          {
            "azureResourceId": "/subscriptions/80000000-0000-4e8a-0000-7ce285849735/resourceGroups/test-rg/providers/Microsoft.CognitiveServices/accounts/LangTestEus",
            "customDomain": "lang-test-eus.cognitiveservices.azure.com",
            "region": "eastus"
          }
        ],
    )
    
    response = poller.result()
    print(response)

def sample_deploy_model():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    project_name = "test_project"
    deployment_name = "production"

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )

    ## If assigned resource Ids are not provided, project is deployed to all assigned resources
    
    poller = client.begin_deploy_project(
        project_name=project_name,
        deployment_name=deployment_name,
        deployment={
          "trainedModelLabel": "sample",
          "assignedResourceIds": [
            "/subscriptions/80000000-0000-4e8a-0000-7ce285849735/resourceGroups/test-rg/providers/Microsoft.CognitiveServices/accounts/LangTestWeu",
            "/subscriptions/80000000-0000-4e8a-0000-7ce285849735/resourceGroups/test-rg/providers/Microsoft.CognitiveServices/accounts/LangTestEus"
          ]
        },
    )
    response = poller.result()
    print(response)


if __name__ == "__main__":
    sample_assign_resources()
    sample_deploy_model()
