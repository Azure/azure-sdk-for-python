# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_orchestration_app_conv_response_async.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration project.
    In this sample, orchestration project's top intent will map to a conversation project.

    For more info about how to setup a CLU orchestration project, see the README.

USAGE:
    python sample_analyze_orchestration_app_conv_response_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME     - project name for your CLU orchestration project.
    4) AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME  - deployment name for your CLU orchestration project.
"""

import asyncio

async def sample_analyze_orchestration_app_conv_response_async():
    # [START analyze_orchestration_app_conv_response]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.aio import ConversationAnalysisClient

    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME"]

    # analyze query
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    async with client:
        query = "Send an email to Carol about the tomorrow's demo"
        result = await client.conversation_analysis.analyze_conversation(
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
    print("query: {}".format(result["result"]["query"]))
    print("project kind: {}\n".format(result["result"]["prediction"]["projectKind"]))

    # top intent
    top_intent = result["result"]["prediction"]["topIntent"]
    print("top intent: {}".format(top_intent))
    top_intent_object = result["result"]["prediction"]["intents"][top_intent]
    print("confidence score: {}".format(top_intent_object["confidenceScore"]))
    print("project kind: {}".format(top_intent_object["targetProjectKind"]))

    # conversation result
    if top_intent_object["targetProjectKind"] == "Conversation":
        print("\nview conversation result:")

        print("\ntop intent: {}".format(top_intent_object["result"]["prediction"]["topIntent"]))
        print("category: {}".format(top_intent_object["result"]["prediction"]["intents"][0]["category"]))
        print("confidence score: {}\n".format(top_intent_object["result"]["prediction"]["intents"][0]["confidenceScore"]))

        print("\nview entities:")
        for entity in top_intent_object["result"]["prediction"]["entities"]:
            print("\ncategory: {}".format(entity["category"]))
            print("text: {}".format(entity["text"]))
            print("confidence score: {}".format(entity["confidenceScore"]))
            if "resolutions" in entity:
                print("resolutions")
                for resolution in entity["resolutions"]:
                    print("kind: {}".format(resolution["resolutionKind"]))
                    print("value: {}".format(resolution["value"]))
            if "extraInformation" in entity:
                print("extra info")
                for data in entity["extraInformation"]:
                    print("kind: {}".format(data["extraInformationKind"]))
                    if data["extraInformationKind"] == "ListKey":
                        print("key: {}".format(data["key"]))
                    if data["extraInformationKind"] == "EntitySubtype":
                        print("value: {}".format(data["value"]))

    # [END analyze_orchestration_app_conv_response]

async def main():
    await sample_analyze_orchestration_app_conv_response_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())