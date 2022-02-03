# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    QuestionAnsweringTest,
    GlobalQuestionAnsweringAccountPreparer,
    QnaAuthoringHelper
)

from azure.ai.language.questionanswering.projects import QuestionAnsweringProjectsClient

class CreateAndDeployTests(QuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    def test_create_project(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # list projects
        qna_projects = client.list_projects()
        found = False
        for p in qna_projects:
            if ("projectName" in p) and p["projectName"] == project_name:
                found = True
        assert found


    @GlobalQuestionAnsweringAccountPreparer()
    def test_deploy_project(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create deployable project
        project_name = "IssacNewton"
        QnaAuthoringHelper.create_test_project(client, project_name=project_name, is_deployable=True)

        # test deploy
        deployment_name = "production"
        deployment_poller = client.begin_deploy_project(
            project_name=project_name,
            deployment_name=deployment_name
        )
        deployment_poller.result()

        # assert
        deployments = client.list_deployments(
            project_name=project_name
        )
        deployment_found = False
        for d in deployments:
            if ("deploymentName" in d) and d["deploymentName"] == deployment_name:
                deployment_found = True
        assert deployment_found
            



