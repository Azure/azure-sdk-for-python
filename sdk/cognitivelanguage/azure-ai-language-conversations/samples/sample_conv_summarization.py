# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conv_summarization.py

DESCRIPTION:
    This sample demonstrates how to analyze a conversation for issue resolution.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_conv_summarization.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
"""

def sample_conv_summarization():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient

    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    # analyze query
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    with client:
        poller = client.begin_conversation_analysis(
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
                                    "role": "Agent",
                                    "participantId": "Agent"
                                },
                                {
                                    "text": "How to upgrade Office? I am getting error messages the whole day.",
                                    "modality": "text",
                                    "id": "2",
                                    "role": "Customer",
                                    "participantId": "Customer"
                                },
                                {
                                    "text": "Press the upgrade button please. Then sign in and follow the instructions.",
                                    "modality": "text",
                                    "id": "3",
                                    "role": "Agent",
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
                        "taskName": "Issue task",
                        "kind": "ConversationalSummarizationTask",
                        "parameters": {
                            "summaryAspects": ["issue"]
                        }
                    },
                    {
                        "taskName": "Resolution task",
                        "kind": "ConversationalSummarizationTask",
                        "parameters": {
                            "summaryAspects": ["resolution"]
                        }
                    },
                ]
            }
        )

        # view result
        result = poller.result()
        task_results = result["tasks"]["items"]
        for task in task_results:
            print(f"\n{task['taskName']} status: {task['status']}")
            task_result = task["results"]
            if task_result["errors"]:
                print("... errors occurred ...")
                for error in task_result["errors"]:
                    print(error)
            else:
                conversation_result = task_result["conversations"][0]
                if conversation_result["warnings"]:
                    print("... view warnings ...")
                    for warning in conversation_result["warnings"]:
                        print(warning)
                else:
                    summaries = conversation_result["summaries"]
                    print("... view task result ...")
                    for summary in summaries:
                        print(f"{summary['aspect']}: {summary['text']}")

    # [END analyze_conversation_app]


if __name__ == '__main__':
    sample_conv_summarization()
