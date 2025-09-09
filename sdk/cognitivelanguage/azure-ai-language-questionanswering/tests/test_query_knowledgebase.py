# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest

from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    KnowledgeBaseAnswerContext,
    ShortAnswerOptions,
    MetadataFilter,
    QueryFilters,
)
from azure.core.credentials import AzureKeyCredential

from testcase import QuestionAnsweringTestCase


class TestQnAKnowledgeBase(QuestionAnsweringTestCase):
    """Sync knowledge base tests covering:
    - Operations group (LLC-style) via client.question_answering.get_answers
    - Convenience wrapper client.get_answers with model / dict / kwargs overloads
    - Short answer optional path
    - Filters normalization (model + dict)
    - Overload & validation error scenarios
    """

    def test_query_knowledgebase_llc(self, recorded_test, qna_creds):
        # LLC style: direct operations call with a model (no convenience normalization beyond model)
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        options = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_user_query="Meet Surface Pro 4",
                previous_qna_id=4,
            ),
        )
        with client:
            output = client.question_answering.get_answers(
                options, project_name=qna_creds["qna_project"], deployment_name="test"
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None
            # No short answer requested in this test
            assert not answer.short_answer
            assert answer.questions
            for q in answer.questions:
                assert q
            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None
            if answer.dialog.prompts:
                for prompt in answer.dialog.prompts:
                    assert prompt.display_order is not None
                    assert prompt.qna_id
                    assert prompt.display_text

    def test_query_knowledgebase_llc_with_answerspan(self, recorded_test, qna_creds):
        # Request short answers (answer span) via model
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        options = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_user_query="Meet Surface Pro 4",
                previous_qna_id=4,
            ),
            short_answer_options=ShortAnswerOptions(confidence_threshold=0.1, top=1),
        )
        with client:
            output = client.question_answering.get_answers(
                options, project_name=qna_creds["qna_project"], deployment_name="test"
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None
            # Short answer is optional; only assert internals if present
            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence is not None
                assert answer.short_answer.offset is not None
                assert answer.short_answer.length
            assert answer.questions
            for q in answer.questions:
                assert q
            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None

    def test_query_knowledgebase(self, recorded_test, qna_creds):
        # Convenience wrapper with model
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
        )
        with client:
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None
            assert not answer.short_answer
            assert answer.questions
            for q in answer.questions:
                assert q
            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None

    @pytest.mark.skipif(
        not all(os.getenv(v) for v in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")),
        reason="AAD environment variables not configured",
    )
    def test_query_knowledgebase_aad(self, recorded_test, qna_creds):
        token = self.get_credential(QuestionAnsweringClient)
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], token)
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
        )
        with client:
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert output.answers

    def test_query_knowledgebase_with_answerspan(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
            short_answer_options=ShortAnswerOptions(confidence_threshold=0.1, top=2),
        )
        with client:
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None
            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence is not None
                assert answer.short_answer.offset is not None
                assert answer.short_answer.length

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_query_knowledgebase_with_dictparams(self, recorded_test, qna_creds):
        # Dict style convenience (aliases should normalize)
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = {
            "question": "How long should my Surface battery last?",
            "top": 3,
            "userId": "sd53lsY=",
            "confidenceScoreThreshold": 0.2,
            "shortAnswerOptions": {"confidence_threshold": 0.2, "top": 1},
            "includeUnstructuredSources": True,
        }
        with client:
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert len(output.answers) == 3
        confident_answers = [a for a in output.answers if a.confidence > 0.7]
        assert len(confident_answers) == 1

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_query_knowledgebase_overload(self, recorded_test, qna_creds):
        # kwargs style convenience
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        with client:
            output = client.get_answers(
                project_name=qna_creds["qna_project"],
                deployment_name="test",
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                short_answer_options=ShortAnswerOptions(confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
        assert len(output.answers) == 3

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    def test_query_knowledgebase_with_followup(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        with client:
            first_query = AnswersOptions(
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                short_answer_options=ShortAnswerOptions(confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
            first_output = client.get_answers(
                first_query, project_name=qna_creds["qna_project"], deployment_name="test"
            )
            confident_answers = [a for a in first_output.answers if a.confidence > 0.8]
            assert len(confident_answers) == 1

            followup = AnswersOptions(
                question="How long it takes to charge Surface?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                answer_context=KnowledgeBaseAnswerContext(
                    previous_question="How long should my Surface battery last?",
                    previous_qna_id=confident_answers[0].qna_id,
                ),
                short_answer_options=ShortAnswerOptions(confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
            second_output = client.get_answers(
                followup, project_name=qna_creds["qna_project"], deployment_name="test"
            )
            assert second_output.answers

    def test_query_knowledgebase_only_id(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        with client:
            query_params = AnswersOptions(qna_id=19)
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert len(output.answers) == 1

    def test_query_knowledgebase_python_dict(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        with client:
            # dict using canonical wire field
            query_params = {"qnaId": 19}
            output = client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert len(output.answers) == 1

    def test_query_knowledgebase_overload_positional_and_kwarg(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                client.get_answers("positional_one", "positional_two")
            with pytest.raises(TypeError):
                client.get_answers("positional_options_bag", options="options bag by name")
            with pytest.raises(TypeError):
                client.get_answers(options={"qnaId": 15}, project_name="hello", deployment_name="test")
            with pytest.raises(TypeError):
                client.get_answers({"qnaId": 15}, question="Why?", project_name="hello", deployment_name="test")

    def test_query_knowledgebase_question_or_qna_id(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            options = AnswersOptions()
            with pytest.raises(TypeError):
                client.get_answers(options, project_name="hello", deployment_name="test")
            with pytest.raises(TypeError):
                client.get_answers(project_name="hello", deployment_name="test")

    def test_query_knowledgebase_filter(self, recorded_test, qna_creds):
        filters = QueryFilters(
            metadata_filter=MetadataFilter(
                metadata=[
                    ("explicitlytaggedheading", "check the battery level"),
                    ("explicitlytaggedheading", "make your battery last"),
                ],
                logical_operation="OR",
            ),
        )
        with QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])) as client:
            response = client.get_answers(
                project_name=qna_creds["qna_project"],
                deployment_name="test",
                question="Battery life",
                filters=filters,
                top=3,
            )
        assert len(response.answers) == 2
        assert any(a.metadata.get("explicitlytaggedheading") == "check the battery level" for a in response.answers)
        assert any(a.metadata.get("explicitlytaggedheading") == "make your battery last" for a in response.answers)

    def test_query_knowledgebase_filter_dict_params(self, recorded_test, qna_creds):
        filters = {
            "metadataFilter": {
                "metadata": [
                    {"key": "explicitlytaggedheading", "value": "check the battery level"},
                    {"key": "explicitlytaggedheading", "value": "make your battery last"},
                ],
                "logicalOperation": "OR",
            }
        }
        with QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])) as client:
            response = client.get_answers(
                project_name=qna_creds["qna_project"],
                deployment_name="test",
                question="Battery life",
                filters=filters,
                top=3,
            )
        assert len(response.answers) == 2
        assert any(a.metadata.get("explicitlytaggedheading") == "check the battery level" for a in response.answers)
        assert any(a.metadata.get("explicitlytaggedheading") == "make your battery last" for a in response.answers)
