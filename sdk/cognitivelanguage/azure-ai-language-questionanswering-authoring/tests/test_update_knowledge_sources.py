from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering.authoring import models as _models
from typing import cast

from helpers import AuthoringTestHelper
from testcase import QuestionAnsweringAuthoringTestCase


class TestSourcesQnasSynonyms(QuestionAnsweringAuthoringTestCase):
    def test_add_source(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name)
        source_display_name = "MicrosoftFAQ"
        update_source_ops = [
            _models.UpdateSourceRecord(
                {
                    "op": "add",
                    "value": {
                        "displayName": source_display_name,
                        "source": "https://www.microsoft.com/en-in/software-download/faq",
                        "sourceUri": "https://www.microsoft.com/en-in/software-download/faq",
                        "sourceKind": "url",
                        "contentStructureKind": "unstructured",
                        "refresh": False,
                    },
                }
            )
        ]
        poller = client.begin_update_sources(
            project_name=project_name,
            sources=cast(list[_models.UpdateSourceRecord], update_source_ops),
            content_type="application/json",
            polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type]
        )
        poller.result()
        assert any(s.get("displayName") == source_display_name for s in client.list_sources(project_name=project_name))

    def test_add_qna(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name)
        question = "What is the easiest way to use azure services in my .NET project?"
        answer = "Using Microsoft's Azure SDKs"
        update_qna_ops = [
            _models.UpdateQnaRecord(
                {
                    "op": "add",
                    "value": {
                        "id": 0,  # required by model schema; service will assign real id
                        "answer": answer,
                        "questions": [question],
                    },
                }
            )
        ]
        poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=cast(list[_models.UpdateQnaRecord], update_qna_ops),
            content_type="application/json",
            polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type]
        )
        poller.result()
        assert any(
            (q.get("answer") == answer and question in q.get("questions", []))
            for q in client.list_qnas(project_name=project_name)
        )

    def test_add_synonym(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name)
        synonyms_model = _models.SynonymAssets(
            value=[
                _models.WordAlterations(alterations=["qnamaker", "qna maker"]),
            ]
        )
        client.update_synonyms(
            project_name=project_name,
            synonyms=synonyms_model,
            content_type="application/json",
        )
        assert any(
            ("qnamaker" in s.get("alterations", []) and "qna maker" in s.get("alterations", []))
            for s in client.list_synonyms(project_name=project_name)
        )
