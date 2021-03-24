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
        from azure.ai.documenttranslation._generated.models import BatchRequest, SourceInput, TargetInput
        self._setup()  # set up test resources

        response_headers = client._client.document_translation._submit_batch_request_initial(
            inputs=[
                BatchRequest(
                    source=SourceInput(
                        source_url=self.source_container_sas_url
                    ),
                    targets=[TargetInput(
                        target_url=self.target_container_sas_url,
                        language="es"
                    )]
                )
            ],
            cls=lambda pipeline_response, _, response_headers: response_headers
        )

        batch_id = response_headers['Operation-Location'].split('/')[-1]
        assert batch_id
        self.wait()
        result = client._client.document_translation.get_operation_status(batch_id)
        assert result
