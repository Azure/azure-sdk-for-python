import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient

from .helpers import AuthoringAsyncTestHelper
from .testcase import QuestionAnsweringAuthoringTestCase


class TestCreateAndDeployAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_create_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await client.create_project(
                project_name=project_name,
                options={
                    "description": "Biography of Sir Isaac Newton",
                    "language": "en",
                    "multilingualResource": True,
                    "settings": {"defaultAnswer": "no answer"},
                },
            )
            found = False
            async for p in client.list_projects():
                if p.get("projectName") == project_name:
                    found = True
            assert found

    @pytest.mark.asyncio
    async def test_deploy_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client, project_name=project_name, is_deployable=True, **self.kwargs_for_polling
            )
            deployment_poller = await client.begin_deploy_project(
                project_name=project_name, deployment_name="production", **self.kwargs_for_polling
            )
            result = await deployment_poller.result()
            assert result["deploymentName"] == "production"
            deployments = client.list_deployments(project_name=project_name)
            found = False
            async for d in deployments:
                if d.get("deploymentName") == "production":
                    found = True
            assert found
