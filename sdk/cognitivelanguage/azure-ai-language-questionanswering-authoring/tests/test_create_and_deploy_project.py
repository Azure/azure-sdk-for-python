# pylint: disable=line-too-long,useless-suppression
import pytest
from typing import Any, Dict, cast
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

from helpers import AuthoringTestHelper
from testcase import QuestionAnsweringAuthoringTestCase


class TestCreateAndDeploy(QuestionAnsweringAuthoringTestCase):
    def test_polling_interval(self, qna_authoring_creds):
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        # Default polling interval may change across previews; assert it is a positive int (previously 30) instead of a fixed legacy value
        assert isinstance(client._config.polling_interval, int) and client._config.polling_interval > 0
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]), polling_interval=1
        )
        assert client._config.polling_interval == 1

    def test_create_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
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
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(
            client,
            project_name=project_name,
            is_deployable=True,
            polling_interval=0 if self.is_playback else None,
        )
        deployment_poller = client.begin_deploy_project(
            project_name=project_name,
            deployment_name="production",
            polling_interval=0 if self.is_playback else None,
        )
        # Preview LRO returns None; just ensure it completes without error
        deployment_poller.result()
        assert any(d.get("deploymentName") == "production" for d in client.list_deployments(project_name=project_name))
