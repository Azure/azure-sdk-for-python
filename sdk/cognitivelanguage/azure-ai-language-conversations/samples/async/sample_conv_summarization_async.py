# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conv_summarization_async.py

DESCRIPTION:
    This sample demonstrates how to analyze a conversation for issue resolution.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_conv_summarization_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
"""

import asyncio

async def sample_conv_summarization_async():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations.aio import ConversationAnalysisClient

    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    # analyze quey
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    async with client:
        poller = await client.begin_conversation_analysis(
            task={
                "displayName": "Analyze conversations from xxx",
                "analysisInput": {
                    "conversations": [
                        {
                            "conversationItems": [
                                {
                                    "text": "Hello, how can I help you?",
                                    "modality": "text",
                                    "id": "1",
                                    "participantId": "Agent"
                                },
                                {
                                    "text": "How to upgrade Office? I am getting error messages the whole day.",
                                    "modality": "text",
                                    "id": "2",
                                    "participantId": "Customer"
                                },
                                {
                                    "text": "Press the upgrade button please. Then sign in and follow the instructions.",
                                    "modality": "text",
                                    "id": "3",
                                    "participantId": "Agent"
                                }
                            ],
                            "modality": "text",
                            "id": "conversation1",
                            "language": "en"
                        },
                    ]
                },
                "tasks": [
                    {
                        "taskName": "analyze 1",
                        "kind": "ConversationalSummarizationTask",
                        "parameters": {
                            "summaryAspects": ["Issue, Resolution"]
                        }
                    }
                ]
            }
        )

        # view result
        result = await poller.result()
        task_result = result["tasks"]["items"][0]
        print("... view task status ...")
        print("status: {}".format(task_result["status"]))
        resolution_result = task_result["results"]
        if resolution_result["errors"]:
            print("... errors occured ...")
            for error in resolution_result["errors"]:
                print(error)
        else:
            conversation_result = resolution_result["conversations"][0]
            if conversation_result["warnings"]:
                print("... view warnings ...")
                for warning in conversation_result["warnings"]:
                    print(warning)
            else:
                summaries = conversation_result["summaries"]
                print("... view task result ...")
                print("issue: {}".format(summaries[0]["text"]))
                print("resolution: {}".format(summaries[1]["text"]))

    # [END analyze_conversation_app]


async def main():
    await sample_conv_summarization_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())