# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_content_result
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiVersion
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer


FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestContentFromUrl(FormRecognizerTest):

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_content_url_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key, **kwargs):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with pytest.raises(ClientAuthenticationError):
            poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_url_pass_stream(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with open(self.receipt_jpg, "rb") as receipt:
            with pytest.raises(HttpResponseError):
                poller = client.begin_recognize_content_from_url(receipt)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_url_transform_pdf(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
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

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_url_pdf(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.invoice_url_pdf)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)
        assert layout.tables[0].row_count == 3
        assert layout.tables[0].column_count== 5
        assert layout.tables[0].page_number == 1

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_url_transform_jpg(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
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

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_url_jpg(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.form_url_jpg)
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
    @recorded_by_proxy
    def test_content_multipage_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf)
        result = poller.result()

        assert len(result) == 3
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_multipage_transform_url(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
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

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_content_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        initial_poller = client.begin_recognize_content_from_url(self.form_url_jpg)
        cont_token = initial_poller.continuation_token()

        poller = client.begin_recognize_content_from_url(None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_multipage_table_span_pdf(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.multipage_table_url_pdf)
        result = poller.result()
        assert len(result) == 2
        layout = result[0]
        assert layout.page_number == 1
        assert len(layout.tables) == 2
        assert layout.tables[0].row_count == 29
        assert layout.tables[0].column_count== 4
        assert layout.tables[0].page_number == 1
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count== 5
        assert layout.tables[1].page_number== 1
        layout = result[1]
        assert len(layout.tables) == 1
        assert layout.page_number == 2
        assert layout.tables[0].row_count == 23
        assert layout.tables[0].column_count== 5
        assert layout.tables[0].page_number == 2
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_selection_marks(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    @recorded_by_proxy
    def test_content_selection_marks_v2(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(form_url=self.selection_mark_url_pdf)
        result = poller.result()
        assert len(result) == 1
        layout = result[0]
        assert layout.page_number == 1
        self.assertFormPagesHasValues(result)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_specify_pages(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1"])
        result = poller.result()
        assert len(result) == 1

        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1", "3"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2"])
        result = poller.result()
        assert len(result) == 2

        poller = client.begin_recognize_content_from_url(self.multipage_url_pdf, pages=["1-2", "3"])
        result = poller.result()
        assert len(result) == 3

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_reading_order(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.form_url_jpg, reading_order="natural")

        assert 'natural' == poller._polling_method._initial_response.http_response.request.query['readingOrder']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_language_specified(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_content_from_url(self.form_url_jpg, language="de")
        assert 'de' == poller._polling_method._initial_response.http_response.request.query['language']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_content_language_error(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_content_from_url(self.form_url_jpg, language="not a language")
        assert "NotSupportedLanguage" == e.value.error.code

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_content_language_v2(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            client.begin_recognize_content_from_url(self.form_url_jpg, language="en")
        assert "'language' is only available for API version V2_1 and up" in str(e.value)
