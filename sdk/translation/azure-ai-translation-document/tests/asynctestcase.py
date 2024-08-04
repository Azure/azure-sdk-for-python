# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import AzureRecordedTestCase
from testcase import DocumentTranslationTest, Document
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget


class AsyncDocumentTranslationTest(DocumentTranslationTest, AzureRecordedTestCase):
    async def _begin_and_validate_translation_async(
        self, async_client, translation_inputs, total_docs_count, language=None, **kwargs
    ):
        wait_for_operation = kwargs.pop("wait", True)
        # submit operation
        poller = await async_client.begin_translation(translation_inputs)
        assert poller.id is not None
        # wait for result
        if wait_for_operation:
            result = await poller.result()
            async for doc in result:
                self._validate_doc_status(doc, language)

        assert poller.details.id is not None

        # validate
        self._validate_translation_metadata(
            poller=poller, status="Succeeded", total=total_docs_count, succeeded=total_docs_count
        )

        return poller.id

    # client helpers
    async def _begin_multiple_translations_async(self, async_client, operations_count, **kwargs):
        container_suffix = kwargs.pop("container_suffix", "")
        variables = kwargs.pop("variables", {})
        wait_for_operation = kwargs.pop("wait", True)
        language = kwargs.pop("language", "es")
        docs_per_operation = kwargs.pop("docs_per_operation", 2)
        result_ids = []
        for i in range(operations_count):
            # prepare containers and test data
            """
            # note
            since we're only testing the client library
            we can use sync container calls in here
            no need for async container clients!
            """
            blob_data = Document.create_dummy_docs(docs_per_operation)
            source_container_sas_url = self.create_source_container(
                data=blob_data, variables=variables, container_suffix=str(i) + container_suffix
            )
            target_container_sas_url = self.create_target_container(
                variables=variables, container_suffix=str(i) + container_suffix
            )

            # prepare translation inputs
            translation_inputs = [
                DocumentTranslationInput(
                    source_url=source_container_sas_url,
                    targets=[TranslationTarget(target_url=target_container_sas_url, language=language)],
                )
            ]

            # submit multiple operations
            poller = await async_client.begin_translation(translation_inputs)
            assert poller.id is not None
            if wait_for_operation:
                await poller.result()
            else:
                await poller.wait()
            result_ids.append(poller.id)

        return result_ids

    async def _begin_and_validate_translation_with_multiple_docs_async(self, async_client, docs_count, **kwargs):
        # get input params
        variables = kwargs.pop("variables", {})
        wait_for_operation = kwargs.pop("wait", False)
        language = kwargs.pop("language", "es")

        # prepare containers and test data
        blob_data = Document.create_dummy_docs(docs_count=docs_count)
        source_container_sas_url = self.create_source_container(data=blob_data, variables=variables)
        target_container_sas_url = self.create_target_container(variables=variables)

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[TranslationTarget(target_url=target_container_sas_url, language=language)],
            )
        ]
        # submit operation
        poller = await async_client.begin_translation(translation_inputs)
        assert poller.id is not None
        # wait for result
        if wait_for_operation:
            result = await poller.result()
            async for doc in result:
                self._validate_doc_status(doc, "es")

        # validate
        self._validate_translation_metadata(poller=poller)
        return poller
