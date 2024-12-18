# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from asynctestcase import AsyncDocumentTranslationTest
from azure.ai.translation.document.models import FileFormatType
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.document.aio import DocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestModelUpdates(AsyncDocumentTranslationTest):
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_start_translation_details_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})

        docs_count = 2
        await self._prepare_and_validate_start_translation_details_async(
            client, docs_count, wait=False, variables=variables
        )
        return variables
