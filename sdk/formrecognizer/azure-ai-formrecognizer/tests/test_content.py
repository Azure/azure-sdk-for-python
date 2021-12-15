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
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormRecognizerApiVersion
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestContentFromStream(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_content_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_content(myfile)

    @FormRecognizerPreparer()
    def test_content_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_content(b"xx", content_type="application/pdf")

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_enum_content_type(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = client.begin_recognize_content(
            myfile,
            content_type=FormContentType.APPLICATION_PDF
        )
        result = poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_content(
                damaged_pdf,
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_bad_content_type_param_passed(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_content(
                myfile,
                content_type="application/jpeg"
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_auto_detect_unsupported_stream_content(self, client):
        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_content(
                myfile
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(myform, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_reading_order(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myform = fd.read()

        poller = client.begin_recognize_content(myform, reading_order="natural")

        assert 'natural' == poller._polling_method._initial_response.http_response.request.query['readingOrder']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(myform, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_stream_jpg(self, client):
        with open(self.form_jpg, "rb") as stream:
            poller = client.begin_recognize_content(stream)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)
        assert layout.tables[0].row_count == 5
        assert layout.tables[0].column_count== 4
        assert layout.tables[1].row_count == 4
        assert layout.tables[1].column_count== 2
        assert layout.tables[0].page_number == 1
        assert layout.tables[1].page_number== 1

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_multipage(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_content(invoice)
        result = poller.result()

        assert len(result) == 3
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(myform, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_continuation_token(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        initial_poller = client.begin_recognize_content(myfile)
        cont_token = initial_poller.continuation_token()

        poller = client.begin_recognize_content(None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_multipage_table_span_transform(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            myform = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(myform, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_selection_marks(self, client):
        with open(self.selection_form_pdf, "rb") as fd:
            myform = fd.read()

        poller = client.begin_recognize_content(myform)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_content_selection_marks_v2(self, client):
        with open(self.selection_form_pdf, "rb") as fd:
            myform = fd.read()

        poller = client.begin_recognize_content(myform)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_specify_pages(self, client):

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myform = fd.read()

        poller = client.begin_recognize_content(myform, pages=["1"])
        result = poller.result()
        assert len(result) == 1

        poller = client.begin_recognize_content(myform, pages=["1", "3"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content(myform, pages=["1-2"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content(myform, pages=["1-2", "3"])
        result = poller.result()
        assert len(result) == 3

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_language_specified(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        poller = client.begin_recognize_content(myfile, language="de")
        assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_language_error(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_content(myfile, language="not a language")
        assert "NotSupportedLanguage" == e.value.error.code

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_content_language_v2(self, client):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_content(myfile, language="en")
        assert "'language' is only available for API version V2_1 and up" in str(e.value)
