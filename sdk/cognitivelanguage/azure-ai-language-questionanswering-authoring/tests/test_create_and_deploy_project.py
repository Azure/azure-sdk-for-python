import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

from helpers import AuthoringTestHelper
from testcase import QuestionAnsweringAuthoringTestCase


class TestCreateAndDeploy(QuestionAnsweringAuthoringTestCase):
    def test_polling_interval(self, qna_authoring_creds):
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        assert client._config.polling_interval == 5
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]), polling_interval=1
        )
        assert client._config.polling_interval == 1

    def test_create_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        found = any(p.get("projectName") == project_name for p in client.list_projects())
        assert found

    def test_deploy_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(
            client, project_name=project_name, is_deployable=True, **self.kwargs_for_polling
        )
        deployment_poller = client.begin_deploy_project(
            project_name=project_name, deployment_name="production", **self.kwargs_for_polling
        )
        project = deployment_poller.result()
        assert project["deploymentName"] == "production"
        assert any(
            d.get("deploymentName") == "production" for d in client.list_deployments(project_name=project_name)
        )
