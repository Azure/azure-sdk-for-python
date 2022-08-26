# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_and_deploy_project_async.py

DESCRIPTION:
    This sample demonstrates how to create and deploy a Qna project.

USAGE:
    python sample_create_and_deploy_project_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

import asyncio

async def sample_create_and_deploy_project_async():
    # [START create_and_deploy_project]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.projects.aio import QuestionAnsweringProjectsClient

    # get service secrets
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    # create client
    client = QuestionAnsweringProjectsClient(endpoint, AzureKeyCredential(key))
    async with client:

        # create project
        project_name = "IssacNewton"
        project = await client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        print("view created project info:")
        print(f"\tname: {project['projectName']}")
        print(f"\tlanguage: {project['language']}")
        print(f"\tdescription: {project['description']}")

        # list projects
        print("find created project ..")
        qna_projects = client.list_projects()
        async for p in qna_projects:
            if p["projectName"] == project_name:
                print(f"project: {p['projectName']}")
                print(f"\tlanguage: {p['language']}")
                print(f"\tdescription: {p['description']}")

        # update sources (REQUIRED TO DEPLOY PROJECT)
        update_sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Issac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url"
                    }
                }
            ]
        )
        await update_sources_poller.result()

        # list sources
        print("list project sources")
        sources = client.list_sources(
            project_name=project_name
        )
        async for source in sources:
            print(f"source name: {source.get('displayName', 'N/A')}")
            print(f"\tsource: {source['source']}")
            print(f"\tsource Uri: {source.get('sourceUri', 'N/A')}")
            print(f"\tsource kind: {source['sourceKind']}")

        # deploy project
        deployment_poller = await client.begin_deploy_project(
            project_name=project_name,
            deployment_name="production"
        )
        await deployment_poller.result()

        # list all deployments
        deployments = client.list_deployments(
            project_name=project_name
        )

        print("view project deployments")
        async for d in deployments:
            print(d)

    # [END create_and_deploy_project]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_create_and_deploy_project_async())
