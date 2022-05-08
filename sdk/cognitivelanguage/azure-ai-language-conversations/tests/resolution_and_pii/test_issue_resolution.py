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
    TextConversation,
    TextConversationItem,
    AnalyzeConversationSummarizationTask,
    ConversationSummarizationTaskParameters,
    ConversationsSummaryResultSummariesItem,
    SummaryResultConversationsItem,
    SummaryResult,
    AnalyzeConversationSummarizationResult,
    ConversationTasksStateTasks,
    AnalyzeConversationJobState
)


class IssueResolutionTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_issue_resolution(self, endpoint, key):
        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            poller = client.begin_conversation_analysis(
                body=AnalyzeConversationJobsInput(
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

            result = poller.result()

            assert not result is None
            assert isinstance(result, AnalyzeConversationJobState)
            assert isinstance(result.tasks, ConversationTasksStateTasks)

            task_result = result.tasks.items[0]
            assert isinstance(task_result, AnalyzeConversationSummarizationResult)
            
            issue_resolution_result = task_result.results
            assert isinstance(issue_resolution_result, SummaryResult)

            # assert status
            status = task_result.status
            if status == "failed":
                assert issue_resolution_result.errors
                assert len(issue_resolution_result.errors) > 0
            else:
                # assert result
                conversation_result = issue_resolution_result.conversations[0]
                assert isinstance(conversation_result, SummaryResultConversationsItem)
                
                # assert warnings
                if conversation_result.warnings:
                    assert len(conversation_result.warnings) > 0

                # assert result
                summaries = conversation_result.summaries
                assert isinstance(summaries, ConversationsSummaryResultSummariesItem)
                assert summaries[0].text is not None
                assert summaries[1].text is not None

    @GlobalConversationAccountPreparer()
    def test_issue_resolution_dict_parms(self, endpoint, key):
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
                            "kind": "IssueResolutionSummarization",
                            "parameters": {
                                "modelVersion": "2022-04-01",
                                "summaryAspects": "Issue, Resolution"
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
            assert isinstance(task_result, AnalyzeConversationSummarizationResult)
            
            issue_resolution_result = task_result.results
            assert isinstance(issue_resolution_result, SummaryResult)

            # assert status
            status = task_result.status
            if status == "failed":
                assert issue_resolution_result.errors
                assert len(issue_resolution_result.errors) > 0
            else:
                # assert result
                conversation_result = issue_resolution_result.conversations[0]
                assert isinstance(conversation_result, SummaryResultConversationsItem)
                
                # assert warnings
                if conversation_result.warnings:
                    assert len(conversation_result.warnings) > 0

                # assert result
                summaries = conversation_result.summaries
                assert isinstance(summaries, ConversationsSummaryResultSummariesItem)
                assert summaries[0].text is not None
                assert summaries[1].text is not None


