# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.translation.document import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestSupportedFormats(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_supported_document_formats(self, client):
        # get supported formats
        supported_doc_formats = client.get_supported_document_formats()
        self.assertIsNotNone(supported_doc_formats)
        # validate
        for doc_format in supported_doc_formats:
            self._validate_format(doc_format)

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_supported_glossary_formats(self, client):
        # get supported formats
        supported_glossary_formats = client.get_supported_glossary_formats()
        self.assertIsNotNone(supported_glossary_formats)
        # validate
        for glossary_format in supported_glossary_formats:
            self._validate_format(glossary_format)