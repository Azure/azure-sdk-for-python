# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# -------------------------------------------------------------------------
# Runtime async tests: knowledge base querying (authoring removed)
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
    async def test_query_knowledgebase_basic(self, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
        )
        async with client:
            output = await client.get_answers(params, project_name=qna_creds["qna_project"], deployment_name="production")
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None

    @pytest.mark.asyncio
    async def test_query_knowledgebase_with_short_answer(self, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
            short_answer_options=ShortAnswerOptions(enable=True, confidence_threshold=0.1, top=2),
        )
        async with client:
            output = await client.get_answers(params, project_name=qna_creds["qna_project"], deployment_name="test")
        assert output.answers
        for answer in output.answers:
            if answer.short_answer:
                assert answer.short_answer.text
                assert answer.short_answer.confidence is not None

    @pytest.mark.asyncio
    async def test_query_knowledgebase_filter(self, qna_creds):
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
                project_name=qna_creds["qna_project"],
                deployment_name="production",
            )
            assert response.answers
            assert any(
                a
                for a in response.answers
                if (a.metadata or {}).get("explicitlytaggedheading") == "check the battery level"
            )
            assert any(
                (a.metadata or {}).get("explicitlytaggedheading") == "make your battery last"
                for a in response.answers
            )

    @pytest.mark.asyncio
    async def test_query_knowledgebase_overload_errors(self):  # negative parameter validation
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                await client.get_answers("positional_one", "positional_two")  # type: ignore[arg-type]
            with pytest.raises(TypeError):
                await client.get_answers("positional_options_bag", options="options bag by name")  # type: ignore[arg-type]
