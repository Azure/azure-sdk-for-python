# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerApiVersion
from azure.ai.formrecognizer.aio import FormRecognizerClient, DocumentAnalysisClient
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer


FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestInvoiceFromUrlAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, polling_interval=6)
            await poller.wait()
            self.assertEqual(poller._polling_method._timeout, 6)
            poller2 = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf)
            await poller2.wait()
            self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_invoices_from_url("https://badurl.jpg")

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_url_multipage_transform_pdf(self, client):
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

        self.assertEqual(1, len(returned_models))
        returned_model = returned_models[0]
        self.assertEqual(2, len(returned_model.pages))
        self.assertEqual(1, returned_model.page_range.first_page_number)
        self.assertEqual(2, returned_model.page_range.last_page_number)

        self.assertEqual(1, len(document_results))
        document_result = document_results[0]
        self.assertEqual(1, document_result.page_range[0])  # checking first page number
        self.assertEqual(2, document_result.page_range[1])  # checking last page number

        for invoice, document_result in zip(returned_models, document_results):
            self.assertFormFieldsTransformCorrect(invoice.fields, document_result.fields, read_results)

        self.assertFormPagesTransformCorrect(returned_model.pages, read_results, page_results)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    async def test_invoice_tiff(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url(model="prebuilt-invoice", document_url=self.invoice_url_tiff)

            result = await poller.result()
        assert len(result.documents) == 1
        invoice = result.documents[0]

        # check dict values
        self.assertEqual(invoice.fields.get("VendorName").value, "Contoso")
        self.assertEqual(invoice.fields.get("VendorAddress").value, '1 Redmond way Suite 6000 Redmond, WA 99243')
        self.assertEqual(invoice.fields.get("CustomerAddressRecipient").value, "Microsoft")
        self.assertEqual(invoice.fields.get("CustomerAddress").value, '1020 Enterprise Way Sunnayvale, CA 87659')
        self.assertEqual(invoice.fields.get("CustomerName").value, "Microsoft")
        self.assertEqual(invoice.fields.get("InvoiceId").value, '34278587')
        self.assertEqual(invoice.fields.get("InvoiceDate").value, date(2017, 6, 18))
        self.assertEqual(invoice.fields.get("Items").value[0].value["Amount"].value, 56651.49)
        self.assertEqual(invoice.fields.get("DueDate").value, date(2017, 6, 24))

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @pytest.mark.live_test_only
    async def test_invoice_continuation_token(self, client):
        async with client:
            initial_poller = await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_invoices_from_url(None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_invoice_v2(self, client):
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)
        assert "Method 'begin_recognize_invoices_from_url' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_locale_specified(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="en-US")
            assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_locale_error(self, client):
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_pages_kwarg_specified(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
