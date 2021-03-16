# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient, BatchDocumentInput, StorageTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestTranslation(DocumentTranslationTest):

    def _setup(self, data=None):
        """Creates a source and target container.

        Pass data in as bytes (or as a list[bytes] to create more than one blob) in the source container.
        """
        if self.is_live:
            self.source_container_sas_url = self.create_source_container(data=data or b'This is written in english.')
            self.target_container_sas_url = self.create_target_container()
        else:
            self.source_container_sas_url = "source_container_sas_url"
            self.target_container_sas_url = "target_container_sas_url"

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
