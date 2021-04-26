# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from datetime import datetime, date
import functools
from testcase import Document
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
import pytest
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_pagination(self, client):
        docs_count = 10
        result_per_page = 2
        no_of_pages = docs_count // result_per_page
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses_pages = list(client.list_all_document_statuses(job_id=job_id, results_per_page=result_per_page))
        self.assertEqual(len(doc_statuses_pages), no_of_pages)

        # iterate by page
        for page in doc_statuses_pages:
            page_items = list(page)
            self.assertEqual(len(page_items), result_per_page)
            for document in page:
                self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_skip(self, client):
        docs_count = 10
        skip = 2
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id=job_id, skip=skip))
        self.assertEqual(len(doc_statuses), docs_count - skip)

        # iterate over docs
        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_status(self, client):
        docs_count = 10
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # list jobs
        statuses = ["Running"]
        doc_statuses = list(client.list_all_document_statuses(job_id, statuses=statuses))
        self.assertIsNotNone(doc_statuses)

        # check statuses
        for document in doc_statuses:
            self._validate_doc_status(document, target_language, status=statuses)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_ids(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # filter ids
        doc_statuses = list(client.list_all_document_statuses(job_id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)
        ids = [doc.id for doc in doc_statuses]
        ids = ids[:docs_count//2]

        # do the testing
        doc_statuses = list(client.list_all_document_statuses(job_id, ids=ids))
        self.assertEqual(len(doc_statuses), len(ids))
        for document in doc_statuses:
            self._validate_doc_status(document, target_language, ids=ids)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_start(self, client):
        # it's not practical to test for created time filter
        pass


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_filter_by_created_end(self, client):
        # it's not practical to test for created time filter
        pass


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_asc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id), order_by=["CreatedDateTimeUtc", "asc"]) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        curr = date.min
        for document in doc_statuses:
            self.assert(document.created_on > curr)
            curr = document.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_order_by_creation_time_desc(self, client):
        docs_count = 5
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id), order_by=["CreatedDateTimeUtc", "asc"]) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)

        curr = date.max
        for document in doc_statuses:
            self.assert(document.created_on < curr)
            curr = document.created_on


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_submitted_jobs_mixed_filters(self, client):
        docs_count = 15
        target_language = "es"

        # submit and validate job
        job_id = self._create_translation_job_with_dummy_docs(client, docs_count, language_code=target_language, wait=False)

        # get ids
        doc_statuses = list(client.list_all_document_statuses(job_id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), docs_count)
        ids = [doc.id for doc in doc_statuses]
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
        filtered_docs = list(filtered_docs)
        self.assertIsNotNone(filtered_docs)

        # check statuses
        curr_time = date.max
        for page in filtered_docs:
            page_docs = list(page)
            self.assertEqual(len(page_docs), results_per_page) # assert paging
            for doc in page:
                # assert ordering
                self.assert(doc.created_on < curr_time)
                curr_time = doc.created_on
                # assert filters
                self.assertIn(doc.status, statuses)
                self.assertIn(doc.id, ids)


