# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential

from testcase import (
    GlobalQuestionAnsweringAccountPreparer,
)
from asynctestcase import (
    AsyncQuestionAnsweringTest,
    QnaAuthoringAsyncHelper
)
from azure.ai.language.questionanswering.projects.aio import QuestionAnsweringProjectsClient

class CreateAndDeployTests(AsyncQuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_create_project(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        await client.create_project(
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
        async for p in qna_projects:
            if ("projectName" in p) and p["projectName"] == project_name:
                found = True
        assert found


    @GlobalQuestionAnsweringAccountPreparer()
    async def test_deploy_project(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create deployable project
        project_name = "IssacNewton"
        await QnaAuthoringAsyncHelper.create_test_project(
            client,
            project_name=project_name,
            is_deployable=True,
            **self.kwargs_for_polling
        )

        # test deploy
        deployment_name = "production"
        deployment_poller = await client.begin_deploy_project(
            project_name=project_name,
            deployment_name=deployment_name,
            **self.kwargs_for_polling
        )
        await deployment_poller.result()

        # assert
        deployments = client.list_deployments(
            project_name=project_name
        )
        deployment_found = False
        async for d in deployments:
            if ("deploymentName" in d) and d["deploymentName"] == deployment_name:
                deployment_found = True
        assert deployment_found




