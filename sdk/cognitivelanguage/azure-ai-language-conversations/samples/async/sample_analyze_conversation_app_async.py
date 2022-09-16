# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_conversation_app_async.py

DESCRIPTION:
    This sample demonstrates how to analyze user query for intents and entities using
    a conversation project with a language parameter.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_analyze_conversation_app_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_PROJECT_NAME     - project name for your CLU conversations project.
    4) AZURE_CONVERSATIONS_DEPLOYMENT_NAME  - deployment name for your CLU conversations project.
"""

import asyncio

async def sample_analyze_conversation_app_async():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.aio import ConversationAnalysisClient

    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # analyze quey
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    async with client:
        query = "Send an email to Carol about the tomorrow's demo"
        result = await client.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "en",
                        "text": query
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": project_name,
                    "deploymentName": deployment_name,
                    "verbose": True
                }
            }
        )

    # view result
    print(f"query: {result['result']['query']}")
    print(f"project kind: {result['result']['prediction']['projectKind']}\n")

    print(f"top intent: {result['result']['prediction']['topIntent']}")
    print(f"category: {result['result']['prediction']['intents'][0]['category']}")
    print(f"confidence score: {result['result']['prediction']['intents'][0]['confidenceScore']}\n")

    print("entities:")
    for entity in result['result']['prediction']['entities']:
        print(f"\ncategory: {entity['category']}")
        print(f"text: {entity['text']}")
        print(f"confidence score: {entity['confidenceScore']}")
        if "resolutions" in entity:
            print("resolutions")
            for resolution in entity['resolutions']:
                print(f"kind: {resolution['resolutionKind']}")
                print(f"value: {resolution['value']}")
        if "extraInformation" in entity:
            print("extra info")
            for data in entity['extraInformation']:
                print(f"kind: {data['extraInformationKind']}")
                if data['extraInformationKind'] == "ListKey":
                    print(f"key: {data['key']}")
                if data['extraInformationKind'] == "EntitySubtype":
                    print(f"value: {data['value']}")

    # [END analyze_conversation_app]


async def main():
    await sample_analyze_conversation_app_async()

if __name__ == '__main__':
    asyncio.run(main())
