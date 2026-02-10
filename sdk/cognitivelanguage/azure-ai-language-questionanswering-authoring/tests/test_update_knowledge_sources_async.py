from typing import cast
import pytest
from helpers import AuthoringAsyncTestHelper
from testcase import QuestionAnsweringAuthoringTestCase

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering.authoring import models as _models



class TestSourcesQnasSynonymsAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_add_source(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined] # pylint: disable=unused-argument
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, polling_interval=0 if self.is_playback else None # pylint: disable=using-constant-test
            )
            source_display_name = "SurfaceBookUserGuide"
            update_source_ops = [
                _models.UpdateSourceRecord(
                    {
                        "op": "add",
                        "value": {
                            "displayName": source_display_name,
                            "source": "https://download.microsoft.com/download/7/B/1/7B10C82E-F520-4080-8516-5CF0D803EEE0/surface-book-user-guide-EN.pdf",
                            "sourceUri": "https://download.microsoft.com/download/7/B/1/7B10C82E-F520-4080-8516-5CF0D803EEE0/surface-book-user-guide-EN.pdf",
                            "sourceKind": "url",
                            "contentStructureKind": "unstructured",
                            "refresh": False,
                        },
                    }
                )
            ]
            poller = await client.begin_update_sources( # pylint: disable=no-value-for-parameter
                project_name=project_name,
                sources=cast(list[_models.UpdateSourceRecord], update_source_ops),
                content_type="application/json",
                polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type] # pylint: disable=using-constant-test
            )
            await poller.result()
            found = False
            async for s in client.list_sources(project_name=project_name):
                if s.get("displayName") == source_display_name:
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_add_qna(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined] # pylint: disable=unused-argument
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, polling_interval=0 if self.is_playback else None # pylint: disable=using-constant-test
            )
            question = "What is the easiest way to use azure services in my .NET project?"
            answer = "Using Microsoft's Azure SDKs"
            update_qna_ops = [
                _models.UpdateQnaRecord(
                    {
                        "op": "add",
                        "value": {
                            "id": 0,
                            "answer": answer,
                            "questions": [question],
                        },
                    }
                )
            ]
            poller = await client.begin_update_qnas( # pylint: disable=no-value-for-parameter
                project_name=project_name,
                qnas=cast(list[_models.UpdateQnaRecord], update_qna_ops),
                content_type="application/json",
                polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type] # pylint: disable=using-constant-test
            )
            await poller.result()
            found = False
            async for qna in client.list_qnas(project_name=project_name):
                if qna.get("answer") == answer and question in qna.get("questions", []):
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_add_synonym(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined] # pylint: disable=unused-argument
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, polling_interval=0 if self.is_playback else None # pylint: disable=using-constant-test
            )
            synonyms_model = _models.SynonymAssets(
                value=[
                    _models.WordAlterations(alterations=["qnamaker", "qna maker"]),
                ]
            )
            await client.update_synonyms( # pylint: disable=no-value-for-parameter
                project_name=project_name,
                synonyms=synonyms_model,
                content_type="application/json",
            )
            found = False
            async for s in client.list_synonyms(project_name=project_name):
                if "qnamaker" in s.get("alterations", []) and "qna maker" in s.get("alterations", []):
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_add_qna_with_explicitlytaggedheading(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined] # pylint: disable=unused-argument
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, polling_interval=0 if self.is_playback else None # pylint: disable=using-constant-test
            )
            update_qna_ops = [
                _models.UpdateQnaRecord(
                    {
                        "op": "add",
                        "value": {
                            "id": 0,
                            "answer": "Check the battery level in Settings.",
                            "questions": ["How do I check the battery level?"],
                            "metadata": {"explicitlytaggedheading": "check the battery level"},
                        },
                    }
                )
            ]
            poller = await client.begin_update_qnas( # pylint: disable=no-value-for-parameter
                project_name=project_name,
                qnas=cast(list[_models.UpdateQnaRecord], update_qna_ops),
                content_type="application/json",
                polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type] # pylint: disable=using-constant-test
            )
            await poller.result()
            deploy_poller = await client.begin_deploy_project(
                project_name=project_name,
                deployment_name="production",
                polling_interval=0 if self.is_playback else None,  # type: ignore[arg-type] # pylint: disable=using-constant-test
            )
            await deploy_poller.result()
            found = False
            async for qna in client.list_qnas(project_name=project_name):
                if (qna.get("metadata") or {}).get("explicitlytaggedheading") == "check the battery level":
                    found = True
            assert found
