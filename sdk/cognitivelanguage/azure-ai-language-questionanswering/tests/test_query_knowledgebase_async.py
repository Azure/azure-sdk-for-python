# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# -------------------------------------------------------------------------
# Inference async tests: knowledge base querying (authoring removed)
# -------------------------------------------------------------------------
import pytest

from testcase import QuestionAnsweringTestCase
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    KnowledgeBaseAnswerContext,
    ShortAnswerOptions,
    QueryFilters,
    MetadataFilter,
    MetadataRecord,
)
from azure.core.credentials import AzureKeyCredential


class TestQueryKnowledgeBaseAsync(QuestionAnsweringTestCase):
    @pytest.mark.asyncio
    async def test_query_knowledgebase_basic(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question=qna_seeded_project["previous_question"],
                previous_qna_id=qna_seeded_project["previous_qna_id"],
            ),
        )
        async with client:
            output = await client.get_answers(
                params,
                project_name=qna_seeded_project["project_name"],
                deployment_name="production",
            )
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            if answer.qna_id != -1:
                assert answer.source
            assert answer.metadata is not None

    @pytest.mark.asyncio
    async def test_query_knowledgebase_with_short_answer(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_question=qna_seeded_project["previous_question"],
                previous_qna_id=qna_seeded_project["previous_qna_id"],
            ),
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.1, top=2),
        )
        async with client:
            output = await client.get_answers(
                params,
                project_name=qna_seeded_project["project_name"],
                deployment_name="production",
            )
        assert output.answers
        for answer in output.answers:
            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence is not None

    @pytest.mark.asyncio
    async def test_query_knowledgebase_filter(self, recorded_test, qna_creds, qna_seeded_project): # pylint: disable=unused-argument
        deployment_name = "production"
        filters = QueryFilters(
            metadata_filter=MetadataFilter(
                metadata=[
                    MetadataRecord(key="explicitlytaggedheading", value="check the battery level"),
                    MetadataRecord(key="explicitlytaggedheading", value="make your battery last"),
                ],
                logical_operation="OR",
            )
        )
        async with QuestionAnsweringClient(
            qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])
        ) as client:
            params = AnswersOptions(
                question="Battery life",
                top=3,
                filters=filters,
            )
            response = await client.get_answers(
                params,
                project_name=qna_seeded_project["project_name"],
                deployment_name=deployment_name,
            )
            assert response.answers
            expected_values = {"check the battery level", "make your battery last"}
            assert any((a.metadata or {}).get("explicitlytaggedheading") in expected_values for a in response.answers)

    @pytest.mark.asyncio
    async def test_query_knowledgebase_overload_errors(self):  # negative parameter validation
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                await client.get_answers("positional_one", "positional_two")  # type: ignore[arg-type]
            with pytest.raises(TypeError):
                await client.get_answers("positional_options_bag", options="options bag by name")  # type: ignore[arg-type]
