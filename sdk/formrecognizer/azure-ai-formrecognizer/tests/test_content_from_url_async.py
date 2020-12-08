# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormRecognizerApiVersion
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestContentFromUrlAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_encoded_url(self, client):
        with pytest.raises(HttpResponseError) as e:
            poller = await client.begin_recognize_content_from_url("https://fakeuri.com/blank%20space")
        await client.close()
        self.assertIn("https://fakeuri.com/blank%20space", e.value.response.request.body)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            async with client:
                poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_auth_successful_key(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content_from_url("https://badurl.jpg")
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_pass_stream(self, client):
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read(4)  # makes the recording smaller

        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content_from_url(receipt)
                result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_pdf(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.invoice_url_pdf)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 3)
        self.assertEqual(layout.tables[0].column_count, 6)
        self.assertEqual(layout.tables[0].page_number, 1)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.form_url_jpg, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_url_jpg(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.form_url_jpg)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 5)
        self.assertEqual(layout.tables[0].column_count, 5)
        self.assertEqual(layout.tables[1].row_count, 4)
        self.assertEqual(layout.tables[1].column_count, 2)
        self.assertEqual(layout.tables[0].page_number, 1)
        self.assertEqual(layout.tables[1].page_number, 1)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_url(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf)
            result = await poller.result()
        self.assertEqual(len(result), 3)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_transform_url(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_content_continuation_token(self, client):
        async with client:
            initial_poller = await client.begin_recognize_content_from_url(self.form_url_jpg)
            cont_token = initial_poller.continuation_token()

            poller = await client.begin_recognize_content_from_url(None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_table_span_pdf(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_table_url_pdf)
            result = await poller.result()
        self.assertEqual(len(result), 2)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertEqual(len(layout.tables), 2)
        self.assertEqual(layout.tables[0].row_count, 29)
        self.assertEqual(layout.tables[0].column_count, 4)
        self.assertEqual(layout.tables[0].page_number, 1)
        self.assertEqual(layout.tables[1].row_count, 6)
        self.assertEqual(layout.tables[1].column_count, 5)
        self.assertEqual(layout.tables[1].page_number, 1)
        layout = result[1]
        self.assertEqual(len(layout.tables), 1)
        self.assertEqual(layout.page_number, 2)
        self.assertEqual(layout.tables[0].row_count, 23)
        self.assertEqual(layout.tables[0].column_count, 5)
        self.assertEqual(layout.tables[0].page_number, 2)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_table_span_transform(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_table_url_pdf, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_selection_marks(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_content_selection_marks_v2(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_specify_pages(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1"])
            result = await poller.result()
            assert len(result) == 1

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1", "3"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2", "3"])
            result = await poller.result()
            assert len(result) == 3

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_language_specified(self, client):
        async with client:
            poller = await client.begin_recognize_content_from_url(self.form_url_jpg, language="de")
            assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
            await poller.wait()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_content_language_error(self, client):
        async with client:
            with pytest.raises(HttpResponseError) as e:
                await client.begin_recognize_content_from_url(self.form_url_jpg, language="not a language")
            assert "NotSupportedLanguage" == e.value.error.code

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_content_language_v2(self, client):
        async with client:
            with pytest.raises(ValueError) as e:
                await client.begin_recognize_content_from_url(self.form_url_jpg, language="en")
            assert "'language' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="german")
    async def test_content_language_german(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="de")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="chinese_simplified")
    async def test_content_language_chinese_simplified(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="zh-Hans")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="dutch")
    async def test_content_language_dutch(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="nl")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="french")
    async def test_content_language_french(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="fr")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="italian")
    async def test_content_language_italian(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="it")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="portuguese")
    async def test_content_language_portuguese(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="pt")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(language="spanish")
    async def test_content_language_spanish(self, client, language_form):
        async with client:
            poller = await client.begin_recognize_content_from_url(language_form, language="es")
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
