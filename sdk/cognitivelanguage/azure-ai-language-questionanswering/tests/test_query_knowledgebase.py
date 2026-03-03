# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# -------------------------------------------------------------------------
# Inference tests: knowledge base querying (authoring removed)
# -------------------------------------------------------------------------
import pytest

from testcase import QuestionAnsweringTestCase
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    KnowledgeBaseAnswerContext,
    ShortAnswerOptions,
    MetadataFilter,
    MetadataRecord,
    QueryFilters,
)
from azure.core.credentials import AzureKeyCredential


class TestQnAKnowledgeBase(QuestionAnsweringTestCase):
    def test_query_knowledgebase(self, recorded_test, qna_creds, qna_seeded_project):  # standard model usage # pylint: disable=unused-argument
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question=qna_seeded_project["previous_question"],
                previous_qna_id=qna_seeded_project["previous_qna_id"],
            ),
        )
        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_seeded_project["project_name"],
                deployment_name="production",
            )
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            # Some projects may return a default "no answer" entry (id == -1) without a source.
            if answer.qna_id != -1:
                assert answer.source

    def test_query_knowledgebase_with_answerspan(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question=qna_seeded_project["previous_question"],
                previous_qna_id=qna_seeded_project["previous_qna_id"],
            ),
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.1, top=2),
        )
        with client:
            output = client.get_answers(
                query_params,
                project_name=qna_seeded_project["project_name"],
                deployment_name="production",
            )
        assert output.answers
        # If short answer returned, essential fields exist
        for answer in output.answers:
            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence is not None

    def test_query_knowledgebase_filter(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        deployment_name = "production"
        filters = QueryFilters(
            metadata_filter=MetadataFilter(
                metadata=[
                    MetadataRecord(key="explicitlytaggedheading", value="check the battery level"),
                    MetadataRecord(key="explicitlytaggedheading", value="make your battery last"),
                ],
                logical_operation="OR",
            ),
        )
        with QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])) as client:
            query_params = AnswersOptions(
                question="Battery life",
                filters=filters,
                top=3,
            )
            response = client.get_answers(
                query_params,
                project_name=qna_seeded_project["project_name"],
                deployment_name=deployment_name,
            )
            assert response.answers
            expected_values = {"check the battery level", "make your battery last"}
            assert any((a.metadata or {}).get("explicitlytaggedheading") in expected_values for a in response.answers)

    def test_query_knowledgebase_only_id(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        with client:
            query_params = AnswersOptions(qna_id=qna_seeded_project["qna_id_only"])
            output = client.get_answers(
                query_params,
                project_name=qna_seeded_project["project_name"],
                deployment_name="production",
            )
            assert output.answers is not None
            assert len(output.answers) == 1

    def test_query_knowledgebase_overload_errors(self):  # negative tests independent of live service
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            # These calls intentionally violate the method signature to ensure TypeError is raised.
            with pytest.raises(TypeError):
                client.get_answers("positional_one", "positional_two")  # type: ignore # pylint: disable=too-many-function-args, missing-kwoa
            with pytest.raises(TypeError):
                client.get_answers("positional_options_bag", options="options bag by name")  # type: ignore # pylint: disable=missing-kwoa
            with pytest.raises(TypeError):
                client.get_answers(options={"qnaId": 15}, project_name="hello", deployment_name="production")  # type: ignore # pylint: disable=no-value-for-parameter
            with pytest.raises(TypeError):
                client.get_answers({"qnaId": 15}, question="Why?", project_name="hello", deployment_name="production")  # type: ignore

    def test_query_knowledgebase_question_or_qna_id(self):
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            options = AnswersOptions()
            with pytest.raises(TypeError):
                client.get_answers(options, project_name="hello", deployment_name="production")
            with pytest.raises(TypeError):
                client.get_answers(project_name="hello", deployment_name="production") # pylint: disable=no-value-for-parameter
