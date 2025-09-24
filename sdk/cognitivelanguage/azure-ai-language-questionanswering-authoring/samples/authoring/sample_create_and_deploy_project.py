"""Sample - Create and deploy a Question Answering authoring project.

This sample demonstrates how to:
  * Create an authoring project
  * Add a knowledge source
  * Deploy the project
  * List deployments

Environment variables required:
  * AZURE_QUESTIONANSWERING_ENDPOINT - endpoint of your Language resource
  * AZURE_QUESTIONANSWERING_KEY - API key

Run with: python sample_create_and_deploy_project.py
"""

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient


def sample_create_and_deploy_project():
    # [START create_and_deploy_project]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    with client:
        project_name = "IsaacNewton"
        project = client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )

        print("Created project:")
        print(f"  name: {project['projectName']}")
        print(f"  language: {project['language']}")
        print(f"  description: {project['description']}")

        print("Listing projects and confirming creation...")
        for p in client.list_projects():
            if p["projectName"] == project_name:
                print(f"Found project {p['projectName']}")

        update_sources_poller = client.begin_update_sources(
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
        sources = update_sources_poller.result()

        print("Knowledge sources:")
        for source in sources:
            print(f"  {source.get('displayName', 'N/A')} -> {source.get('sourceUri', 'N/A')}")

        deployment_poller = client.begin_deploy_project(
            project_name=project_name, deployment_name="production"
        )
        deployment = deployment_poller.result()
        print(f"Deployment created: {deployment['deploymentName']}")

        print("Project deployments:")
        for d in client.list_deployments(project_name=project_name):
            print(f"  {d['deploymentName']} (lastDeployed: {d.get('lastDeployedDateTime', 'N/A')})")
    # [END create_and_deploy_project]


if __name__ == "__main__":
    sample_create_and_deploy_project()
