import asyncio
import pytest

from helpers import AuthoringAsyncTestHelper
from testcase import QuestionAnsweringAuthoringTestCase

from azure.ai.language.questionanswering.authoring import models as _models
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient


class TestExportAndImportAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_export_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        polling_interval = self.kwargs_for_polling.get("polling_interval")
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, polling_interval=polling_interval
            )
            poller = await client.begin_export(
                project_name=project_name, file_format="json", polling_interval=polling_interval
            )
            await poller.result()  # LROPoller[None]; ensure completion
            assert poller.done()

    @pytest.mark.asyncio
    async def test_import_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        polling_interval = self.kwargs_for_polling.get("polling_interval")
        async with client:
            # For import, ensure project exists; do NOT delete it beforehand to avoid 404.
            await AuthoringAsyncTestHelper.create_test_project(
                client,
                project_name=project_name,
                get_export_url=False,
                delete_old_project=False,
                polling_interval=polling_interval,
            )
            # Wait for project to be observable (eventual consistency) before import.
            project_visible = False
            for _ in range(5):
                async for proj in client.list_projects():
                    if proj.get("projectName") == project_name:
                        project_visible = True
                        break
                if project_visible:
                    break
                await asyncio.sleep(1)
            assert project_visible, "Project not visible after creation"

            # Construct minimal valid ImportJobOptions (metadata fields are read-only server side;
            # import focuses on assets. Provide an empty Assets object to exercise path.)
            import_body = _models.ImportJobOptions(
                assets=_models.Assets(
                    qnas=[
                        _models.ImportQnaRecord(
                            id=1,
                            answer="Gravity is a force of attraction.",
                            source="https://wikipedia.org/wiki/Isaac_Newton",
                            questions=["What is gravity?"],
                        )
                    ]
                )
            )
            poller = await client.begin_import_assets(
                project_name=project_name, body=import_body, file_format="json", polling_interval=polling_interval
            )
            await poller.result()  # LROPoller[None]; ensure completion
            assert poller.done()
            found = False
            async for p in client.list_projects():
                if p.get("projectName") == project_name:
                    found = True
            assert found
