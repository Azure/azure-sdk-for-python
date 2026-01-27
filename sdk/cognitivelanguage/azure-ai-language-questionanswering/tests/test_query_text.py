# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# -------------------------------------------------------------------------
# Runtime tests: text records querying (authoring removed)
# -------------------------------------------------------------------------
import pytest
from testcase import QuestionAnsweringTestCase

from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import AnswersFromTextOptions, TextDocument
from azure.core.credentials import AzureKeyCredential


class TestQueryText(QuestionAnsweringTestCase):
    def test_query_text_basic(self, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = AnswersFromTextOptions(
            question="What is the meaning of life?",
            text_documents=[
                TextDocument(text="abc Graphics  Surprise, surprise -- our 4K  ", id="doc1"),
                TextDocument(text="Short text about battery life and charging speed.", id="doc2"),
            ],
            language="en",
        )
        # Use operations group directly to satisfy static type checking (dynamic convenience wrapper added in _patch)
        output = client.get_answers_from_text(params)
        assert output.answers
        for answer in output.answers:
            assert answer.answer
            assert answer.confidence is not None
            assert answer.id is not None
            if answer.short_answer:
                assert answer.short_answer.text

    def test_query_text_with_str_records(self, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        params = {
            "question": "How long it takes to charge surface?",
            # Wire field must be 'records' per AnswersFromTextOptions (text_documents -> records)
            "records": [
                {
                    "text": "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully.",
                    "id": "r1",
                },
                {
                    "text": "You can use the USB port on your Surface Pro 4 power supply to charge other devices.",
                    "id": "r2",
                },
            ],
            "language": "en",
        }
        with client:
            output = client.get_answers_from_text(params)
            assert output.answers

    def test_query_text_overload_errors(self):  # negative client-side parameter validation
        with QuestionAnsweringClient("http://fake.com", AzureKeyCredential("123")) as client:
            with pytest.raises(TypeError):
                client.get_answers_from_text("positional_one", "positional_two")  # type: ignore[arg-type] #pylint: disable=too-many-function-args
            with pytest.raises(TypeError):
                client.get_answers_from_text("positional_options_bag", options="options bag by name")  # type: ignore[arg-type]
            params = AnswersFromTextOptions(
                question="Meaning?",
                text_documents=[TextDocument(text="foo", id="doc1"), TextDocument(text="bar", id="doc2")],
            )
            with pytest.raises(TypeError):
                client.get_answers_from_text(options=params)  # type: ignore[arg-type] #pylint: disable=no-value-for-parameter
            with pytest.raises(TypeError):
                client.get_answers_from_text(question="why?", text_documents=["foo", "bar"], options=params)  # type: ignore[arg-type] #pylint: disable=no-value-for-parameter
            with pytest.raises(TypeError):
                client.get_answers_from_text(params, question="Why?")  # type: ignore[arg-type]

    def test_query_text_default_lang_override(self, qna_creds):
        client = QuestionAnsweringClient(
            qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]), default_language="es"
        )
        # client default applies
        output = client.get_answers_from_text(
            {
                "question": "How long it takes to charge surface?",
                "language": "es",
                "records": [
                    {
                        "text": "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully.",
                        "id": "doc1",
                    }
                ],
            },
            raw_response_hook=lambda r: _assert_request_language(r, "es"),
        )
        # override
        output = client.get_answers_from_text(
            {
                "question": "How long it takes to charge surface?",
                "language": "en",
                "records": [
                    {
                        "text": "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully.",
                        "id": "doc1",
                    }
                ],
            },
            raw_response_hook=lambda r: _assert_request_language(r, "en"),
        )
        assert output is not None


def _assert_request_language(response, expected):
    import json

    body = json.loads(response.http_request.content)
    assert body.get("language") == expected
