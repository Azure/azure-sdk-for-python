# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

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
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient, models as _models


def sample_create_and_deploy_project():
    # [START create_and_deploy_project]
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    with client:
        project_name = "IsaacNewton"
        project = client.create_project( # pylint: disable=no-value-for-parameter
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

        update_sources_poller = client.begin_update_sources( # pylint: disable=no-value-for-parameter
            project_name=project_name,
            sources=[
                _models.UpdateSourceRecord(
                    op="add",
                    value=_models.UpdateQnaSourceRecord(
                        display_name="Isaac Newton Bio",
                        source="https://wikipedia.org/wiki/Isaac_Newton",  # source id
                        source_uri="https://wikipedia.org/wiki/Isaac_Newton",
                        source_kind="url",
                        content_structure_kind="unstructured",
                        refresh=False,
                    ),
                )
            ],
        )
        update_sources_poller.result()  # completes; no return payload
        print("Knowledge sources updated (1 URL added)")

        deployment_poller = client.begin_deploy_project(project_name=project_name, deployment_name="production")
        deployment_poller.result()  # LRO completes; no deployment payload returned in current SDK
        print("Deployment created: production")

        print("Project deployments:")
        for d in client.list_deployments(project_name=project_name):
            print(f"  {d['deploymentName']} (lastDeployed: {d.get('lastDeployedDateTime', 'N/A')})")
    # [END create_and_deploy_project]


if __name__ == "__main__":
    sample_create_and_deploy_project()
