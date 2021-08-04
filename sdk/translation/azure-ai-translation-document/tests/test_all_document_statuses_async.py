# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
import functools
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document.aio import DocumentTranslationClient
import pytest

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(AsyncDocumentTranslationTest):


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(poller.id)
        doc_statuses_list = []

        async for document in doc_statuses:
            doc_statuses_list.append(document)
            self._validate_doc_status(document, target_language)

        self.assertEqual(len(doc_statuses_list), docs_count)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_with_pagination(self, client):
        docs_count = 7
        results_per_page = 2
        no_of_pages = docs_count // results_per_page + 1
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses_pages = client.list_all_document_statuses(translation_id=poller.id, results_per_page=results_per_page).by_page()
        pages_list = []

        # iterate by page
        async for page in doc_statuses_pages:
            pages_list.append(page)
            page_docs_list = []
            async for document in page:
                page_docs_list.append(document)
                self._validate_doc_status(document, target_language)
            self.assertLessEqual(len(page_docs_list), results_per_page)

        self.assertEqual(len(pages_list), no_of_pages)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_with_skip(self, client):
        docs_count = 5
        skip = 2
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(translation_id=poller.id, skip=skip)
        doc_statuses_list = []

        # iterate over docs
        async for document in doc_statuses:
            doc_statuses_list.append(document)
            self._validate_doc_status(document, target_language)

        self.assertEqual(len(doc_statuses_list), docs_count - skip)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_filter_by_status(self, client):
        docs_count = 10
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # list operations
        statuses = ["NotStarted"]
        doc_statuses = client.list_all_document_statuses(poller.id, statuses=statuses)
        counter = 0
        async for doc in doc_statuses:
            counter += 1
        assert(counter == 0)

        statuses = ["Succeeded"]
        doc_statuses = client.list_all_document_statuses(poller.id, statuses=statuses)
        counter = 0
        async for doc in doc_statuses:
            counter += 1
        assert(counter == docs_count)

        statuses = ["Failed"]
        doc_statuses = client.list_all_document_statuses(poller.id, statuses=statuses)
        counter = 0
        async for doc in doc_statuses:
            counter += 1
        assert(counter == 0)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_filter_by_ids(self, client):
        docs_count = 15
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # filter ids
        doc_statuses = client.list_all_document_statuses(poller.id)
        ids = [document.id async for document in doc_statuses]
        self.assertEqual(len(ids), docs_count)
        ids = ids[:docs_count//2]

        # do the testing
        doc_statuses = client.list_all_document_statuses(poller.id, document_ids=ids)
        counter = 0
        async for document in doc_statuses:
            counter += 1
            self._validate_doc_status(document, target_language, ids=ids)

        assert(counter == len(ids))


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_order_by_creation_time_asc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(poller.id, order_by=["created_on asc"])

        curr = datetime.min
        docs = []
        async for document in doc_statuses:
            docs.append(document)
            assert(document.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = document.created_on

        self.assertEqual(len(docs), docs_count)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_order_by_creation_time_desc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(poller.id, order_by=["created_on desc"])

        curr = datetime.max
        docs = []
        async for document in doc_statuses:
            docs.append(document)
            assert(document.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = document.created_on

        self.assertEqual(len(docs), docs_count)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    async def test_list_document_statuses_mixed_filters(self, client):
        docs_count = 25
        target_language = "es"
        results_per_page = 2
        statuses = ["Succeeded"]
        skip = 3

        # submit and validate operation
        poller = await self._begin_and_validate_translation_with_multiple_docs_async(client, docs_count, language_code=target_language, wait=True)

        # get ids
        doc_statuses = client.list_all_document_statuses(poller.id)
        ids = [document.id async for document in doc_statuses]
        self.assertEqual(len(ids), docs_count)
        ids = ids[:docs_count//2]

        filtered_docs = client.list_all_document_statuses(
            poller.id,
            # filters
            document_ids=ids,
            statuses=statuses,
            # ordering
            order_by=["created_on asc"],
            # paging
            skip=skip,
            results_per_page=results_per_page
        ).by_page()

        # check statuses
        counter = 0
        curr_time = datetime.min
        async for page in filtered_docs:
            page_docs = []
            async for doc in page:
                counter += 1
                page_docs.append(doc)
                # assert ordering
                assert(doc.created_on.replace(tzinfo=None) >= curr_time.replace(tzinfo=None))
                curr_time = doc.created_on
                # assert filters
                self.assertIn(doc.status, statuses)
                self.assertIn(doc.id, ids)
                
            self.assertLessEqual(len(page_docs), results_per_page) # assert paging

        assert(counter == len(ids) - skip)

