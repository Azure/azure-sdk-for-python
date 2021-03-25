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


class TestListStatus(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_statuses(self, client):
        # prepare containers
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # wait for result
        job_result = client.wait_until_done(job_detail.id)

        # assert
        self.assertEqual(job_result.status, "Succeeded")  # job succeeded
        self.assertIsNotNone(job_result.created_on)
        self.assertIsNotNone(job_result.last_updated_on)
        self.assertIsNotNone(job_result.documents_total_count)
        self.assertIsNotNone(job_result.documents_failed_count)
        self.assertIsNotNone(job_result.documents_succeeded_count)
        self.assertIsNotNone(job_result.documents_in_progress_count)
        self.assertIsNotNone(job_result.documents_not_yet_started_count)
        self.assertIsNotNone(job_result.documents_cancelled_count)
        self.assertIsNotNone(job_result.total_characters_charged)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_detail.id)
        self.assertEqual(len(doc_statuses), 1)
        for document in doc_statuses:
            self.assertIsNotNone(document.translated_document_url)
            self.assertIsNotNone(document.created_on)
            self.assertIsNotNone(document.last_updated_on)
            self.assertIsNotNone(document.status)
            self.assertIsNotNone(document.translate_to)
            self.assertIsNotNone(document.translation_progress)
            self.assertIsNotNone(document.id)
            self.assertIsNotNone(document.characters_charged)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_status_with_pagination(self, client):
        # prepare containers
        blob_data = [b'text 1', b'text 2', b'text 3', b'text 4', b'text 5', b'text 6']
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # wait for result
        job_result = client.wait_until_done(job_detail.id)

        # assert
        self.assertEqual(job_result.status, "Succeeded")  # job succeeded
        self.assertIsNotNone(job_result.created_on)
        self.assertIsNotNone(job_result.last_updated_on)
        self.assertIsNotNone(job_result.documents_total_count)
        self.assertIsNotNone(job_result.documents_failed_count)
        self.assertIsNotNone(job_result.documents_succeeded_count)
        self.assertIsNotNone(job_result.documents_in_progress_count)
        self.assertIsNotNone(job_result.documents_not_yet_started_count)
        self.assertIsNotNone(job_result.documents_cancelled_count)
        self.assertIsNotNone(job_result.total_characters_charged)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id=job_detail.id, results_per_page=2)
        self.assertEqual(len(doc_statuses), 1)
        # how to check for pages in ItemPaged
        for document in doc_statuses:
            self.assertIsNotNone(document.translated_document_url)
            self.assertIsNotNone(document.created_on)
            self.assertIsNotNone(document.last_updated_on)
            self.assertIsNotNone(document.status)
            self.assertIsNotNone(document.translate_to)
            self.assertIsNotNone(document.translation_progress)
            self.assertIsNotNone(document.id)
            self.assertIsNotNone(document.characters_charged)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_list_status_with_skip(self, client):
        # prepare containers
        blob_data = [b'text 1', b'text 2', b'text 3', b'text 4', b'text 5', b'text 6']
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    )
                ]
            )
        ]

        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)

        # wait for result
        job_result = client.wait_until_done(job_detail.id)

        # assert
        self.assertEqual(job_result.status, "Succeeded")  # job succeeded
        self.assertIsNotNone(job_result.created_on)
        self.assertIsNotNone(job_result.last_updated_on)
        self.assertIsNotNone(job_result.documents_total_count)
        self.assertIsNotNone(job_result.documents_failed_count)
        self.assertIsNotNone(job_result.documents_succeeded_count)
        self.assertIsNotNone(job_result.documents_in_progress_count)
        self.assertIsNotNone(job_result.documents_not_yet_started_count)
        self.assertIsNotNone(job_result.documents_cancelled_count)
        self.assertIsNotNone(job_result.total_characters_charged)

        # check doc statuses
        doc_statuses = client.list_all_document_statuses(job_id=job_detail.id, skip=2)
        self.assertEqual(len(doc_statuses), 1)
        # how to check for pages in ItemPaged
        for document in doc_statuses:
            self.assertIsNotNone(document.translated_document_url)
            self.assertIsNotNone(document.created_on)
            self.assertIsNotNone(document.last_updated_on)
            self.assertIsNotNone(document.status)
            self.assertIsNotNone(document.translate_to)
            self.assertIsNotNone(document.translation_progress)
            self.assertIsNotNone(document.id)
            self.assertIsNotNone(document.characters_charged)