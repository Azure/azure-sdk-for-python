# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormRecognizerApiVersion
from testcase import FormRecognizerTest
from preparers import FormRecognizerPreparer, get_sync_client
from conftest import skip_flaky_test

get_fr_client = functools.partial(get_sync_client, FormRecognizerClient)


class TestContentFromStream(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_content_bad_endpoint(self, **kwargs):
        formrecognizer_test_api_key = "fakeZmFrZV9hY29jdW50X2tleQ=="
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_content(my_file)

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_authentication_bad_key(self, **kwargs):
        client = get_fr_client(api_key="xxxx")
        with pytest.raises(ClientAuthenticationError):
            poller = client.begin_recognize_content(b"xx", content_type="application/pdf")

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_passing_enum_content_type(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        poller = client.begin_recognize_content(
            my_file,
            content_type=FormContentType.APPLICATION_PDF
        )
        result = poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_damaged_file_passed_as_bytes(self):
        client = get_fr_client()
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with pytest.raises(HttpResponseError):
            poller = client.begin_recognize_content(
                damaged_pdf,
            )

    @FormRecognizerPreparer()
    def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            poller = client.begin_recognize_content(
                my_file,
                content_type="application/jpeg"
            )

    @FormRecognizerPreparer()
    def test_auto_detect_unsupported_stream_content(self, **kwargs):
        client = get_fr_client()
        with open(self.unsupported_content_py, "rb") as fd:
            my_file = fd.read()

        with pytest.raises(ValueError):
            poller = client.begin_recognize_content(
                my_file
            )

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_stream_transform_pdf(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(form, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_reading_order(self):
        client = get_fr_client()
        with open(self.invoice_pdf, "rb") as fd:
            form = fd.read()

        poller = client.begin_recognize_content(form, reading_order="natural")

        assert 'natural' == poller._polling_method._initial_response.http_response.request.query['readingOrder']
        result = poller.result()
        assert result

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_stream_transform_jpg(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(form, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_stream_jpg(self):
        client = get_fr_client()
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

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_multipage(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_content(invoice)
        result = poller.result()

        assert len(result) == 3
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_multipage_transform(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(form, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    def test_content_continuation_token(self, **kwargs):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        initial_poller = client.begin_recognize_content(my_file)
        cont_token = initial_poller.continuation_token()

        poller = client.begin_recognize_content(None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so devtools_testutils doesn't throw assertion error

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_multipage_table_span_transform(self):
        client = get_fr_client()
        with open(self.multipage_table_pdf, "rb") as fd:
            form = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_content_result(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        poller = client.begin_recognize_content(form, cls=callback)
        result = poller.result()
        raw_response = responses[0]
        layout = responses[1]
        page_results = raw_response.analyze_result.page_results
        read_results = raw_response.analyze_result.read_results

        # Check form pages
        self.assertFormPagesTransformCorrect(layout, read_results, page_results)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_selection_marks(self):
        client = get_fr_client()
        with open(self.selection_form_pdf, "rb") as fd:
            form = fd.read()

        poller = client.begin_recognize_content(form)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_selection_marks_v2(self):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        with open(self.selection_form_pdf, "rb") as fd:
            form = fd.read()

        poller = client.begin_recognize_content(form)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_specify_pages(self):
        client = get_fr_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            form = fd.read()

        poller = client.begin_recognize_content(form, pages=["1"])
        result = poller.result()
        assert len(result) == 1

        poller = client.begin_recognize_content(form, pages=["1", "3"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content(form, pages=["1-2"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content(form, pages=["1-2", "3"])
        result = poller.result()
        assert len(result) == 3

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_language_specified(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        poller = client.begin_recognize_content(my_file, language="de")
        assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_language_error(self):
        client = get_fr_client()
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_content(my_file, language="not a language")
        assert "NotSupportedLanguage" == e.value.error.code

    @FormRecognizerPreparer()
    def test_content_language_v2(self, **kwargs):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_content(my_file, language="en")
        assert "'language' is only available for API version V2_1 and up" in str(e.value)
