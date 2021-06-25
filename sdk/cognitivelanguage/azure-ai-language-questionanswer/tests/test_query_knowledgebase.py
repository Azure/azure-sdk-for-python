# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    QuestionAnsweringTest,
    GlobalQuestionAnsweringAccountPreparer,
    QuestionAnsweringClientPreparer
)

from azure.ai.language.questionanswer import QuestionAnsweringClient
from azure.ai.language.questionanswer.rest import *


class QnATests(QuestionAnsweringTest):
    def setUp(self):
        super(QnATests, self).setUp()

    @GlobalQuestionAnsweringAccountPreparer()
    @QuestionAnsweringClientPreparer(QuestionAnsweringClient)
    def test_query_knowledgebase_llc(self, client, question_answering_project):
        json_content = {
            "question": "Ports and connectors",
            "top": 3,
            "context": {
                "previousUserQuery": "Meet Surface Pro 4",
                "previousQnAId": 4
            }
        }
        request = build_query_knowledgebase_request(
            json=json_content,
            project_name=question_answering_project,
            deployment_name='test'
        )
        with client:
            response = client.send_request(request)
            assert response.status_code == 200

        output = response.json()
        assert output
        assert output.get('answers')
        for answer in output['answers']:
            assert answer.get('answer')
            assert answer.get('confidenceScore')
            assert answer.get('id')
            assert answer.get('source')
            assert answer.get('metadata') is not None
            assert not answer.get('answerSpan')
            
            assert answer.get('questions')
            for question in answer['questions']:
                assert question

            assert answer.get('dialog')
            assert answer['dialog'].get('isContextOnly') is not None
            assert answer['dialog'].get('prompts') is not None
            if answer['dialog'].get('prompts'):
                for prompt in answer['dialog']['prompts']:
                    assert prompt.get('displayOrder') is not None
                    assert prompt.get('qnaId')
                    assert prompt.get('displayText')

    @GlobalQuestionAnsweringAccountPreparer()
    @QuestionAnsweringClientPreparer(QuestionAnsweringClient)
    def test_query_knowledgebase_llc_with_answerspan(self, client, question_answering_project):
        json_content = {
            "question": "Ports and connectors",
            "top": 3,
            "context": {
                "previousUserQuery": "Meet Surface Pro 4",
                "previousQnAId": 4
            },
            "answerSpanRequest": {
                "enable": True,
                "confidenceScoreThreshold": 0.1,
                "topAnswersWithSpan": 1
            }
        }
        request = question_answering_knowledgebase.build_query_request(
            json=json_content,
            project_name=question_answering_project,
            deployment_name='test'
        )
        with client:
            response = client.send_request(request)
            assert response.status_code == 200

        output = response.json()
        assert output
        assert output.get('answers')
        for answer in output['answers']:
            assert answer.get('answer')
            assert answer.get('confidenceScore')
            assert answer.get('id')
            assert answer.get('source')
            assert answer.get('metadata') is not None

            if answer.get('answerSpan'):
                assert answer['answerSpan'].get('text')
                assert answer['answerSpan'].get('confidenceScore')
                assert answer['answerSpan'].get('offset') is not None
                assert answer['answerSpan'].get('length')
            
            assert answer.get('questions')
            for question in answer['questions']:
                assert question

            assert answer.get('dialog')
            assert answer['dialog'].get('isContextOnly') is not None
            assert answer['dialog'].get('prompts') is not None
            if answer['dialog'].get('prompts'):
                for prompt in answer['dialog']['prompts']:
                    assert prompt.get('displayOrder') is not None
                    assert prompt.get('qnaId')
                    assert prompt.get('displayText')
