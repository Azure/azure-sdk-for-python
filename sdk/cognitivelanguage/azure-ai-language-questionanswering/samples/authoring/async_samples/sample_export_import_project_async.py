# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_export_import_project_async.py

DESCRIPTION:
    This sample demonstrates how to export and import a Qna project.

USAGE:
    python sample_export_import_project_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

import asyncio

async def sample_export_import_project_async():
    # [START export_import_project]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient

    # get service secrets
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

    # create client
    client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
    async with client:

        # create project
        project_name = "IssacNewton"
        await client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # export
        export_poller = await client.begin_export(
            project_name=project_name,
            format="json"
        )
        export_result = await export_poller.result()
        export_url = export_result["resultUrl"]

        # import project
        project = {
            "Metadata": {
                "ProjectName": "IssacNewton",
                "Description": "biography of Sir Issac Newton",
                "Language": "en",
                "DefaultAnswer": None,
                "MultilingualResource": False,
                "CreatedDateTime": "2022-01-25T13:10:08Z",
                "LastModifiedDateTime": "2022-01-25T13:10:08Z",
                "LastDeployedDateTime": None,
                "Settings": {
                    "DefaultAnswer": "no answer",
                    "EnableHierarchicalExtraction": None,
                    "DefaultAnswerUsedForExtraction": None
                }
            }
        }
        import_poller = await client.begin_import_assets(
            project_name=project_name,
            options=project
        )
        await import_poller.result()

        # list projects
        print("view all qna projects:")
        qna_projects = client.list_projects()
        async for p in qna_projects:
            if p["projectName"] == project_name:
                print("project: {}".format(p["projectName"]))
                print("\tlanguage: {}".format(p["language"]))
                print("\tdescription: {}".format(p["description"]))

    # [END export_import_project]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_export_import_project_async())
