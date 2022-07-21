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

from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient

class SourcesQnasSynonymsTests(AsyncQuestionAnsweringTest):

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_add_source(self, qna_account, qna_key):
        client = QuestionAnsweringAuthoringClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        await QnaAuthoringAsyncHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)

        # add sources
        source_display_name = "MicrosoftFAQ"
        sources_poller = await client.begin_update_sources(
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
            }],
            **self.kwargs_for_polling
        )
        await sources_poller.result() # wait until done

        # assert
        sources = client.list_sources(
            project_name=project_name
        )
        source_added = False
        async for s in sources:
            if ("displayName" in s) and s["displayName"] == source_display_name:
                source_added = True
        assert source_added

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_add_qna(self, qna_account, qna_key):
        client = QuestionAnsweringAuthoringClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        await QnaAuthoringAsyncHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)

        # add qnas
        question = "What is the easiest way to use azure services in my .NET project?"
        answer = "Using Microsoft's Azure SDKs"
        qna_poller = await client.begin_update_qnas(
            project_name=project_name,
            qnas=[{
                "op": "add",
                "value": {
                    "questions": [
                        question
                    ],
                    "answer": answer
                }
            }],
            **self.kwargs_for_polling
        )
        await qna_poller.result()

        # assert
        qnas = client.list_qnas(
            project_name=project_name
        )
        qna_added = False
        async for qna in qnas:
            if ("answer" in qna and "questions" in qna) and (qna["answer"] == answer and question in qna["questions"]):
                qna_added = True
        assert qna_added

    @GlobalQuestionAnsweringAccountPreparer()
    async def test_add_synonym(self, qna_account, qna_key):
        client = QuestionAnsweringAuthoringClient(qna_account, AzureKeyCredential(qna_key))

        # create project
        project_name = "IssacNewton"
        await QnaAuthoringAsyncHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)

        # add synonyms
        await client.update_synonyms(
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
        async for s in synonyms:
            if ("alterations" in s) and ("qnamaker" in s["alterations"] and "qna maker" in s["alterations"]):
                synonym_added = True
        assert synonym_added
