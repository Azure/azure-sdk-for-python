# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from io import BytesIO
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest


class TestContentFromStreamAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            poller = await client.begin_recognize_content(myfile)
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_authentication_successful_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = await client.begin_recognize_content(myfile)
        result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = await client.begin_recognize_content(b"xxx", content_type="application/pdf")
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_enum_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = await client.begin_recognize_content(
            myfile,
            content_type=FormContentType.application_pdf
        )
        result = await poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_passed_as_bytes(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = await client.begin_recognize_content(
                damaged_pdf,
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = await client.begin_recognize_content(
                damaged_pdf,
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_passed_as_bytes_io(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = await client.begin_recognize_content(
                damaged_pdf,
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = await client.begin_recognize_content(
                damaged_pdf,
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_blank_page(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        poller = await client.begin_recognize_content(
            blank,
        )
        result = await poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_bad_content_type_param_passed(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            poller = await client.begin_recognize_content(
                myfile,
                content_type="application/jpeg"
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_stream_passing_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(TypeError):
            poller = await client.begin_recognize_content("https://badurl.jpg", content_type="application/json")
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_auto_detect_unsupported_stream_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = await client.begin_recognize_content(
                myfile
            )
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_stream_transform_pdf(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = await client.begin_recognize_content(myform, cls=callback)
        result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_stream_pdf(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        poller = await client.begin_recognize_content(myform)
        result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 2)
        self.assertEqual(layout.tables[0].column_count, 6)
        self.assertEqual(layout.tables[0].page_number, 1)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_stream_transform_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.form_jpg, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = await client.begin_recognize_content(myform, cls=callback)
        result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_stream_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))
        with open(self.form_jpg, "rb") as fd:
            myform = fd.read()

        poller = await client.begin_recognize_content(myform)
        result = await poller.result()
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
    async def test_content_multipage(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.multipage_invoice_pdf, "rb") as fd:
            invoice = fd.read()
        poller = await client.begin_recognize_content(invoice)
        result = await poller.result()

        self.assertEqual(len(result), 3)
        self.assertFormPagesHasValues(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_content_multipage_transform(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = await client.begin_recognize_content(myform, cls=callback)
        result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.live_test_only
    async def test_content_continuation_token(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        initial_poller = await client.begin_recognize_content(myfile)
        cont_token = initial_poller.continuation_token()

        poller = await client.begin_recognize_content(myfile, continuation_token=cont_token)
        result = await poller.result()
        self.assertIsNotNone(result)
        await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error


    @GlobalFormRecognizerAccountPreparer()
    async def test_content_multipage_table_span_pdf(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account,
                                      AzureKeyCredential(form_recognizer_account_key))

        with open(self.multipage_table_pdf, "rb") as fd:
            myfile = fd.read()
        poller = await client.begin_recognize_content(myfile)
        result = await poller.result()
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
    async def test_content_multipage_table_span_transform(self, resource_group, location, form_recognizer_account,
                                                form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.multipage_table_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = await client.begin_recognize_content(myform, cls=callback)
        result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)
