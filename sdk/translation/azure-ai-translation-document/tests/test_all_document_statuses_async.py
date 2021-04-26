# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime, date
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


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_status(self, client):
        docs_count = 10
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # list jobs
        statuses = ["Running"]
        doc_statuses = client.list_all_document_statuses(job_id, statuses=statuses)

        # check statuses
        async for document in doc_statuses:
            self._validate_doc_status(document, target_language, status=statuses)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_ids(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # filter ids
        doc_statuses = client.list_all_document_statuses(job_id)
        ids = await [document.id async for document in doc_statuses]
        self.assertEqual(len(ids), docs_count)
        ids = ids[:docs_count//2]

        # do the testing
        doc_statuses = client.list_all_document_statuses(job_id, ids=ids)
        async for document in doc_statuses:
            self._validate_doc_status(document, target_language, ids=ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_start(self, client):
        # it's not practical to test for created time filter
        pass


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_filter_by_created_end(self, client):
        # it's not practical to test for created time filter
        pass


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id, order_by=["CreatedDateTimeUtc", "asc"])

        curr = date.min
        docs = []
        async for document in doc_statuses:
            docs.append(document)
            self.assert(document.created_on > curr)
            curr = document.created_on

        self.assertEqual(len(docs), docs_count)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id, order_by=["CreatedDateTimeUtc", "desc"])

        curr = date.max
        docs = []
        for document in doc_statuses:
            docs.append(document)
            self.assert(document.created_on < curr)
            curr = document.created_on

        self.assertEqual(len(docs), docs_count)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_submitted_jobs_mixed_filters(self, client):
        docs_count = 15
        target_language = "es"

        # submit and validate job
        job_id = await self._create_translation_job_with_dummy_docs_async(client, docs_count, language_code=target_language, wait=False)

        # get ids
        doc_statuses = client.list_all_document_statuses(job_id)
        ids = await [document.id async for document in doc_statuses]
        self.assertEqual(len(ids), docs_count)
        ids = ids[:docs_count//2]

        # create some jobs
        results_per_page = 2
        statuses = ["Running"]

        # list jobs
        filtered_docs = client.list_all_document_statuses(
            job_id,
            # filters
            ids=ids,
            statuses=statuses,
            # ordering
            order_by=["CreatedDateTimeUtc", "asc"],
            # paging
            skip=1,
            results_per_page=results_per_page
        )

        # check statuses
        curr_time = date.max
        for page in filtered_docs:
            page_docs = []
            for doc in page:
                page_docs.append(doc)
                # assert ordering
                self.assert(doc.created_on < curr_time)
                curr_time = doc.created_on
                # assert filters
                self.assertIn(doc.status, statuses)
                self.assertIn(doc.id, ids)
                
            self.assertEqual(len(page_docs), results_per_page) # assert paging



