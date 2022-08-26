# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_update_knowledge_sources_async.py

DESCRIPTION:
    This sample demonstrates how to update Qna project knowledge sources.

USAGE:
    python sample_update_knowledge_sources_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_QUESTIONANSWERING_ENDPOINT - the endpoint to your QuestionAnswering resource.
    2) AZURE_QUESTIONANSWERING_KEY - your QuestionAnswering API key.
"""

import asyncio

async def sample_update_knowledge_sources_async():
    # [START update_knowledge_sources]
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
        project_name = "Microsoft"
        await client.create_project(
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
        sources_poller = await client.begin_update_sources(
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
        await sources_poller.result() # wait until done

        sources = client.list_sources(
            project_name=project_name
        )
        async for item in sources:
            print(f"source name: {item.get('displayName', 'N/A')}")
            print(f"\tsource: {item['source']}")
            print(f"\tsource uri: {item.get('sourceUri', 'N/A')}")
            print(f"\tsource kind: {item['sourceKind']}")

        # qnas
        qna_poller = await client.begin_update_qnas(
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
        await qna_poller.result()

        qnas = client.list_qnas(
            project_name=project_name
        )
        async for item in qnas:
            print(f"qna: {item['id']}")
            print("\tquestions:")
            for question in item["questions"]:
                print(f"\t\t{question}")
            print(f"\tanswer: {item['answer']}")

        # synonyms
        await client.update_synonyms(
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
        async for item in synonyms:
            print("synonyms:")
            print("\talterations:")
            for alt in item["alterations"]:
                print(f"\t\t{alt}")
            print('')

    # [END update_knowledge_sources]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_update_knowledge_sources_async())
