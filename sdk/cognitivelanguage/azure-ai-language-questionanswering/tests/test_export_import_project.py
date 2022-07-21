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

from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

class ExportAndImportTests(QuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    def test_export_project(self, qna_account, qna_key):
        client = QuestionAnsweringAuthoringClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        QnaAuthoringHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)

        # export project
        export_poller = client.begin_export(
            project_name=project_name,
            format="json",
            **self.kwargs_for_polling
        )
        result = export_poller.result()
        assert result["status"] == "succeeded"
        assert result["resultUrl"] is not None


    @GlobalQuestionAnsweringAccountPreparer()
    def test_import_project(self, qna_account, qna_key):
        client = QuestionAnsweringAuthoringClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        export_url = QnaAuthoringHelper.create_test_project(
            client,
            project_name=project_name,
            get_export_url=True,
            delete_old_project=True,
            **self.kwargs_for_polling
        )

        # import project
        project = {
            "Metadata": {
                "ProjectName": project_name,
                "Description": "biography of Sir Issac Newton",
                "Language": "en",
                "MultilingualResource": False,
                "Settings": {
                    "DefaultAnswer": "no answer"
                }
            }
        }
        import_poller = client.begin_import_assets(
            project_name=project_name,
            options=project,
            **self.kwargs_for_polling
        )
        import_poller.result()

        # assert
        project_found = False
        projects = client.list_projects()
        for p in projects:
            if ("projectName" in p) and p["projectName"] == project_name:
                project_found = True
        assert project_found
