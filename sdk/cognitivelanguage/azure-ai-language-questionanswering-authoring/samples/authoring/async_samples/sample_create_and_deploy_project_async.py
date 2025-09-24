"""Async sample - Create and deploy a Question Answering authoring project."""
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient


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
                {
                    "op": "add",
                    "value": {
                        "displayName": "Isaac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url",
                    },
                }
            ],
        )
        sources = await update_sources_poller.result()
        print("Knowledge sources:")
        async for source in sources:
            print(f"  {source.get('displayName', 'N/A')} -> {source.get('sourceUri', 'N/A')}")

        deployment_poller = await client.begin_deploy_project(
            project_name=project_name, deployment_name="production"
        )
        deployment = await deployment_poller.result()
        print(f"Deployment created: {deployment['deploymentName']}")

        print("Project deployments:")
        async for d in client.list_deployments(project_name=project_name):
            print(f"  {d['deploymentName']}")
    # [END create_and_deploy_project]


if __name__ == "__main__":
    asyncio.run(sample_create_and_deploy_project_async())
