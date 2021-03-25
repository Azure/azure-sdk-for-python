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


class TestTranslation(DocumentTranslationTest):

    def _submit_translation_and_validate_result(self, client, translation_inputs, total_docs_count):
        # submit job
        job_detail = client.create_translation_job(translation_inputs)
        self.assertIsNotNone(job_detail.id)
        # wait for result
        job_result = client.wait_until_done(job_detail.id)
        # assert
        self.assertEqual(job_result.status, "Succeeded")
        # docs count
        self.assertEqual(job_result.documents_total_count, total_docs_count)
        self.assertEqual(job_result.documents_failed_count, 0)
        self.assertEqual(job_result.documents_succeeded_count, total_docs_count)
        self.assertEqual(job_result.documents_in_progress_count, 0)
        self.assertEqual(job_result.documents_not_yet_started_count, 0)
        self.assertEqual(job_result.documents_cancelled_count, 0)
        # generic assertions
        self.assertIsNotNone(job_result.total_characters_charged)
        self.assertIsNotNone(job_result.created_on)
        self.assertIsNotNone(job_result.last_updated_on)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target(self, client):
        # prepare containers and test data
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

        # submit job and test
        self._submit_translation_and_validate_result(client, translation_inputs, 1)
        


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_two_targets(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()
        additional_target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="es"
                    ),
                    TranslationTarget(
                        target_url=additional_target_container_sas_url,
                        language_code="fr"
                    )
                ]
            )
        ]

        # submit job and test
        self._submit_translation_and_validate_result(client, translation_inputs, 2)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_multiple_sources_single_target(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        source_container_sas_url = self.create_source_container(data=blob_data)
        blob_data = b'This is some text2'
        additional_source_container_sas_url = self.create_source_container(data=blob_data)
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
            ),
            DocumentTranslationInput(
                source_url=additional_source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code="fr"
                    )
                ]
            )
        ]

        # submit job and test
        self._submit_translation_and_validate_result(client, translation_inputs, 2)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_prefix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        prefix = "xyz"
        source_container_sas_url = self.create_source_container(data=blob_data, blob_prefix=prefix)
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
                ],
                prefix=prefix
            )
        ]

        # submit job and test
        self._submit_translation_and_validate_result(client, translation_inputs, 1)


    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_single_source_single_target_with_suffix(self, client):
        # prepare containers and test data
        blob_data = b'This is some text'
        suffix = "txt"
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
                ],
                suffix=suffix
            )
        ]

        # submit job and test
        self._submit_translation_and_validate_result(client, translation_inputs, 1)


