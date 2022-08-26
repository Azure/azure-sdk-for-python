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
        project_name = "Microsoft"
        client.create_project(
            project_name=project_name,
            options={
                "description": "test project for some Microsoft QnAs",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # sources
        sources_poller = client.begin_update_sources(
            project_name=project_name,
            sources=[{
                "op": "add",
                "value": {
                    "displayName": "MicrosoftFAQ",
                    "source": "https://www.microsoft.com/en-in/software-download/faq",
                    "sourceUri": "https://www.microsoft.com/en-in/software-download/faq",
                    "sourceKind": "url",
                    "contentStructureKind": "unstructured",
                    "refresh": False
                }
            }]
        )
        sources_poller.result() # wait until done

        sources = client.list_sources(
            project_name=project_name
        )
        for item in sources:
            print(f"source name: {item.get('displayName', 'N/A')}")
            print(f"\tsource: {item['source']}")
            print(f"\tsource uri: {item.get('sourceUri', 'N/A')}")
            print(f"\tsource kind: {item['sourceKind']}")

        # qnas
        qna_poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=[{
                "op": "add",
                "value": {
                    "questions": [
                        "What is the easiest way to use azure services in my .NET project?"
                    ],
                    "answer": "Using Microsoft's Azure SDKs"
                }
            }]
        )
        qna_poller.result()

        qnas = client.list_qnas(
            project_name=project_name
        )
        for item in qnas:
            print(f"qna: {item['id']}")
            print("\tquestions:")
            for question in item['questions']:
                print(f"\t\t{question}")
            print(f"\tanswer: {item['answer']}")

        # synonyms
        client.update_synonyms(
            project_name=project_name,
            synonyms={
                "value": [
                    {
                        "alterations": [
                            "qnamaker",
                            "qna maker"
                        ]
                    },
                    {
                        "alterations": [
                            "qna",
                            "question and answer"
                        ]
                    }
                ]
            }
        )
        synonyms = client.list_synonyms(
            project_name=project_name
        )
        for item in synonyms:
            print("synonyms:")
            print("\talterations:")
            for alt in item["alterations"]:
                print(f"\t\t{alt}")
            print('')

    # [END update_knowledge_sources]


if __name__ == '__main__':
    sample_update_knowledge_sources()
