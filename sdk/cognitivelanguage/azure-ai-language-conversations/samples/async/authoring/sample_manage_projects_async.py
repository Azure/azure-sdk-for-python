# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_manage_projects_async.py

DESCRIPTION:
    This sample demonstrates some common authoring operation snippets with the ConversationAuthoringClient.

USAGE:
    python sample_manage_projects_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT             - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                  - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_PROJECT_NAME         - project name for your existing CLU conversations project
"""

import asyncio
import uuid


async def sample_export_project():
    import os
    from azure.core.rest import HttpRequest
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    existing_project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )
    async with client:
        poller = await client.begin_export_project(
            project_name=existing_project_name,
            string_index_type="Utf16CodeUnit",
            exported_project_format="Conversation"
        )
        job_state = await poller.result()
        print(f"Export project status: {job_state['status']}")
        request = HttpRequest("GET", job_state["resultUrl"])
        response = await client.send_request(request)
        exported_project = response.json()
        return exported_project


async def sample_import_project(exported_project, project_name):
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    print(f"Importing project as '{project_name}'")
    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )
    async with client:
        poller = await client.begin_import_project(
            project_name=project_name,
            project=exported_project
        )
        response = await poller.result()
        print(f"Import project status: {response['status']}")
        return project_name


async def sample_train_model(project_name):
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )
    print(f"Training model under label 'sample'.")
    async with client:
        poller = await client.begin_train(
            project_name=project_name,
            configuration={"modelLabel": "sample", "trainingMode": "standard"},
        )

        response = await poller.result()
        print(f"Train model status: {response['status']}")


async def sample_deploy_model(project_name):
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    deployment_name = "production"

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )

    print(f"Deploying 'sample' model to 'production'.")
    async with client:
        poller = await client.begin_deploy_project(
            project_name=project_name,
            deployment_name=deployment_name,
            deployment={"trainedModelLabel": "sample"},
        )
        response = await poller.result()
        print(f"Model '{response['modelId']}' deployed to '{response['deploymentName']}'")


async def sample_delete_project(project_name):
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    client = ConversationAuthoringClient(
        clu_endpoint, AzureKeyCredential(clu_key)
    )
    async with client:
        poller = await client.begin_delete_project(
            project_name=project_name
        )
        await poller.result()
        print(f"Deleted project {project_name}")


async def main():
    project_name = "test_project" + str(uuid.uuid4())
    try:
        print("Exporting project...")
        project = await sample_export_project()
        print("Importing project...")
        project_name = await sample_import_project(project, project_name)
        print("Training model...")
        await sample_train_model(project_name)
        print("Deploying model...")
        await sample_deploy_model(project_name)
    finally:
        print("Deleting project...")
        await sample_delete_project(project_name)

if __name__ == '__main__':
    asyncio.run(main())
