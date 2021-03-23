# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from testcase import DocumentTranslationTest
from preparer import DocumentTranslationPreparer, DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer
from azure.ai.documenttranslation import DocumentTranslationClient
DocumentTranslationClientPreparer = functools.partial(_DocumentTranslationClientPreparer, DocumentTranslationClient)


class TestSupportedFormats(DocumentTranslationTest):

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_supported_document_formats(self, client):
        self._setup()  # set up test resources

        supported_doc_formats = client.get_document_formats()  # List[FileFormat]

        for doc_format in supported_doc_formats:
            assert doc_format

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    def test_supported_glossary_formats(self, client):
        self._setup()  # set up test resources

        supported_glossary_formats = client.get_glossary_formats()  # List[FileFormat]

        for glossary_format in supported_glossary_formats:
            assert glossary_format
