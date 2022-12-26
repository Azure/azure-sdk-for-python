# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assign_deployment_resources.py

DESCRIPTION:
    This sample demonstrates how to assign deployment resources to a project and deploy a project
    to specific deployment resources. Assigning resources allow you to train your model in one
    resource and deploy them to other assigned resources.

    Assigning deployment resources requires you to authenticate with AAD, you cannot assign
    deployment resources with key based authentication. You must have the role Cognitive Services
    Language Owner assigned to the authoring resource and the target resources.

USAGE:
    python sample_assign_deployment_resources.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT             - endpoint for your CLU resource.
    2) AZURE_CLIENT_ID                          - the client ID of your active directory application.
    3) AZURE_TENANT_ID                          - the tenant ID of your active directory application.
    4) AZURE_CLIENT_SECRET                      - the secret of your active directory application.
"""


def sample_assign_resources():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.language.conversations.authoring import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = ConversationAuthoringClient(clu_endpoint, credential=credential)

    project_name = "test_project"

    poller = client.begin_assign_deployment_resources(
        project_name=project_name,
        body={
            "resourcesMetadata": [
                {
                    "azureResourceId": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.CognitiveServices/accounts/<resource-name>",
                    "customDomain": "<resource-name>.cognitiveservices.azure.com",
                    "region": "<region>",
                },
                {
                    "azureResourceId": "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.CognitiveServices/accounts/<resource-name>",
                    "customDomain": "<resource-name>.cognitiveservices.azure.com",
                    "region": "<region>",
                },
            ],
        },
    )

    response = poller.result()
    print(response)


def sample_deploy_model():
    import os
    from azure.identity import DefaultAzureCredential
    from azure.ai.language.conversations.authoring import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    project_name = "test_project"
    deployment_name = "production"

    client = ConversationAuthoringClient(clu_endpoint, credential=credential)

    ## If assigned resource Ids are not provided, project is deployed to all assigned resources

    poller = client.begin_deploy_project(
        project_name=project_name,
        deployment_name=deployment_name,
        deployment={
            "trainedModelLabel": "sample",
            "assignedResourceIds": [
                "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.CognitiveServices/accounts/<resource-name>",
                "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.CognitiveServices/accounts/<resource-name>",
            ],
        },
    )
    response = poller.result()
    print(response)


if __name__ == "__main__":
    sample_assign_resources()
    sample_deploy_model()
