"""Async sample - Create and deploy a Question Answering authoring project."""

import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering.authoring import models as _models


async def sample_create_and_deploy_project_async():
    # [START create_and_deploy_project]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:
        project_name = "IsaacNewton"
        project = await client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        print(f"Created project {project['projectName']}")

        print("Listing projects and confirming creation...")
        async for p in client.list_projects():
            if p["projectName"] == project_name:
                print(f"Found project {p['projectName']}")

        update_sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                _models.UpdateSourceRecord(
                    op="add",
                    value=_models.UpdateQnaSourceRecord(
                        display_name="Isaac Newton Bio",
                        source="https://wikipedia.org/wiki/Isaac_Newton",
                        source_uri="https://wikipedia.org/wiki/Isaac_Newton",
                        source_kind="url",
                        content_structure_kind="unstructured",
                        refresh=False,
                    ),
                )
            ],
        )
        await update_sources_poller.result()
        print("Knowledge sources updated (1 URL added)")

        deployment_poller = await client.begin_deploy_project(project_name=project_name, deployment_name="production")
        await deployment_poller.result()  # completes; no payload
        print("Deployment created: production")

        print("Project deployments:")
        async for d in client.list_deployments(project_name=project_name):
            print(f"  {d['deploymentName']}")
    # [END create_and_deploy_project]


if __name__ == "__main__":
    asyncio.run(sample_create_and_deploy_project_async())
