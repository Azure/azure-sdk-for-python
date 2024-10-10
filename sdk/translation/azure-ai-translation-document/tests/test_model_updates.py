# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from azure.ai.translation.document.models import FileFormatType
from testcase import DocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from devtools_testutils import recorded_by_proxy
from azure.ai.translation.document import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)

class TestModelUpdates(DocumentTranslationTest):
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_start_translation_details_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables", {})

        docs_count = 2
        self._prepare_and_validate_start_translation_details(client, docs_count, wait=False, variables=variables)
        return variables
    
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_supported_formats(self, **kwargs):
        client = kwargs.pop("client")
        
        # get supported glossary formats
        supported_glossary_formats = client._get_supported_formats(FileFormatType.GLOSSARY)
        assert supported_glossary_formats is not None
        # validate
        for glossary_format in supported_glossary_formats:
            self._validate_format(glossary_format)

        # get supported document formats
        supported_document_formats = client._get_supported_formats(FileFormatType.DOCUMENT)
        assert supported_document_formats is not None
        # validate
        for document_format in supported_document_formats:
            self._validate_format(document_format)

        # get supported formats
        supported_formats = client._get_supported_formats()
        assert supported_formats is not None
        # validate
        for format in supported_formats:
            self._validate_format(format)
    