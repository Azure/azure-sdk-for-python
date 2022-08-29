# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_import_train_deploy_project_async.py

DESCRIPTION:
    This sample demonstrates how to import a project.

USAGE:
    python sample_import_train_deploy_project_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT             - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                  - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_PROJECT_NAME         - project name for your CLU conversations project.
"""

import asyncio

async def sample_import_project():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    project_name = "test_project"

    exported_project_assets = {
        "projectKind": "Conversation",
        "intents": [{"category": "Read"}, {"category": "Delete"}],
        "entities": [{"category": "Sender"}],
        "utterances": [
            {
                "text": "Open Blake's email",
                "dataset": "Train",
                "intent": "Read",
                "entities": [{"category": "Sender", "offset": 5, "length": 5}],
            },
            {
                "text": "Delete last email",
                "language": "en-gb",
                "dataset": "Test",
                "intent": "Delete",
                "entities": [],
            },
        ],
    }

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )
    poller = await client.begin_import_project(
        project_name=project_name,
        project={
            "assets": exported_project_assets,
            "metadata": {
                "projectKind": "Conversation",
                "settings": {"confidenceThreshold": 0.7},
                "projectName": "EmailApp",
                "multilingual": True,
                "description": "Trying out CLU",
                "language": "en-us",
            },
            "projectFileVersion": "2022-05-01",
        },
    )
    response = await poller.result()
    print(response)


async def sample_train_model():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    project_name = "test_project"

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )

    poller = await client.begin_train(
        project_name=project_name,
        configuration={"modelLabel": "sample", "trainingMode": "standard"},
    )

    response = await poller.result()
    print(response)


async def sample_deploy_model():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    project_name = "test_project"
    deployment_name = "production"

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )

    poller = await client.begin_deploy_project(
        project_name=project_name,
        deployment_name=deployment_name,
        deployment={"trainedModelLabel": "sample"},
    )
    response = await poller.result()
    print(response)


async def main():
    await sample_import_project()
    await sample_train_model()
    await sample_deploy_model()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())