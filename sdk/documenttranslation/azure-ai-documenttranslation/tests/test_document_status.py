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