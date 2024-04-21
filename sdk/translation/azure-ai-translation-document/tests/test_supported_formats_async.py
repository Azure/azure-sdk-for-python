# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from asynctestcase import AsyncDocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.translation.document.aio import DocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)
from azure.ai.translation.document.models._enums import FormatType

class TestSupportedFormats(AsyncDocumentTranslationTest):
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_supported_document_formats(self, **kwargs):
        client = kwargs.pop("client")
        # get supported formats
        supported_doc_formats = await client.get_supported_formats(type=FormatType.DOCUMENT)
        assert supported_doc_formats is not None
        # validate
        for doc_format in supported_doc_formats.value:
            self._validate_format(doc_format)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_supported_glossary_formats(self, **kwargs):
        client = kwargs.pop("client")
        # get supported formats
        supported_glossary_formats = await client.get_supported_formats(type=FormatType.GLOSSARY)
        assert supported_glossary_formats is not None
        # validate
        for glossary_format in supported_glossary_formats.value:
            self._validate_format(glossary_format)
