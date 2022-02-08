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

class SourcesQnasSynonymsTests(QuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    def test_add_source(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        QnaAuthoringHelper.create_test_project(client, project_name=project_name)

        # add sources
        source_display_name = "MicrosoftFAQ"
        sources_poller = client.begin_update_sources(
            project_name=project_name,
            sources=[{
                "op": "add",
                "value": {
                    "displayName": source_display_name,
                    "source": "https://www.microsoft.com/en-in/software-download/faq",
                    "sourceUri": "https://www.microsoft.com/en-in/software-download/faq",
                    "sourceKind": "url",
                    "contentStructureKind": "unstructured",
                    "refresh": False
                }
            }]
        )
        sources_poller.result() # wait until done

        # assert
        sources = client.list_sources(
            project_name=project_name
        )
        source_added = False
        for s in sources:
            if ("displayName" in s) and s["displayName"] == source_display_name:
                source_added = True
        assert source_added

    @GlobalQuestionAnsweringAccountPreparer()
    def test_add_qna(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        QnaAuthoringHelper.create_test_project(client, project_name=project_name)

        # add qnas
        question = "What is the easiest way to use azure services in my .NET project?"
        answer = "Using Microsoft's Azure SDKs"
        qna_poller = client.begin_update_qnas(
            project_name=project_name,
            qnas=[{
                "op": "add",
                "value": {
                    "questions": [
                        question
                    ],
                    "answer": answer
                }
            }]
        )
        qna_poller.result()

        # assert
        qnas = client.list_qnas(
            project_name=project_name
        )
        qna_added = False
        for qna in qnas:
            if ("answer" in qna and "questions" in qna) and (qna["answer"] == answer and question in qna["questions"]):
                qna_added = True
        assert qna_added

    @GlobalQuestionAnsweringAccountPreparer()
    def test_add_synonym(self, qna_account, qna_key):
        client = QuestionAnsweringProjectsClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        QnaAuthoringHelper.create_test_project(client, project_name=project_name)

        # add synonyms
        client.update_synonyms(
            project_name=project_name,
            synonyms={
                "value": [
                    {
                        "alterations": [
                            "qnamaker",
                            "qna maker"
                        ]
                    }
                ]
            }
        )

        # assert
        synonym_added = False
        synonyms = client.list_synonyms(
            project_name=project_name
        )
        for s in synonyms:
            if ("alterations" in s) and ("qnamaker" in s["alterations"] and "qna maker" in s["alterations"]):
                synonym_added = True
        assert synonym_added
