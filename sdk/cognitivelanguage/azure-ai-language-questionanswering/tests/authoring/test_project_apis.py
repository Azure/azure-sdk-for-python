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
    GlobalQuestionAnsweringAccountPreparer
)

from azure.ai.language.questionanswering.projects import QuestionAnsweringProjectsClient
from azure.ai.language.questionanswering.projects import models

class QnaAuthoringTests(QuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    def test_create_project(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        client.question_answering_projects.create_project(
            project_name=project_name,
            body={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # list projects
        qna_projects = client.question_answering_projects.list_projects()
        found = False
        for p in qna_projects:
            if p.project_name == project_name:
                found = True
        assert found