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


class TestDocumentStatus(DocumentTranslationTest):

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

        # submit and validate translation job
        job_id = self._submit_and_validate_translation_job(self, client, translation_inputs, len(blob_data))

        # get doc statuses
        doc_statuses = client.list_all_document_statuses(job_id)
        self.assertIsNotNone(doc_statuses)

        # get first doc
        test_doc = next(doc_statuses)
        self.assertIsNotNone(test_doc.id)

        # get doc details
        doc_status = client.get_document_status(job_id=job_id, document_id=test_doc.id)
        self._validate_doc_status(doc_status, target_language)


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