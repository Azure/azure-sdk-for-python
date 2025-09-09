# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import pytest

from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    KnowledgeBaseAnswerContext,
    ShortAnswerOptions,
    QueryFilters,
    MetadataFilter,
)
from azure.core.credentials import AzureKeyCredential

from testcase import QuestionAnsweringTestCase


class TestQnAKnowledgeBaseAsync(QuestionAnsweringTestCase):
    """Async knowledge base tests covering:
    - Operations group vs convenience (model / dict / kwargs)
    - Short answer optional path
    - Filters normalization (model + dict)
    - Follow-up / context chaining
    - Validation and overload error scenarios
    """

    @pytest.mark.asyncio
    async def test_query_knowledgebase_llc(self, recorded_test, qna_creds):
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
        async with client:
            output = await client.question_answering.get_answers(
                options, project_name=qna_creds["qna_project"], deployment_name="test"
            )

        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.qna_id is not None
            assert answer.source
            assert answer.metadata is not None
            assert not answer.short_answer  # no short answer requested
            assert answer.questions
            for q in answer.questions:
                assert q
            assert answer.dialog
            assert answer.dialog.is_context_only is not None
            assert answer.dialog.prompts is not None

    @pytest.mark.asyncio
    async def test_query_knowledgebase_llc_with_answerspan(self, recorded_test, qna_creds):
        # LLC style with short answer request via model
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        options = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(
                previous_user_query="Meet Surface Pro 4",
                previous_qna_id=4,
            ),
            short_answer_options=ShortAnswerOptions(confidence_threshold=0.1, top=2),
        )
        async with client:
            output = await client.question_answering.get_answers(
                options, project_name=qna_creds["qna_project"], deployment_name="test"
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
            assert answer.questions
            for q in answer.questions:
                assert q
            assert answer.dialog

    @pytest.mark.asyncio
    async def test_query_knowledgebase(self, recorded_test, qna_creds):
        # Convenience wrapper with model
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
        )
        async with client:
            output = await client.get_answers(
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

    @pytest.mark.skipif(
        not all(os.getenv(v) for v in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")),
        reason="AAD environment variables not configured",
    )
    @pytest.mark.asyncio
    async def test_query_knowledgebase_aad(self, recorded_test, qna_creds):
        token = self.get_credential(QuestionAnsweringClient, is_async=True)
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], token)
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_question="Meet Surface Pro 4", previous_qna_id=4),
        )
        async with client:
            output = await client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert output.answers

    @pytest.mark.asyncio
    async def test_query_knowledgebase_with_answerspan(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = AnswersOptions(
            question="Ports and connectors",
            top=3,
            answer_context=KnowledgeBaseAnswerContext(previous_user_query="Meet Surface Pro 4", previous_qna_id=4),
            short_answer_options=ShortAnswerOptions(confidence_threshold=0.1, top=2),
        )
        async with client:
            output = await client.get_answers(
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
    @pytest.mark.asyncio
    async def test_query_knowledgebase_with_dictparams(self, recorded_test, qna_creds):
        # Dict input through convenience wrapper (aliases should normalize)
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        query_params = {
            "question": "How long should my Surface battery last?",
            "top": 3,
            "userId": "sd53lsY=",
            "confidenceScoreThreshold": 0.2,
            "shortAnswerOptions": {"confidence_threshold": 0.2, "top": 1},
            "includeUnstructuredSources": True,
        }
        async with client:
            output = await client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )

        assert len(output.answers) == 3
        confident_answers = [a for a in output.answers if a.confidence > 0.7]
        assert len(confident_answers) == 1

    @pytest.mark.live_test_only("Needs re-recording to work with new common sanitizers")
    @pytest.mark.asyncio
    async def test_query_knowledgebase_overload(self, recorded_test, qna_creds):
        # kwargs style convenience
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        async with client:
            output = await client.get_answers(
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
    @pytest.mark.asyncio
    async def test_query_knowledgebase_with_followup(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        async with client:
            first = AnswersOptions(
                question="How long should my Surface battery last?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                short_answer_options=ShortAnswerOptions(confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
            first_out = await client.get_answers(
                first, project_name=qna_creds["qna_project"], deployment_name="test"
            )
            confident = [a for a in first_out.answers if a.confidence > 0.8]
            assert len(confident) == 1

            follow = AnswersOptions(
                question="How long it takes to charge Surface?",
                top=3,
                user_id="sd53lsY=",
                confidence_threshold=0.2,
                answer_context=KnowledgeBaseAnswerContext(
                    previous_question="How long should my Surface battery last?",
                    previous_qna_id=confident[0].qna_id,
                ),
                short_answer_options=ShortAnswerOptions(confidence_threshold=0.2, top=1),
                include_unstructured_sources=True,
            )
            second_out = await client.get_answers(
                follow, project_name=qna_creds["qna_project"], deployment_name="test"
            )
            assert second_out.answers

    @pytest.mark.asyncio
    async def test_query_knowledgebase_only_id(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        async with client:
            query_params = {"qnaId": 19}
            output = await client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert len(output.answers) == 1

    @pytest.mark.asyncio
    async def test_query_knowledgebase_python_dict(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        async with client:
            query_params = {"qna_id": 19}  # alias form
            output = await client.get_answers(
                query_params, project_name=qna_creds["qna_project"], deployment_name="test"
            )
        assert len(output.answers) == 1

    @pytest.mark.asyncio
    async def test_query_knowledgebase_overload_positional_and_kwarg(self):
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                await client.get_answers("positional_one", "positional_two")
            with pytest.raises(TypeError):
                await client.get_answers("positional_options_bag", options="options bag by name")

    @pytest.mark.asyncio
    async def test_query_knowledgebase_question_or_qna_id(self):
        async with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            options = AnswersOptions()
            with pytest.raises(TypeError):
                await client.get_answers(options, project_name="hello", deployment_name="test")
            with pytest.raises(TypeError):
                await client.get_answers(project_name="hello", deployment_name="test")

    @pytest.mark.asyncio
    async def test_query_knowledgebase_filter(self, recorded_test, qna_creds):
        filters = QueryFilters(
            metadata_filter=MetadataFilter(
                metadata=[
                    ("explicitlytaggedheading", "check the battery level"),
                    ("explicitlytaggedheading", "make your battery last"),
                ],
                logical_operation="OR",
            )
        )
        async with QuestionAnsweringClient(
            qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])
        ) as client:
            response = await client.get_answers(
                project_name=qna_creds["qna_project"],
                deployment_name="test",
                question="Battery life",
                filters=filters,
                top=3,
            )
        assert len(response.answers) == 2
        assert any(a.metadata.get("explicitlytaggedheading") == "check the battery level" for a in response.answers)
        assert any(a.metadata.get("explicitlytaggedheading") == "make your battery last" for a in response.answers)

    @pytest.mark.asyncio
    async def test_query_knowledgebase_filter_dict_params(self, recorded_test, qna_creds):
        filters = {
            "metadataFilter": {
                "metadata": [
                    {"key": "explicitlytaggedheading", "value": "check the battery level"},
                    {"key": "explicitlytaggedheading", "value": "make your battery last"},
                ],
                "logicalOperation": "OR",
            }
        }
        async with QuestionAnsweringClient(
            qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"])
        ) as client:
            response = await client.get_answers(
                project_name=qna_creds["qna_project"],
                deployment_name="test",
                question="Battery life",
                filters=filters,
                top=3,
            )
        assert len(response.answers) == 2
        assert any(a.metadata.get("explicitlytaggedheading") == "check the battery level" for a in response.answers)
        assert any(a.metadata.get("explicitlytaggedheading") == "make your battery last" for a in response.answers)
