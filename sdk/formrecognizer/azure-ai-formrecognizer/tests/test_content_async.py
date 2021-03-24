# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestContentFromStreamAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_content_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_content(myfile)
                result = await poller.result()

    @FormRecognizerPreparer()
    async def test_content_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_content(b"xxx", content_type="application/pdf")
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_passing_enum_content_type(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        async with client:
            poller = await client.begin_recognize_content(
                myfile,
                content_type=FormContentType.APPLICATION_PDF
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content(
                    damaged_pdf,
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    damaged_pdf,
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes_io(self, client):
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_content(
                    damaged_pdf,
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    damaged_pdf,
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_blank_page(self, client):
        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        async with client:
            poller = await client.begin_recognize_content(
                blank,
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_passing_bad_content_type_param_passed(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    myfile,
                    content_type="application/jpeg"
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_stream_passing_url(self, client):
        with self.assertRaises(TypeError):
            async with client:
                poller = await client.begin_recognize_content("https://badurl.jpg", content_type="application/json")
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_auto_detect_unsupported_stream_content(self, client):
        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_content(
                    myfile
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(myform, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_stream_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        async with client:
            poller = await client.begin_recognize_content(myform)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)
        self.assertEqual(layout.tables[0].row_count, 3)
        self.assertEqual(layout.tables[0].column_count, 6)
        self.assertEqual(layout.tables[0].page_number, 1)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(myform, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_stream_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            myform = fd.read()

        async with client:
            poller = await client.begin_recognize_content(myform)
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

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            invoice = fd.read()
        async with client:
            poller = await client.begin_recognize_content(invoice)
            result = await poller.result()

        self.assertEqual(len(result), 3)
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_recognize_content(myform, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_content_continuation_token(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        async with client:
            initial_poller = await client.begin_recognize_content(myfile)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_content(None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error


    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_table_span_pdf(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            myfile = fd.read()
        async with client:
            poller = await client.begin_recognize_content(myfile)
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

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_multipage_table_span_transform(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)
        async with client:
            poller = await client.begin_recognize_content(myform, cls=callback)
            result = await poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_selection_marks(self, client):
        with open(self.selection_form_pdf, "rb") as fd:
            myform = fd.read()

        async with client:
            poller = await client.begin_recognize_content(myform)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_content_selection_marks_v2(self, client):
        with open(self.selection_form_pdf, "rb") as fd:
            myform = fd.read()

        async with client:
            poller = await client.begin_recognize_content(myform)
            result = await poller.result()
        self.assertEqual(len(result), 1)
        layout = result[0]
        self.assertEqual(layout.page_number, 1)
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_specify_pages(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myform = fd.read()

        async with client:
            poller = await client.begin_recognize_content(myform, pages=["1"])
            result = await poller.result()
            assert len(result) == 1

            poller = await client.begin_recognize_content(myform, pages=["1", "3"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content(myform, pages=["1-2"])
            result = await poller.result()
            assert len(result) == 2

            poller = await client.begin_recognize_content(myform, pages=["1-2", "3"])
            result = await poller.result()
            assert len(result) == 3

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_language_specified(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        async with client:
            poller = await client.begin_recognize_content(myfile, language="de")
            assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_content_language_error(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        async with client:
            with pytest.raises(HttpResponseError) as e:
                await client.begin_recognize_content(myfile, language="not a language")
            assert "NotSupportedLanguage" == e.value.error.code

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_content_language_v2(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        async with client:
            with pytest.raises(ValueError) as e:
                await client.begin_recognize_content(myfile, language="en")
            assert "'language' is only available for API version V2_1_PREVIEW and up" in str(e.value)
