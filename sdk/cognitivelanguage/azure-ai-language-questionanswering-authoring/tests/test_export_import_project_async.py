import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient

from helpers import AuthoringAsyncTestHelper
from testcase import QuestionAnsweringAuthoringTestCase


class TestExportAndImportAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_export_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, **self.kwargs_for_polling
            )
            poller = await client.begin_export(
                project_name=project_name, file_format="json", **self.kwargs_for_polling
            )
            result = await poller.result()
            assert result["status"] == "succeeded"
            assert result["resultUrl"]

    @pytest.mark.asyncio
    async def test_import_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client,
                project_name=project_name,
                get_export_url=True,
                delete_old_project=True,
                **self.kwargs_for_polling,
            )
            payload = {
                "Metadata": {
                    "ProjectName": project_name,
                    "Description": "Biography of Sir Isaac Newton",
                    "Language": "en",
                    "MultilingualResource": False,
                    "Settings": {"DefaultAnswer": "no answer"},
                }
            }
            poller = await client.begin_import_assets(
                project_name=project_name, options=payload, **self.kwargs_for_polling
            )
            result = await poller.result()
            assert result["jobId"]
            found = False
            async for p in client.list_projects():
                if p.get("projectName") == project_name:
                    found = True
            assert found
