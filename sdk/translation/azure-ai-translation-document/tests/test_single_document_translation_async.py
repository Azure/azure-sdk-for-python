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
from asynctestcase import AsyncDocumentTranslationTest
from preparer import (
    DocumentTranslationPreparer,
    DocumentTranslationClientPreparer as _DocumentTranslationClientPreparer,
)
from azure.ai.translation.document.aio import SingleDocumentTranslationClient

DocumentTranslationClientPreparer = functools.partial(
    _DocumentTranslationClientPreparer, SingleDocumentTranslationClient
)
from devtools_testutils.aio import recorded_by_proxy_async

TEST_Glossary_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./TestData/test-glossary.csv"))
TEST_INPUT_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./TestData/test-input.txt"))

from test_single_document_translation import TestSingleDocumentTranslation as _TestSingleDocumentTranslation


class TestSingleDocumentTranslation(AsyncDocumentTranslationTest):
    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_translate_text_document(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(
                document=_TestSingleDocumentTranslation()._get_document_content()
            )

            # Invoke document translation
            response_stream = await client.document_translate(
                body=document_translate_content, target_language=target_languages
            )

            # validate response
            translated_response = response_stream.decode("utf-8-sig")
            assert translated_response is not None
            return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_translate_single_csv_glossary(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(
                document=_TestSingleDocumentTranslation()._get_document_content(),
                glossary=_TestSingleDocumentTranslation()._get_single_glossary_content(),
            )

            # Invoke document translation
            response_stream = await client.document_translate(
                body=document_translate_content, target_language=target_languages
            )

            # validate response
            translated_response = response_stream.decode("utf-8-sig")
            assert translated_response is not None
            assert "test" in translated_response, "Glossary 'test' not found in translated response"
            return variables

    @DocumentTranslationPreparer()
    @DocumentTranslationClientPreparer()
    @recorded_by_proxy_async
    async def test_translate_multiple_csv_glossary(self, **kwargs):
        if self.is_live:  # running these tests in Live mode only
            client = kwargs.pop("client")
            variables = kwargs.pop("variables", {})
            target_languages = "hi"

            # prepare translation content
            document_translate_content = DocumentTranslateContent(
                document=_TestSingleDocumentTranslation()._get_document_content(),
                glossary=_TestSingleDocumentTranslation()._get_multiple_glossary_contents(),
            )

            # Invoke document translation and validate exception
            try:
                await client.document_translate(body=document_translate_content, target_language=target_languages)
            except HttpResponseError as e:
                assert e.status_code == 400
            return variables
