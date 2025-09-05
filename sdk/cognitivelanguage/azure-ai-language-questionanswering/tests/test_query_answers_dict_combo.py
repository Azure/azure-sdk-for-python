# coding=utf-8
# Test for combined dict normalization: qna_id / short_answer_options / answer_context / filters.
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

from testcase import QuestionAnsweringTestCase


class TestQueryAnswersDictCombo(QuestionAnsweringTestCase):
    def test_answers_dict_combo(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        # Use qna_id path (no question) plus all normalization features
        payload = {
            "qna_id": 1,
            "short_answer_options": {"confidence_threshold": 0.1, "top": 3},
            "answer_context": {"previous_user_query": "test previous"},
            "filters": {
                "metadata_filter": {
                    "logical_operation": "and",
                    "metadata": [("k1", "v1"), ("k2", "v2")],
                }
            },
            "top": 5,
        }
        with client:
            result = client.get_answers(payload, project_name=qna_creds["project"], deployment_name=qna_creds["deployment"])  # type: ignore[arg-type]
            # We cannot assert concrete answer content in live/recorded test deterministically.
            # Focus on normalization side-effects existing in wire result (validated indirectly by presence of answers / no error).
            assert result.answers is not None
            # If span enabled, at least one answer should have short_answer
            assert any(a.short_answer for a in result.answers if getattr(a, 'short_answer', None))

    def test_answers_dict_requires_question_or_qna(self, recorded_test, qna_creds):
        client = QuestionAnsweringClient(qna_creds["qna_endpoint"], AzureKeyCredential(qna_creds["qna_key"]))
        bad = {"top": 1}
        with client:
            with pytest.raises(TypeError):
                client.get_answers(bad, project_name=qna_creds["project"], deployment_name=qna_creds["deployment"])  # type: ignore[arg-type]
