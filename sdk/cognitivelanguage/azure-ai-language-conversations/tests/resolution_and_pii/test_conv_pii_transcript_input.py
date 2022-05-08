# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    ConversationTest,
    GlobalConversationAccountPreparer
)

from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    AnalyzeConversationJobsInput,
    MultiLanguageConversationAnalysisInput,
    TranscriptConversation,
    TranscriptConversationItem,
    TranscriptConversationItemContent,
    AnalyzeConversationPIITask,
    ConversationPIITaskParameters,
    ConversationTasksStateTasks,
    AnalyzeConversationJobState,
    Entity,
    AnalyzeConversationPIIResult,
    ConversationPIIResults,
    ConversationPIIResultsConversationsItem,
    ConversationPIIItemResult
)


class ConversationPIITests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_conversation_pii(self, endpoint, key):
        # analyze query
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

            result = poller.result()

            assert not result is None
            assert isinstance(result, AnalyzeConversationJobState)
            assert isinstance(result.tasks, ConversationTasksStateTasks)

            task_result = result.tasks.items[0]
            assert isinstance(task_result, AnalyzeConversationPIIResult)
            
            conversation_result = task_result.results
            assert isinstance(conversation_result, ConversationPIIResults)

            # assert status
            status = task_result.status
            if status == "failed":
                assert conversation_result.errors
                assert len(conversation_result.errors) > 0
            else:
                # assert result
                conversation_result = conversation_result.conversations[0]
                assert isinstance(conversation_result, ConversationPIIResultsConversationsItem)
                
                # assert warnings
                if conversation_result.warnings:
                    assert len(conversation_result.warnings) > 0

                # assert result
                for conversation in conversation_result.conversation_items:
                    assert isinstance(conversation, ConversationPIIItemResult)
                    for entity in conversation.entities:
                        assert isinstance(entity, Entity)
                        assert entity.text
                        assert entity.category
                        assert entity.confidence_score
                        assert entity.offset
                        assert entity.length

    @GlobalConversationAccountPreparer()
    def test_conversation_pii_dict_parms(self, endpoint, key):
        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            poller = client.begin_conversation_analysis(
                body={
                    "displayName": "Analyze conversations from xxx",
                    "analysisInput": {
                        "conversations": [
                            {
                                "conversationItems": [
                                    {
                                        "content": {
                                            "text": "It is john doe.",
                                            "lexical": "It is john doe",
                                            "itn": "It is john doe",
                                            "maskedItn": "It is john doe",
                                            "audioTiming": []
                                        },
                                        "id": "1",
                                        "participantId": "0",
                                        "modality": "transcript"
                                    },
                                    {
                                        "content": {
                                            "text": "Yes, 633-27-8199 is my phone",
                                            "lexical": "yes six three three two seven eight one nine nine is my phone",
                                            "itn": "yes 633278199 is my phone",
                                            "maskedItn": "yes 633278199 is my phone",
                                            "audioTiming": []
                                        },
                                        "id": "2",
                                        "participantId": "1",
                                        "modality": "transcript"
                                    },
                                    {
                                        "content": {
                                            "text": "j.doe@yahoo.com is my email",
                                            "lexical": "j dot doe at yahoo dot com is my email",
                                            "maskedItn": "j.doe@yahoo.com is my email",
                                            "itn": "j.doe@yahoo.com is my email",
                                            "audioTiming": []
                                        },
                                        "id": "3",
                                        "participantId": "1",
                                        "modality": "transcript"
                                    }
                                ],
                                "modality": "transcript",
                                "id": "1",
                                "language": "en"
                            }
                        ]
                    },
                    "tasks": [
                        {
                            "taskName": "analyze 1",
                            "kind": "ConversationPII",
                            "parameters": {
                                "modelVersion": "2022-04-01",
                                "redactionSource": "text",
                                "loggingOptOut": "false",
                                "piiCategories": [
                                    "all"
                                ]
                            }
                        }
                    ]
                }
            )

            result = poller.result()

            assert not result is None
            assert isinstance(result, AnalyzeConversationJobState)
            assert isinstance(result.tasks, ConversationTasksStateTasks)

            task_result = result.tasks.items[0]
            assert isinstance(task_result, AnalyzeConversationPIIResult)
            
            conversation_result = task_result.results
            assert isinstance(conversation_result, ConversationPIIResults)

            # assert status
            status = task_result.status
            if status == "failed":
                assert conversation_result.errors
                assert len(conversation_result.errors) > 0
            else:
                # assert result
                conversation_result = conversation_result.conversations[0]
                assert isinstance(conversation_result, ConversationPIIResultsConversationsItem)
                
                # assert warnings
                if conversation_result.warnings:
                    assert len(conversation_result.warnings) > 0

                # assert result
                for conversation in conversation_result.conversation_items:
                    assert isinstance(conversation, ConversationPIIItemResult)
                    for entity in conversation.entities:
                        assert isinstance(entity, Entity)
                        assert entity.text
                        assert entity.category
                        assert entity.confidence_score
                        assert entity.offset
                        assert entity.length
