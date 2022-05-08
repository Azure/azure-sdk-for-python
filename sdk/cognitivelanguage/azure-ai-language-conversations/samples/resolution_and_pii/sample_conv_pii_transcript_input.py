# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conv_pii_transcript_input.py

DESCRIPTION:
    This sample demonstrates how to analyze a conversation for PII (personally identifiable information).

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_conv_pii_transcript_input.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
"""

from azure.ai.language import conversations


def sample_conv_pii_transcript_input():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import (
        AnalyzeConversationJobsInput,
        MultiLanguageConversationAnalysisInput,
        TranscriptConversation,
        TranscriptConversationItem,
        TranscriptConversationItemContent,
        AnalyzeConversationPIITask,
        ConversationPIITaskParameters
    )

    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    # analyze quey
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    with client:

        poller = client.begin_conversation_analysis(
            body=AnalyzeConversationJobsInput(
                analysis_input=MultiLanguageConversationAnalysisInput(
                    conversations=[
                        TranscriptConversation(
                            id=1,
                            language="en",
                            conversation_items=[
                                TranscriptConversationItem(
                                    id=1,
                                    participant_id=0,
                                    content=TranscriptConversationItemContent(
                                        text="It is john doe.",
                                        lexical="It is john doe",
                                        itn="It is john doe",
                                        masked_itn="It is john doe"
                                    )
                                ),
                                TranscriptConversationItem(
                                    id=2,
                                    participant_id=1,
                                    content=TranscriptConversationItemContent(
                                        text="Yes, 633-27-8199 is my phone",
                                        lexical="yes six three three two seven eight one nine nine is my phone",
                                        itn="yes 633278199 is my phone",
                                        masked_itn="yes 633278199 is my phone"
                                    )
                                ),
                                TranscriptConversationItem(
                                    id=3,
                                    participant_id=1,
                                    content=TranscriptConversationItemContent(
                                        text="j.doe@yahoo.com is my email",
                                        lexical="j dot doe at yahoo dot com is my email",
                                        masked_itn="j.doe@yahoo.com is my email",
                                        itn="j.doe@yahoo.com is my email"
                                    )
                                )
                            ]
                        )
                    ]
                ),
                tasks=[
                    AnalyzeConversationPIITask(
                        parameters=ConversationPIITaskParameters(
                            pii_categories=["all"]
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
        conv_pii_result = task_result.results
        if conv_pii_result.errors:
            print("... errors occured ...")
            for error in conv_pii_result.errors:
                print(error)
        conversation_result = conv_pii_result.conversations[0]
        if conversation_result.warnings:
            print("... view warnings ...")
            for warning in conversation_result.warnings:
                print(warning)
        print("... view task result ...")
        for conversation in conversation_result.conversation_items:
            print("conversation id: {}".format(conversation.id))
            print("... entities ...")
            for entity in conversation.entities:
                print("text: {}".format(entity.text))
                print("category: {}".format(entity.category))
                print("confidence: {}".format(entity.confidence_score))
                print("offset: {}".format(entity.offset))
                print("length: {}".format(entity.length))


    # [END analyze_conversation_app]


if __name__ == '__main__':
    sample_conv_pii_transcript_input()
