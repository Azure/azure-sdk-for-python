import pytest
from helpers import AuthoringAsyncTestHelper
from testcase import QuestionAnsweringAuthoringTestCase

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient



class TestCreateAndDeployAsync(QuestionAnsweringAuthoringTestCase):
    @pytest.mark.asyncio
    async def test_create_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await client.create_project( # pylint: disable=no-value-for-parameter
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
    async def test_deploy_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        async with client:
            await AuthoringAsyncTestHelper.create_test_project(
                client,
                project_name=project_name,
                is_deployable=True,
                polling_interval=0 if self.is_playback else None, # pylint: disable=using-constant-test
            )
            deployment_poller = await client.begin_deploy_project(
                project_name=project_name,
                deployment_name="production",
                polling_interval=0 if self.is_playback else None,  # pylint: disable=using-constant-test
            )
            # Preview LRO returns None; just await completion
            await deployment_poller.result()
            deployments = client.list_deployments(project_name=project_name)
            found = False
            async for d in deployments:
                if d.get("deploymentName") == "production":
                    found = True
            assert found
