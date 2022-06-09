# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerApiVersion
from azure.ai.formrecognizer.aio import FormRecognizerClient
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer


FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestInvoiceFromUrlAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_polling_interval(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        assert client._client._config.polling_interval ==  7

        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, polling_interval=6)
            await poller.wait()
            assert poller._polling_method._timeout ==  6
            poller2 = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf)
            await poller2.wait()
            assert poller2._polling_method._timeout ==  7  # goes back to client default

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_bad_url(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_invoices_from_url("https://badurl.jpg")

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_url_multipage_transform_pdf(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        async with client:
            poller = await client.begin_recognize_invoices_from_url(
                invoice_url=self.multipage_vendor_url_pdf,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
        raw_response = responses[0]
        returned_models = responses[1]
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        assert 1 ==  len(returned_models)
        returned_model = returned_models[0]
        assert 2 ==  len(returned_model.pages)
        assert 1 ==  returned_model.page_range.first_page_number
        assert 2 ==  returned_model.page_range.last_page_number

        assert 1 ==  len(document_results)
        document_result = document_results[0]
        assert 1 ==  document_result.page_range[0]  # checking first page number
        assert 2 ==  document_result.page_range[1]  # checking last page number

        for invoice, document_result in zip(returned_models, document_results):
            self.assertFormFieldsTransformCorrect(invoice.fields, document_result.fields, read_results)

        self.assertFormPagesTransformCorrect(returned_model.pages, read_results, page_results)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_continuation_token(self, **kwargs):
        client = kwargs.pop("client")
        async with client:
            initial_poller = await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_invoices_from_url(None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_invoice_v2(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)
        assert "Method 'begin_recognize_invoices_from_url' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_locale_specified(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="en-US")
            assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_locale_error(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, **kwargs):
        client = kwargs.pop("client")
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
