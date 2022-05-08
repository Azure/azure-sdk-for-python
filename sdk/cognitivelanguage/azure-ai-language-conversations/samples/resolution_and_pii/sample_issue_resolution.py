# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_issue_resolution.py

DESCRIPTION:
    This sample demonstrates how to analyze a conversation for issue resolution.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_issue_resolution.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
"""

def sample_issue_resolution():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import (
        AnalyzeConversationJobsInput,
        MultiLanguageConversationAnalysisInput,
        TextConversation,
        TextConversationItem,
        AnalyzeConversationSummarizationTask,
        ConversationSummarizationTaskParameters
    )

    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    # analyze quey
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    with client:
        # submit job
        poller = client.begin_conversation_analysis(
            jobs=AnalyzeConversationJobsInput(
                analysis_input=MultiLanguageConversationAnalysisInput(
                    conversations=[
                        TextConversation(
                            id=1,
                            language="en",
                            conversation_items=[
                                TextConversationItem(
                                    id=1,
                                    participant_id="Agent",
                                    text="Hello, how can I help you?"
                                ),
                                TextConversationItem(
                                    id=2,
                                    participant_id="Customer",
                                    text="How to upgrade Office? I am getting error messages the whole day."
                                ),
                                TextConversationItem(
                                    id=3,
                                    participant_id="Agent",
                                    text="Press the upgrade button please. Then sign in and follow the instructions."
                                )
                            ]
                        )
                    ]
                ),
                tasks=[
                    AnalyzeConversationSummarizationTask(
                        parameters=ConversationSummarizationTaskParameters(
                            summary_aspects="Issue, Resolution"
                        )
                    )
                ]
            )
        )

        # view result
        result = poller.result()
        task_result = result.tasks.items[0]
        print("... view task status ...")
        print("status: {}".format(task_result.status))
        issue_resolution_result = task_result.results
        if issue_resolution_result.errors:
            print("... errors occured ...")
            for error in issue_resolution_result.errors:
                print(error)
        conversation_result = issue_resolution_result.conversations[0]
        if conversation_result.warnings:
            print("... view warnings ...")
            for warning in conversation_result.warnings:
                print(warning)
        summaries = conversation_result.summaries
        print("... view task result ...")
        print("issue: {}".format(summaries[0].text))
        print("resolution: {}".format(summaries[1].text))

    # [END analyze_conversation_app]


if __name__ == '__main__':
    sample_issue_resolution()
