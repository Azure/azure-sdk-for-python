from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

from .helpers import AuthoringTestHelper
from .testcase import QuestionAnsweringAuthoringTestCase


class TestSourcesQnasSynonyms(QuestionAnsweringAuthoringTestCase):
    def test_add_source(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)
        source_display_name = "MicrosoftFAQ"
        poller = client.begin_update_sources(
            project_name=project_name,
            sources=[
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
            ],
            **self.kwargs_for_polling,
        )
        poller.result()
        assert any(
            s.get("displayName") == source_display_name for s in client.list_sources(project_name=project_name)
        )

    def test_add_qna(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)
        question = "What is the easiest way to use azure services in my .NET project?"
        answer = "Using Microsoft's Azure SDKs"
        poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=[
                {
                    "op": "add",
                    "value": {"questions": [question], "answer": answer},
                }
            ],
            **self.kwargs_for_polling,
        )
        poller.result()
        assert any(
            (q.get("answer") == answer and question in q.get("questions", []))
            for q in client.list_qnas(project_name=project_name)
        )

    def test_add_synonym(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)
        client.update_synonyms(
            project_name=project_name,
            synonyms={"value": [{"alterations": ["qnamaker", "qna maker"]}]},
        )
        assert any(
            ("qnamaker" in s.get("alterations", []) and "qna maker" in s.get("alterations", []))
            for s in client.list_synonyms(project_name=project_name)
        )
