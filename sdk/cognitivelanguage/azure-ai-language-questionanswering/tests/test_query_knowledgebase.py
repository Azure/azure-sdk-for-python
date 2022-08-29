# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    QuestionAnsweringTest,
    GlobalQuestionAnsweringAccountPreparer
)

from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering._operations._operations import build_get_answers_request
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    KnowledgeBaseAnswerContext,
    ShortAnswerOptions,
    MetadataFilter,
    QueryFilters,
)


class QnAKnowledgeBaseTests(QuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_llc(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        json_content = {
            "question": "Ports and connectors",
            "top": 3,
            "context": {
                "previousUserQuery": "Meet Surface Pro 4",
                "previousQnAId": 4
            }
        }
        request = build_get_answers_request(
            json=json_content,
            project_name=qna_project,
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
    def test_query_knowledgebase_llc_with_answerspan(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
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
        request = build_get_answers_request(
            json=json_content,
            project_name=qna_project,
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

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question="Meet Surface Pro 4",
                previous_qna_id=4
            )
        )

        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence
            assert answer.qna_id
            assert answer.source
            assert answer.metadata is not None
            assert not answer.short_answer

            assert answer.questions
            for question in answer.questions:
                assert question

            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None
            if answer.dialog.prompts:
                for prompt in answer.dialog.prompts:
                    assert prompt.display_order is not None
                    assert prompt.qna_id
                    assert prompt.display_text

    @pytest.mark.live_test_only
    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_aad(self, qna_account, qna_key, qna_project):
        token = self.get_credential(QuestionAnsweringClient)
        client = QuestionAnsweringClient(qna_account, token)
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question="Meet Surface Pro 4",
                previous_qna_id=4
            )
        )

        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence
            assert answer.qna_id
            assert answer.source
            assert answer.metadata is not None
            assert not answer.short_answer

            assert answer.questions
            for question in answer.questions:
                assert question

            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None
            if answer.dialog.prompts:
                for prompt in answer.dialog.prompts:
                    assert prompt.display_order is not None
                    assert prompt.qna_id
                    assert prompt.display_text

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_with_answerspan(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question="Meet Surface Pro 4",
                previous_qna_id=4
            ),
            short_answer_options=ShortAnswerOptions(
                confidence_threshold=0.1,
                top=2
            )
        )

        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence
            assert answer.qna_id
            assert answer.source
            assert answer.metadata is not None

            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence
                assert answer.short_answer.offset is not None
                assert answer.short_answer.length

            assert answer.questions
            for question in answer.questions:
                assert question

            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None
            if answer.dialog.prompts:
                for prompt in answer.dialog.prompts:
                    assert prompt.display_order is not None
                    assert prompt.qna_id
                    assert prompt.display_text


    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_with_dictparams(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        query_params = {
            "question": "How long should my Surface battery last?",
            "top": 3,
            "userId": "sd53lsY=",
            "confidenceScoreThreshold": 0.2,
            "answerSpanRequest": {
                "enable": True,
                "confidenceScoreThreshold": 0.2,
                "topAnswersWithSpan": 1
            },
            "includeUnstructuredSources": True
        }

        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert len(output.answers) == 3
        confident_answers = [a for a in output.answers if a.confidence > 0.7]
        assert len(confident_answers) == 1
        assert confident_answers[0].source == "surface-book-user-guide-EN.pdf"

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_overload(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            output = client.get_answers(
                project_name=qna_project,
                deployment_name='test',
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                short_answer_options=ShortAnswerOptions(
                    confidence_threshold=0.2,
                    top=1
                ),
                include_unstructured_sources=True
            )

        assert len(output.answers) == 3
        confident_answers = [a for a in output.answers if a.confidence > 0.7]
        assert len(confident_answers) == 1
        assert confident_answers[0].source == "surface-book-user-guide-EN.pdf"

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_with_followup(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            query_params = AnswersOptions(
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                short_answer_options=ShortAnswerOptions(
                    confidence_threshold=0.2,
                    top=1
                ),
                include_unstructured_sources=True
            )

            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )
            confident_answers = [a for a in output.answers if a.confidence > 0.7]
            assert len(confident_answers) == 1
            assert confident_answers[0].source == "surface-book-user-guide-EN.pdf"

            query_params = AnswersOptions(
                question="How long it takes to charge Surface?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                answer_context=KnowledgeBaseAnswerContext(
                    previous_question="How long should my Surface battery last?",
                    previous_qna_id=confident_answers[0].qna_id
                ),
                short_answer_options=ShortAnswerOptions(
                    confidence_threshold=0.2,
                    top=1
                ),
                include_unstructured_sources=True
            )
            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

            assert output.answers
            confident_answers = [a for a in output.answers if a.confidence > 0.48]
            assert len(confident_answers) == 1
            assert confident_answers[0].short_answer.text == " two to four hours"


    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_only_id(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            query_params = AnswersOptions(
                qna_id=19
            )

            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

            assert len(output.answers) == 1

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_python_dict(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            query_params = {"qna_id": 19}

            output = client.get_answers(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

            assert len(output.answers) == 1

    def test_query_knowledgebase_overload_positional_and_kwarg(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                client.get_answers("positional_one", "positional_two")
            with pytest.raises(TypeError):
                client.get_answers("positional_options_bag", options="options bag by name")
            with pytest.raises(TypeError):
                client.get_answers(
                    options={'qnaId': 15},
                    project_name="hello",
                    deployment_name='test'
                )
            with pytest.raises(TypeError):
                client.get_answers(
                    {'qnaId': 15},
                    question='Why?',
                    project_name="hello",
                    deployment_name='test'
                )

    def test_query_knowledgebase_question_or_qna_id(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:

            options = AnswersOptions()
            with pytest.raises(TypeError):
                client.get_answers(
                    options,
                    project_name="hello",
                    deployment_name='test'
                )

            with pytest.raises(TypeError):
                client.get_answers(
                    project_name="hello",
                    deployment_name='test'
                )

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_filter(self, qna_account, qna_key, qna_project):
        """Thanks to @heaths for this test!"""
        filters = QueryFilters(
            metadata_filter=MetadataFilter(
                metadata=[
                    ("explicitlytaggedheading", "check the battery level"),
                    ("explicitlytaggedheading", "make your battery last")
                ],
                logical_operation="OR"
            ),
        )
        with QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key)) as client:
            response = client.get_answers(
                project_name=qna_project,
                deployment_name='test',
                question="Battery life",
                filters=filters,
                top=3,
            )
            assert len(response.answers) == 2
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "check the battery level"]
            )
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "make your battery last"]
            )

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_filter_dict_params(self, qna_account, qna_key, qna_project):
        filters = {
            "metadataFilter": {
                "metadata": [
                    ("explicitlytaggedheading", "check the battery level"),
                    ("explicitlytaggedheading", "make your battery last")
                ],
                "logicalOperation": "or"
            },
        }
        with QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key)) as client:
            response = client.get_answers(
                project_name=qna_project,
                deployment_name='test',
                question="Battery life",
                filters=filters,
                top=3,
            )
            assert len(response.answers) == 2
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "check the battery level"]
            )
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "make your battery last"]
            )
