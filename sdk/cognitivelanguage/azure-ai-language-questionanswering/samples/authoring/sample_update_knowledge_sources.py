# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_update_knowledge_sources.py

DESCRIPTION:
    This sample demonstrates how to update Qna project knowledge sources.

USAGE:
    python sample_update_knowledge_sources.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

def sample_update_knowledge_sources():
    # [START update_knowledge_sources]
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
        client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # synonyms
        client.update_synonyms(
            project_name=project_name,
            synonyms={
                "value": [
                    {
                        "alterations": [
                            "string"
                        ]
                    }
                ]
            }
        )

        synonyms = client.list_synonyms(
            project_name=project_name
        )
        for item in synonyms:
            print(item)

        # qnas
        qna_poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=[
                {
                    'op': 'add',
                    "value": {
                        "id": 0,
                        "answer": "string",
                        "source": "string",
                        "questions": [
                            "string"
                        ]
                    }
                }
            ]
        )
        qna_poller.result()

        qnas = client.list_qnas(
            project_name=project_name
        )
        for item in qnas:
            print(item)

        # sources
        sources_poller = client.begin_update_sources(
            project_name=project_name,
            sources=[
                    {
                        "op": "add",
                        "value": {
                            "sourceKind": "url",
                            "sourceUri": "please/update/with/some/url"
                        }
                    }
                ]
        )
        sources_poller.result()
        sources = client.list_sources(
            project_name=project_name
        )
        for item in sources:
            print(item)

    # [END update_knowledge_sources]


if __name__ == '__main__':
    sample_update_knowledge_sources()
