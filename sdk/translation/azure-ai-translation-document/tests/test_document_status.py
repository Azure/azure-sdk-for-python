# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest, Document
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class DocumentStatus(DocumentTranslationTest):

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

        # submit and validate translation operation
        translation_id = self._begin_and_validate_translation(client, translation_inputs, len(blob_data), target_language)

        # get doc statuses
        doc_statuses = client.list_all_document_statuses(translation_id)
        self.assertIsNotNone(doc_statuses)

        # get first doc
        first_doc = next(doc_statuses)
        self.assertIsNotNone(first_doc.id)

        # get doc details
        doc_status = client.get_document_status(translation_id=translation_id, document_id=first_doc.id)
        self._validate_doc_status(doc_status, target_language)