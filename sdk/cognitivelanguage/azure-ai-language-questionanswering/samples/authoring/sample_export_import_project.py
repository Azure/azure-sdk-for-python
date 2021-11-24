# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_export_import_project.py

DESCRIPTION:
    This sample demonstrates how to export and import a Qna project.

USAGE:
    python sample_export_import_project.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

def sample_export_import_project():
    # [START query_text]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.projects import QuestionAnsweringProjectsClient
    from azure.ai.language.questionanswering.projects import models

    # get service secrets
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    # create client
    client = QuestionAnsweringProjectsClient(endpoint, AzureKeyCredential(key))
    with client:

        # create project
        project_name = "IssacNewton"
        client.question_answering_projects.create_project(
            project_name=project_name,
            body={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # export
        export_poller = client.question_answering_projects.begin_export(
            project_name=project_name
        )
        export_poller.result()

        # delete old project
        delete_poller = client.question_answering_projects.delete_project(
            project_name=project_name
        )
        delete_poller.result()

        # import project
        import_poller = client.question_answering_projects.begin_import_method(
            project_name=project_name,
            file_uri="asdsadasdasd"
        )
        import_poller.result()

        # list projects
        print("view all qna projects:")
        qna_projects = client.question_answering_projects.list_projects()
        for p in qna_projects:
            print(u"project: {}".format(p.project_name))
            print(u"\tlanguage: {}".format(p.language))
            print(u"\tdescription: {}".format(p.description))

        client.question_answering_projects.get_project_details(
            project_name=project_name
        )
    # [END query_text]


if __name__ == '__main__':
    sample_export_import_project()
