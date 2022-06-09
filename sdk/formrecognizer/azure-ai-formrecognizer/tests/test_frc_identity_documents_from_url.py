# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiVersion
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestIdDocumentsFromUrl(FormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_polling_interval(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        assert client._client._config.polling_interval ==  7

        poller = client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, polling_interval=6)
        poller.wait()
        assert poller._polling_method._timeout ==  6
        poller2 = client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
        poller2.wait()
        assert poller2._polling_method._timeout ==  7  # goes back to client default

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_identity_document_url_transform_jpg(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        poller = client.begin_recognize_identity_documents_from_url(
            identity_document_url=self.identity_document_url_jpg,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        id_document = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertFormFieldsTransformCorrect(id_document.fields, actual, read_results)

        # check page range
        assert id_document.page_range.first_page_number ==  document_results[0].page_range[0]
        assert id_document.page_range.last_page_number ==  document_results[0].page_range[1]

        # Check page metadata
        self.assertFormPagesTransformCorrect(id_document.pages, read_results, page_results)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_identity_document_jpg_include_field_elements(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, include_field_elements=True)

        result = poller.result()
        assert len(result) == 1
        id_document = result[0]

        self.assertFormPagesHasValues(id_document.pages)

        for field in id_document.fields.values():
            if field.name == "CountryRegion":
                assert field.value ==  "USA"
                continue
            elif field.name == "Region":
                assert field.value ==  "Washington"
            else:
                self.assertFieldElementsHasValues(field.value_data.field_elements, id_document.page_range.first_page_number)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_identity_document_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        initial_poller = client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_identity_documents_from_url(None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_identity_document_v2(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
        assert "Method 'begin_recognize_identity_documents_from_url' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_pages_kwarg_specified(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        poller = client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
