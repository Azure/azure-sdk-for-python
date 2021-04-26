# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import Document
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget
from azure.ai.translation.document.aio import DocumentTranslationClient
import pytest
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(AsyncDocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_statuses(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id)
        doc_statuses_list = []

        async for document in doc_statuses:
            doc_statuses_list.append(document)
            self._validate_doc_status(document, target_language)

        self.assertEqual(len(doc_statuses_list), docs_count)



    @pytest.mark.skip("top not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_statuses_with_pagination(self, client):
        docs_count = 5
        result_per_page = 2
        no_of_pages = docs_count // result_per_page
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses_pages = client.list_all_document_statuses(job_id=job_id, results_per_page=result_per_page)
        pages_list = []

        # iterate by page
        async for page in doc_statuses_pages:
            pages_list.append(page)
            page_docs_list = []
            async for document in page:
                page_docs_list.append(document)
                self._validate_doc_status(document, target_language)
            self.assertEqual(len(page_docs_list), result_per_page)

        self.assertEqual(len(pages_list), no_of_pages)



    @pytest.mark.skip("skip not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_statuses_with_skip(self, client):
        docs_count = 5
        skip = 2
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id=job_id, skip=skip)
        doc_statuses_list = []

        # iterate over docs
        async for document in doc_statuses:
            doc_statuses_list.append(document)
            self._validate_doc_status(document, target_language)

        self.assertEqual(len(doc_statuses_list), docs_count - skip)
