# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import time
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient, BatchDocumentInput, StorageTarget
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestTranslation(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_storage_sources(self, client):

        sources = client.get_supported_storage_sources()
        assert sources

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_translate(self, client, documenttranslation_source_container_sas_url, documenttranslation_target_container_sas_url):
        from azure.ai.documenttranslation._generated.models import BatchRequest, SourceInput, TargetInput

        poller = client._client.document_translation.begin_submit_batch_request(
            inputs=[
                BatchRequest(
                    source=SourceInput(
                        source_url=documenttranslation_source_container_sas_url
                    ),
                    targets=[TargetInput(
                        target_url=documenttranslation_target_container_sas_url,
                        language="es"
                    )]
                )
            ],
            polling=True
        )

        batch_id = poller._polling_method._operation._async_url.split("/batches/")[1]
        assert batch_id
