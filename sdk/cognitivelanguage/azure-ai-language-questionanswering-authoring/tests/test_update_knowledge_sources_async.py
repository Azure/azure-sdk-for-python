import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient

from .helpers import AuthoringAsyncTestHelper
from .testcase import QuestionAnsweringAuthoringTestCase


class TestSourcesQnasSynonymsAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_add_source(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, **self.kwargs_for_polling
            )
            poller = await client.begin_update_sources(
                project_name=project_name,
                sources=[
                    {
                        "op": "add",
                        "value": {
                            "displayName": "MicrosoftFAQ",
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
            await poller.result()
            found = False
            async for s in client.list_sources(project_name=project_name):
                if s.get("displayName") == "MicrosoftFAQ":
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_add_qna(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, **self.kwargs_for_polling
            )
            question = "What is the easiest way to use azure services in my .NET project?"
            answer = "Using Microsoft's Azure SDKs"
            poller = await client.begin_update_qnas(
                project_name=project_name,
                qnas=[{"op": "add", "value": {"questions": [question], "answer": answer}}],
                **self.kwargs_for_polling,
            )
            await poller.result()
            found = False
            async for qna in client.list_qnas(project_name=project_name):
                if qna.get("answer") == answer and question in qna.get("questions", []):
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_add_synonym(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, **self.kwargs_for_polling
            )
            await client.update_synonyms(
                project_name=project_name,
                synonyms={"value": [{"alterations": ["qnamaker", "qna maker"]}]},
            )
            found = False
            async for s in client.list_synonyms(project_name=project_name):
                if "qnamaker" in s.get("alterations", []) and "qna maker" in s.get("alterations", []):
                    found = True
            assert found
