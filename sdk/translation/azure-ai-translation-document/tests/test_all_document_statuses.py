# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime
import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient
import pytest

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(DocumentTranslationTest):


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # list docs statuses
        doc_statuses = list(client.list_all_document_statuses(poller.id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        for document in doc_statuses:
            self._validate_doc_status(document, target_language)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_with_pagination(self, client):
        docs_count = 10
        results_per_page = 2
        no_of_pages = docs_count // results_per_page
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses_pages = list(client.list_all_document_statuses(translation_id=poller.id, results_per_page=results_per_page).by_page())
        self.assertEqual(len(doc_statuses_pages), no_of_pages)

        # iterate by page
        for page in doc_statuses_pages:
            page_items = list(page)
            self.assertLessEqual(len(page_items), results_per_page)
            for document in page_items:
                self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_with_skip(self, client):
        docs_count = 10
        skip = 2
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(translation_id=poller.id, skip=skip))
        self.assertEqual(len(doc_statuses), docs_count - skip)

        # iterate over docs
        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_filter_by_status(self, client):
        docs_count = 10
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # list operations
        statuses = ["NotStarted"]
        doc_statuses = list(client.list_all_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == 0)

        statuses = ["Succeeded"]
        doc_statuses = list(client.list_all_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == docs_count)

        statuses = ["Failed"]
        doc_statuses = list(client.list_all_document_statuses(poller.id, statuses=statuses))
        assert(len(doc_statuses) == 0)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_filter_by_ids(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # filter ids
        doc_statuses = list(client.list_all_document_statuses(poller.id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)
        ids = [doc.id for doc in doc_statuses]
        ids = ids[:docs_count//2]

        # do the testing
        doc_statuses = list(client.list_all_document_statuses(poller.id, document_ids=ids))
        self.assertEqual(len(doc_statuses), len(ids))
        for document in doc_statuses:
            self._validate_doc_status(document, target_language, ids=ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_order_by_creation_time_asc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(poller.id, order_by=["createdDateTimeUtc asc"])) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        curr = datetime.min
        for document in doc_statuses:
            assert(document.created_on.replace(tzinfo=None) >= curr.replace(tzinfo=None))
            curr = document.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_order_by_creation_time_desc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(poller.id, order_by=["createdDateTimeUtc desc"])) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        curr = datetime.max
        for document in doc_statuses:
            assert(document.created_on.replace(tzinfo=None) <= curr.replace(tzinfo=None))
            curr = document.created_on


    @pytest.mark.skip(reason="not working! - list returned is empty")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_document_statuses_mixed_filters(self, client):
        docs_count = 25
        target_language = "es"
        skip = 3
        results_per_page = 2
        statuses = ["Succeeded"]

        # submit and validate operation
        poller = self._begin_and_validate_translation_with_multiple_docs(client, docs_count, language_code=target_language, wait=True)

        # get ids
        doc_statuses = list(client.list_all_document_statuses(poller.id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)
        ids = [doc.id for doc in doc_statuses]
        ids = ids[:docs_count//2]

        filtered_docs = client.list_all_document_statuses(
            poller.id,
            # filters
            document_ids=ids,
            statuses=statuses,
            # ordering
            order_by=["createdDateTimeUtc asc"],
            # paging
            skip=skip,
            results_per_page=results_per_page
        ).by_page()
        self.assertIsNotNone(filtered_docs)

        # check statuses
        counter = 0
        curr_time = datetime.min
        for page in filtered_docs:
            page_docs = list(page)
            self.assertLessEqual(len(page_docs), results_per_page) # assert paging
            for doc in page_docs:
                counter += 1
                # assert ordering
                assert(doc.created_on.replace(tzinfo=None) >= curr_time.replace(tzinfo=None))
                curr_time = doc.created_on
                # assert filters
                self.assertIn(doc.status, statuses)
                self.assertIn(doc.id, ids)

        assert(counter == len(ids) - skip)
