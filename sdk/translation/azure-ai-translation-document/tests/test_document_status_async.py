# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import Document
from asynctestcase import AsyncDocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.document import DocumentTranslationInput, TranslationTarget
from azure.ai.translation.document.aio import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestDocumentStatus(AsyncDocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_list_statuses(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})
        # prepare containers and test data
        blob_data = [Document(data=b'This is some text')]
        source_container_sas_url = self.create_source_container(data=blob_data, variables=variables)
        target_container_sas_url = self.create_target_container(variables=variables)
        target_language = "es"

        # prepare translation inputs
        translation_inputs = [
            DocumentTranslationInput(
                source_url=source_container_sas_url,
                targets=[
                    TranslationTarget(
                        target_url=target_container_sas_url,
                        language=target_language
                    )
                ]
            )
        ]

        # submit and validate translation translation
        translation_id = await self._begin_and_validate_translation_async(client, translation_inputs, len(blob_data), target_language)

        # get doc statuses
        doc_statuses = client.list_document_statuses(translation_id)
        assert doc_statuses is not None

        # get first doc
        first_doc = await doc_statuses.__anext__()
        assert first_doc.id is not None

        # get doc details
        doc_status = await client.get_document_status(translation_id=translation_id, document_id=first_doc.id)
        self._validate_doc_status(doc_status, target_language)
        return variables
