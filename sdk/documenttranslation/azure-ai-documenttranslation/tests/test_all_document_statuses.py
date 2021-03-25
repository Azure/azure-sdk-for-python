# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestAllDocumentStatuses(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses(self, client):
        # prepare containers and test data
        blob_data = [b'This is some text']
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
        doc_statuses = client.list_all_document_statuses(job_id)
        self.assertEqual(len(doc_statuses), len(blob_data))

        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_pagination(self, client):
        # prepare containers and test data
        blob_data = [b'text 1', b'text 2', b'text 3', b'text 4', b'text 5', b'text 6']
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
        doc_statuses_pages = client.list_all_document_statuses(job_id=job_id, results_per_page=result_per_page)
        self.assertEqual(len(doc_statuses_pages), no_of_pages)

        # iterate by page
        for page in doc_statuses_pages:
            self.assertEqual(len(page), result_per_page)
            for document in page:
                self._validate_doc_status(document, target_language)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses_with_skip(self, client):
        # prepare containers and test data
        blob_data = [b'text 1', b'text 2', b'text 3', b'text 4', b'text 5', b'text 6']
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
        doc_statuses = client.list_all_document_statuses(job_id=job_id, skip=skip)
        self.assertEqual(len(doc_statuses), docs_len - skip)

        # iterate over docs
        for document in doc_statuses:
            self._validate_doc_status(document, target_language)


    # helper methods
    def _validate_doc_status(self, document, target_language):
        # specific assertions
        self.assertEqual(document.status, "Succeeded")
        self.assertIsNotNone(document.translate_to, target_language)
        # generic assertions
        self.assertIsNotNone(document.id)
        self.assertIsNotNone(document.translated_document_url)
        self.assertIsNotNone(document.translation_progress)
        self.assertIsNotNone(document.characters_charged)
        self.assertIsNotNone(document.created_on)
        self.assertIsNotNone(document.last_updated_on)


    def _submit_and_validate_translation_job(self, client, translation_inputs, total_docs_count):
        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)
        # wait for result
        job_result = client.wait_until_done(job_detail.id)
        # assertions
        self.assertEqual(job_result.status, "Succeeded")
        # docs count
        self.assertEqual(job_result.documents_total_count, total_docs_count)
        self.assertEqual(job_result.documents_failed_count, 0)
        self.assertEqual(job_result.documents_succeeded_count, total_docs_count)
        self.assertEqual(job_result.documents_in_progress_count, 0)
        self.assertEqual(job_result.documents_not_yet_started_count, 0)
        self.assertEqual(job_result.documents_cancelled_count, 0)
        # generic assertions
        self.assertIsNotNone(job_result.created_on)
        self.assertIsNotNone(job_result.last_updated_on)
        self.assertIsNotNone(job_result.total_characters_charged)

        return job_detail.id