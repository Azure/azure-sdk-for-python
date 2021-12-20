# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_and_deploy_project.py

DESCRIPTION:
    This sample demonstrates how to create and deploy a Qna project.

USAGE:
    python sample_create_and_deploy_project.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

def sample_create_and_deploy_project():
    # [START query_text]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.projects import QuestionAnsweringProjectsClient

    # get service secrets
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    # create client
    client = QuestionAnsweringProjectsClient(endpoint, AzureKeyCredential(key))
    with client:

        # create project
        project_name = "IssacNewton"
        project = client.create_project(
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
        print(u"\tname: {}".format(project["projectName"]))
        print(u"\tlanguage: {}".format(project["language"]))
        print(u"\tdescription: {}".format(project["description"]))

        # list projects
        print("view all qna projects:")
        qna_projects = client.list_projects()
        for p in qna_projects:
            print(u"project: {}".format(p["projectName"]))
            print(u"\tlanguage: {}".format(p["language"]))
            print(u"\tdescription: {}".format(p["description"]))

        # update sources
        update_sources_poller = client.begin_update_sources(
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
        update_sources_poller.result()

        # list sources
        print("list project sources")
        sources = client.list_sources(
            project_name=project_name
        )
        for source in sources:
            print(u"\project: {}".format(source["displayName"]))
            print(u"\tsource: {}".format(source["source"]))
            print(u"\tsource Uri: {}".format(source["sourceUri"]))
            print(u"\tsource kind: {}".format(source["sourceKind"]))

        # deploy project
        deployment_poller = client.begin_deploy_project(
            project_name=project_name,
            deployment_name="production"
        )
        deployment_poller.result()

        # list all deployments
        deployments = client.list_deployments(
            project_name=project_name
        )

        print("view project deployments")
        for d in deployments:
            print(d)

    # [END query_text]


if __name__ == '__main__':
    sample_create_and_deploy_project()
