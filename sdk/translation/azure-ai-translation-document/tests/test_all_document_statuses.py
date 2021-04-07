# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

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
        # prepare containers and test data
        blob_data = [Document(data=b'This is some text')]
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        target_language = "es"

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code=target_language
                    )
                ]
            )
        ]

        # submit and validate job
        job_id = self._submit_and_validate_translation_job(client, translation_inputs, len(blob_data))

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id)) # convert from generic iterator to list
        self.assertEqual(len(doc_statuses), len(blob_data))

        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    @pytest.mark.skip("top not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_pagination(self, client):
        # prepare containers and test data
        blob_text = b'blob text'
        blob_data = [Document(data=blob_text), Document(data=blob_text), Document(data=blob_text),
                     Document(data=blob_text), Document(data=blob_text), Document(data=blob_text)]
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        result_per_page = 2
        no_of_pages = len(blob_data) // result_per_page
        target_language = "es"

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code=target_language
                    )
                ]
            )
        ]

        # submit and validate job
        job_id = self._submit_and_validate_translation_job(client, translation_inputs, len(blob_data))

        # check doc statuses
        doc_statuses_pages = list(client.list_all_document_statuses(job_id=job_id, results_per_page=result_per_page))
        self.assertEqual(len(doc_statuses_pages), no_of_pages)

        # iterate by page
        for page in doc_statuses_pages:
            page_items = list(page)
            self.assertEqual(len(page_items), result_per_page)
            for document in page:
                self._validate_doc_status(document, target_language)


    @pytest.mark.skip("skip not exposed yet")
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_skip(self, client):
        # prepare containers and test data
        blob_text = b'blob text'
        blob_data = [Document(data=blob_text), Document(data=blob_text), Document(data=blob_text),
                     Document(data=blob_text), Document(data=blob_text), Document(data=blob_text)]
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        docs_len = len(blob_data)
        skip = 2
        target_language = "es"

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code=target_language
                    )
                ]
            )
        ]

        # submit and validate job
        job_id = self._submit_and_validate_translation_job(client, translation_inputs, len(blob_data))

        # check doc statuses
        doc_statuses = list(client.list_all_document_statuses(job_id=job_id, skip=skip))
        self.assertEqual(len(doc_statuses), docs_len - skip)

        # iterate over docs
        for document in doc_statuses:
            self._validate_doc_status(document, target_language)