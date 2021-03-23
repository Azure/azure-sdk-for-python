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

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_translate(self, client):
        # this uses generated code and should be deleted. Using it to test live tests pending our code in master
        self._setup()  # set up test resources

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=self.source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=self.target_container_sas_url,
                        language_code="es"
                    )
                ],
                prefix="document"
            )
        ]

        # submit job
        job_detail = client.create_translation_job(translation_inputs)

        # wait for result
        job_result = client.wait_until_done(job_detail.id)
