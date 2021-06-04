# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from testcase import DocumentTranslationTest, Document
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget

class AsyncDocumentTranslationTest(DocumentTranslationTest):

    def __init__(self, method_name):
        super(AsyncDocumentTranslationTest, self).__init__(method_name)

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity.aio import ClientSecretCredential
            return ClientSecretCredential(
                os.getenv("TRANSLATION_TENANT_ID"),
                os.getenv("TRANSLATION_CLIENT_ID"),
                os.getenv("TRANSLATION_CLIENT_SECRET"),
            )

    async def _begin_and_validate_translation_async(self, async_client, translation_inputs, total_docs_count, language=None):
        # submit operation
        poller = await async_client.begin_translation(translation_inputs)
        self.assertIsNotNone(poller.id)
        # wait for result
        doc_statuses = await poller.result()
        # validate
        self._validate_translation_metadata(poller=poller, status='Succeeded', total=total_docs_count, succeeded=total_docs_count)
        async for doc in doc_statuses:
            self._validate_doc_status(doc, language)
        return poller.id

    # client helpers
    async def _begin_multiple_translations_async(self, async_client, operations_count, **kwargs):
        wait_for_operation = kwargs.pop('wait', True)
        language_code = kwargs.pop('language_code', "es")
        docs_per_operation = kwargs.pop('docs_per_operation', 2)
        result_ids = []
        for i in range(operations_count):
            # prepare containers and test data
            '''
                # note
                since we're only testing the client library
                we can use sync container calls in here
                no need for async container clients!
            '''
            blob_data = Document.create_dummy_docs(docs_per_operation)
            source_container_sas_url = self.create_source_container(data=blob_data)
            target_container_sas_url = self.create_target_container()

            # prepare translation inputs
            translation_inputs = [
                DocumentTranslationInput(
                    source_url=source_container_sas_url,
                    targets=[
                        TranslationTarget(
                            target_url=target_container_sas_url,
                            language_code=language_code
                        )
                    ]
                )
            ]

            # submit multiple operations
            poller = await async_client.begin_translation(translation_inputs)
            self.assertIsNotNone(poller.id)
            if wait_for_operation:
                await poller.result()
            else:
                await poller.wait()
            result_ids.append(poller.id)

        return result_ids

    async def _begin_and_validate_translation_with_multiple_docs_async(self, async_client, docs_count, **kwargs):
        # get input parms
        wait_for_operation = kwargs.pop('wait', False)
        language_code = kwargs.pop('language_code', "es")

        # prepare containers and test data
        blob_data = Document.create_dummy_docs(docs_count=docs_count)
        source_container_sas_url = self.create_source_container(data=blob_data)
        target_container_sas_url = self.create_target_container()

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language_code=language_code
                    )
                ]
            )
        ]

        # submit operation
        poller = await async_client.begin_translation(translation_inputs)
        self.assertIsNotNone(poller.id)
        # wait for result
        if wait_for_operation:
            result = await poller.result()
            async for doc in result:
                self._validate_doc_status(doc, "es")

        # validate
        self._validate_translation_metadata(poller=poller)
        return poller
