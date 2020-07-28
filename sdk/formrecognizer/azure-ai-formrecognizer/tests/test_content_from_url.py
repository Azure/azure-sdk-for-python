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
from azure.ai.formrecognizer import FormRecognizerClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestContentFromUrl(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_encoded_url(self, client):
        with pytest.raises(HttpResponseError) as e:
            poller = client.begin_recognize_content_from_url("https://fakeuri.com/blank%20space")
        client.close()
        self.assertIn("https://fakeuri.com/blank%20space", e.value.response.request.body)

    @GlobalFormRecognizerAccountPreparer()
    def test_content_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_auth_successful_key(self, client):
        poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)
        result = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    def test_content_url_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_content_from_url("https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_pass_stream(self, client):
        with open(self.receipt_jpg, "rb") as receipt:
            with self.assertRaises(HttpResponseError):
                poller = client.begin_recognize_content_from_url(receipt)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content_from_url(self.invoice_url_pdf, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_pdf(self, client):
        poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)
        result = poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 2)
        self.assertEqual(layout.tables[0].column_count, 6)
        self.assertEqual(layout.tables[0].page_number, 1)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content_from_url(self.form_url_jpg, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_url_jpg(self, client):
        poller = client.begin_recognize_content_from_url(self.form_url_jpg)
        result = poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 4)
        self.assertEqual(layout.tables[0].column_count, 3)
        self.assertEqual(layout.tables[1].row_count, 6)
        self.assertEqual(layout.tables[1].column_count, 4)
        self.assertEqual(layout.tables[0].page_number, 1)
        self.assertEqual(layout.tables[1].page_number, 1)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_multipage_url(self, client):
        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf)
        result = poller.result()

        self.assertEqual(len(result), 3)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_multipage_transform_url(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_content_continuation_token(self, client):
        initial_poller = client.begin_recognize_content_from_url(self.form_url_jpg)
        cont_token = initial_poller.continuation_token()

        poller = client.begin_recognize_content_from_url(self.form_url_jpg, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_multipage_table_span_pdf(self, client):
        poller = client.begin_recognize_content_from_url(self.multipage_table_url_pdf)
        result = poller.result()
        self.assertEqual(len(result), 2)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertEqual(len(layout.tables), 2)
        self.assertEqual(layout.tables[0].row_count, 30)
        self.assertEqual(layout.tables[0].column_count, 5)
        self.assertEqual(layout.tables[0].page_number, 1)
        self.assertEqual(layout.tables[1].row_count, 6)
        self.assertEqual(layout.tables[1].column_count, 5)
        self.assertEqual(layout.tables[1].page_number, 1)
        layout = result[1]
        self.assertEqual(len(layout.tables), 1)
        self.assertEqual(layout.page_number, 2)
        self.assertEqual(layout.tables[0].row_count, 24)
        self.assertEqual(layout.tables[0].column_count, 5)
        self.assertEqual(layout.tables[0].page_number, 2)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_content_multipage_table_span_transform(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content_from_url(self.multipage_table_url_pdf, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)
