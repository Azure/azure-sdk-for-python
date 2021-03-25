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

        # get doc statuses
        doc_statuses = client.list_all_document_statuses(job_detail.id)

        # get first doc
        test_doc = next(doc_statuses)
        self.assertIsNotNone(test_doc.id)

        doc_status = client.get_document_status(job_id=job_detail.id, document_id=test_doc.id)
        self.assertIsNotNone(doc_status.id)
        self.assertIsNotNone(doc_status.translated_document_url)
        self.assertIsNotNone(doc_status.created_on)
        self.assertIsNotNone(doc_status.last_updated_on)
        self.assertIsNotNone(doc_status.status)
        self.assertIsNotNone(doc_status.translate_to)
        self.assertIsNotNone(doc_status.translation_progress)
        self.assertIsNotNone(doc_status.characters_charged)