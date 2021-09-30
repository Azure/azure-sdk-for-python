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
from azure.ai.language.questionanswering.operations._operations import build_query_text_request, build_query_knowledge_base_request
from azure.ai.language.questionanswering.models import (
    QueryKnowledgeBaseOptions,
    KnowledgeBaseAnswerRequestContext,
    AnswerSpanRequest,
    MetadataFilter,
    LogicalOperationKind,
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
        request = build_query_knowledge_base_request(
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
        request = build_query_knowledge_base_request(
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
        query_params = QueryKnowledgeBaseOptions(
            question="Ports and connectors",
            top=3,
            context=KnowledgeBaseAnswerRequestContext(
                previous_user_query="Meet Surface Pro 4",
                previous_qna_id=4
            )
        )

        with client:
            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence_score
            assert answer.id
            assert answer.source
            assert answer.metadata is not None
            assert not answer.answer_span

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
        query_params = QueryKnowledgeBaseOptions(
            question="Ports and connectors",
            top=3,
            context=KnowledgeBaseAnswerRequestContext(
                previous_user_query="Meet Surface Pro 4",
                previous_qna_id=4
            ),
            answer_span_request=AnswerSpanRequest(
                enable=True,
                confidence_score_threshold=0.1,
                top_answers_with_span=2
            )
        )

        with client:
            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence_score
            assert answer.id
            assert answer.source
            assert answer.metadata is not None

            if answer.answer_span:
                assert answer.answer_span.text
                assert answer.answer_span.confidence_score
                assert answer.answer_span.offset is not None
                assert answer.answer_span.length

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
            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

        assert len(output.answers) == 2
        confident_answers = [a for a in output.answers if a.confidence_score > 0.9]
        assert len(confident_answers) == 1
        assert confident_answers[0].source == "surface-pro-4-user-guide-EN.pdf"

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_overload(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            output = client.query_knowledge_base(
                project_name=qna_project,
                deployment_name='test',
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_score_threshold=0.2,
                answer_span_request=AnswerSpanRequest(
                    enable=True,
                    confidence_score_threshold=0.2,
                    top_answers_with_span=1
                ),
                include_unstructured_sources=True
            )

        assert len(output.answers) == 2
        confident_answers = [a for a in output.answers if a.confidence_score > 0.9]
        assert len(confident_answers) == 1
        assert confident_answers[0].source == "surface-pro-4-user-guide-EN.pdf"

    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_with_followup(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            query_params = QueryKnowledgeBaseOptions(
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_score_threshold=0.2,
                answer_span_request=AnswerSpanRequest(
                    enable=True,
                    confidence_score_threshold=0.2,
                    top_answers_with_span=1
                ),
                include_unstructured_sources=True
            )

            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )
            confident_answers = [a for a in output.answers if a.confidence_score > 0.9]
            assert len(confident_answers) == 1
            assert confident_answers[0].source == "surface-pro-4-user-guide-EN.pdf"

            query_params = QueryKnowledgeBaseOptions(
                question="How long it takes to charge Surface?",
                top=3,
                user_id="sd53lsY=",
                confidence_score_threshold=0.2,
                context=KnowledgeBaseAnswerRequestContext(
                    previous_user_query="How long should my Surface battery last?",
                    previous_qna_id=confident_answers[0].id
                ),
                answer_span_request=AnswerSpanRequest(
                    enable=True,
                    confidence_score_threshold=0.2,
                    top_answers_with_span=1
                ),
                include_unstructured_sources=True
            )
            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

            assert len(output.answers) == 2
            confident_answers = [a for a in output.answers if a.confidence_score > 0.5]
            assert len(confident_answers) == 1
            assert confident_answers[0].answer_span.text == " two to four hours"


    @GlobalQuestionAnsweringAccountPreparer()
    def test_query_knowledgebase_only_id(self, qna_account, qna_key, qna_project):
        client = QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key))
        with client:
            query_params = QueryKnowledgeBaseOptions(
                qna_id=19
            )

            output = client.query_knowledge_base(
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

            output = client.query_knowledge_base(
                query_params,
                project_name=qna_project,
                deployment_name='test'
            )

            assert len(output.answers) == 1

    def test_query_knowledgebase_overload_positional_and_kwarg(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                client.query_knowledge_base("positional_one", "positional_two")
            with pytest.raises(TypeError):
                client.query_knowledge_base("positional_options_bag", options="options bag by name")

    def test_query_knowledgebase_question_or_qna_id(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:

            options = QueryKnowledgeBaseOptions()
            with pytest.raises(TypeError):
                client.query_knowledge_base(
                    options,
                    project_name="hello",
                    deployment_name='test'
                )

            with pytest.raises(TypeError):
                client.query_knowledge_base(
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
            ),
            logical_operation=LogicalOperationKind.OR_ENUM
        )
        with QuestionAnsweringClient(qna_account, AzureKeyCredential(qna_key)) as client:
            response = client.query_knowledge_base(
                project_name=qna_project,
                deployment_name='test',
                question="Battery life",
                filters=filters,
                top=3,
            )
            assert len(response.answers) == 3
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "check the battery level"]
            )
            assert any(
                [a for a in response.answers if a.metadata.get('explicitlytaggedheading') == "make your battery last"]
            )
