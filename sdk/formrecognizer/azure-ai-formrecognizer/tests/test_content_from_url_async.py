# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest


class TestContentFromUrlAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            result = await client.recognize_content_from_url(self.invoice_url_pdf)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_auth_successful_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        result = await client.recognize_content_from_url(self.invoice_url_pdf)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = await client.recognize_content_from_url(self.invoice_url_pdf)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_bad_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(HttpResponseError):
            result = await client.recognize_content_from_url("https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_pass_stream(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read(4)  # makes the recording smaller

        with self.assertRaises(HttpResponseError):
            result = await client.recognize_content_from_url(receipt)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_transform_pdf(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        result = await client.recognize_content_from_url(self.invoice_url_pdf, cls=callback)
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_pdf(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))

        result = await client.recognize_content_from_url(self.invoice_url_pdf)
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 2)
        self.assertEqual(layout.tables[0].column_count, 6)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_transform_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        result = await client.recognize_content_from_url(self.form_url_jpg, cls=callback)
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_url_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))

        result = await client.recognize_content_from_url(self.form_url_jpg)
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 4)
        self.assertEqual(layout.tables[0].column_count, 3)
        self.assertEqual(layout.tables[1].row_count, 6)
        self.assertEqual(layout.tables[1].column_count, 4)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_multipage_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        result = await client.recognize_content_from_url(self.multipage_url_pdf)

        self.assertEqual(len(result), 3)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_multipage_transform_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        result = await client.recognize_content_from_url(self.multipage_url_pdf, cls=callback)
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)
