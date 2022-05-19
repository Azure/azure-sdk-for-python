# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_orchestration_direct_target_async.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration project.
    In this sample, orchestration project's top intent will map to a Qna project.

    For more info about how to setup a CLU orchestration project, see the README.

USAGE:
    python sample_analyze_orchestration_direct_target_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME     - project name for your CLU orchestration project.
    4) AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME  - deployment name for your CLU orchestration project.
"""

import asyncio

async def sample_analyze_orchestration_direct_target_async():
    # [START analyze_orchestration_app_qna_response]
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
        query = "How are you?"
        qna_app = "ChitChat-QnA"
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
                    "directTarget": qna_app,
                    "targetProjectParameters": {
                        "ChitChat-QnA": {
                            "targetProjectKind": "QuestionAnswering",
                            "callingOptions": {
                                "question": query
                            }
                        }
                    }
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

    if top_intent_object["targetProjectKind"] == "QuestionAnswering":
        print("\nview qna result:")
        qna_result = top_intent_object["result"]
        for answer in qna_result["answers"]:
            print("\nanswer: {}".format(answer["answer"]))
            print("answer: {}".format(answer["confidenceScore"]))

    # [END analyze_orchestration_app_qna_response]


async def main():
    await sample_analyze_orchestration_direct_target_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())