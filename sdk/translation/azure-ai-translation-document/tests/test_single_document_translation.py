# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
import json
import os
from typing import List

import requests
from azure.core.exceptions import HttpResponseError
from azure.ai.translation.document.models import DocumentTranslateContent
from azure.core.rest._helpers import FileType
from testcase import DocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from azure.ai.translation.document import SingleDocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(
    _DocumentTranslationClientPreparer, SingleDocumentTranslationClient
)

from devtools_testutils import recorded_by_proxy

TEST_Glossary_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./TestData/test-glossary.csv"))
TEST_INPUT_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./TestData/test-input.txt"))


class TestSingleDocumentTranslation(DocumentTranslationTest):
    def _get_document_content(self):
        file_name = os.path.basename(TEST_INPUT_FILE_NAME)
        file_type = "text/html"
        with open(TEST_INPUT_FILE_NAME, "r") as file:
            file_contents = file.read()

        document_content: FileType = (file_name, file_contents, file_type)
        return document_content

    def _get_single_glossary_content(self):
        file_name = os.path.basename(TEST_Glossary_FILE_NAME)
        file_type = "text/csv"
        with open(TEST_Glossary_FILE_NAME, "r") as file:
            file_contents = file.read()

        glossary_content: List[FileType] = [(file_name, file_contents, file_type)]
        return glossary_content

    def _get_multiple_glossary_contents(self):
        file_name = os.path.basename(TEST_Glossary_FILE_NAME)
        file_type = "text/csv"
        with open(TEST_Glossary_FILE_NAME, "r") as file:
            file_contents = file.read()

        glossary_contents: List[FileType] = [
            (file_name, file_contents, file_type),
            (file_name, file_contents, file_type),
        ]
        return glossary_contents

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translate_text_document(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(document=self._get_document_content())

            # Invoke document translation
            response_stream = client.document_translate(
                body=document_translate_content, target_language=target_languages
            )

            # validate response
            translated_response = response_stream.decode("utf-8-sig")
            assert translated_response is not None
            return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translate_single_csv_glossary(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(
                document=self._get_document_content(), glossary=self._get_single_glossary_content()
            )

            # Invoke document translation
            response_stream = client.document_translate(
                body=document_translate_content, target_language=target_languages
            )

            # validate response
            translated_response = response_stream.decode("utf-8-sig")
            assert translated_response is not None
            assert "test" in translated_response, "Glossary 'test' not found in translated response"
            return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy
    def test_translate_multiple_csv_glossary(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(
                document=self._get_document_content(), glossary=self._get_multiple_glossary_contents()
            )

            # Invoke document translation and validate exception
            try:
                client.document_translate(body=document_translate_content, target_language=target_languages)
            except HttpResponseError as e:
                assert e.status_code == 400
            return variables
