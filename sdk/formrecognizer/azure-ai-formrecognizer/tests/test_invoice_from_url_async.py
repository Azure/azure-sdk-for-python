# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date, time
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from azure.ai.formrecognizer.aio import FormRecognizerClient
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


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
    @GlobalClientPreparer()
    async def test_invoice_encoded_url(self, client):
        async with client:
            try:
                poller = await client.begin_recognize_invoices_from_url("https://fakeuri.com/blank%20space")
            except HttpResponseError as e:
                self.assertIn("https://fakeuri.com/blank%20space", e.response.request.body)

    @FormRecognizerPreparer()
    async def test_invoice_url_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf)

    @FormRecognizerPreparer()
    async def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_invoices_from_url("https://badurl.jpg")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_url_pass_stream(self, client):
        with open(self.invoice_tiff, "rb") as invoice:
            with self.assertRaises(HttpResponseError):
                async with client:
                    poller = await client.begin_recognize_invoices_from_url(invoice)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_url_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        async with client:
            poller = await client.begin_recognize_invoices_from_url(
                invoice_url=self.invoice_url_pdf,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        invoice = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertFormFieldsTransformCorrect(invoice.fields, actual, read_results)

        # check page range
        self.assertEqual(invoice.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(invoice.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(invoice.pages, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_url_transform_tiff(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        async with client:
            poller = await client.begin_recognize_invoices_from_url(
                invoice_url=self.invoice_url_tiff,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        invoice = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertFormFieldsTransformCorrect(invoice.fields, actual, read_results)

        # check page range
        self.assertEqual(invoice.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(invoice.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(invoice.pages, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
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
    @GlobalClientPreparer()
    async def test_invoice_tiff(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        invoice = result[0]

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
    @GlobalClientPreparer()
    async def test_invoice_multipage_pdf(self, client):

        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.multipage_vendor_url_pdf)
            result = await poller.result()

        self.assertEqual(len(result), 1)
        invoice = result[0]
        self.assertEqual("prebuilt:invoice", invoice.form_type)
        self.assertEqual(1, invoice.page_range.first_page_number)
        self.assertEqual(2, invoice.page_range.last_page_number)

        vendor_name = invoice.fields["VendorName"]
        self.assertEqual(vendor_name.value, 'Southridge Video')
        self.assertEqual(vendor_name.value_data.page_number, 2)

        remittance_address_recipient = invoice.fields["RemittanceAddressRecipient"]
        self.assertEqual(remittance_address_recipient.value, "Contoso Ltd.")
        self.assertEqual(remittance_address_recipient.value_data.page_number, 1)

        remittance_address = invoice.fields["RemittanceAddress"]
        self.assertEqual(remittance_address.value, '2345 Dogwood Lane Birch, Kansas 98123')
        self.assertEqual(remittance_address.value_data.page_number, 1)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_pdf_include_field_elements(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, include_field_elements=True)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        invoice = result[0]

        self.assertFormPagesHasValues(invoice.pages)

        for field in invoice.fields.values():
            if field.name == "Items":
                continue
            self.assertFieldElementsHasValues(field.value_data.field_elements, invoice.page_range.first_page_number)
        self.assertInvoiceItemsHasValues(invoice.fields["Items"].value, invoice.page_range.first_page_number, True)

        # check dict values
        self.assertEqual(invoice.fields.get("VendorName").value, "Contoso")
        self.assertEqual(invoice.fields.get("VendorAddress").value, '1 Redmond way Suite 6000 Redmond, WA 99243')
        self.assertEqual(invoice.fields.get("CustomerAddressRecipient").value, "Microsoft")
        self.assertEqual(invoice.fields.get("CustomerAddress").value, '1020 Enterprise Way Sunnayvale, CA 87659')
        self.assertEqual(invoice.fields.get("CustomerName").value, "Microsoft")
        self.assertEqual(invoice.fields.get("InvoiceId").value, '34278587')
        self.assertEqual(invoice.fields.get("InvoiceDate").value, date(2017, 6, 18))
        self.assertEqual(invoice.fields.get("InvoiceTotal").value, 56651.49)
        self.assertEqual(invoice.fields.get("DueDate").value, date(2017, 6, 24))

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
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
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_invoice_v2(self, client):
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_tiff)
        assert "Method 'begin_recognize_invoices_from_url' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_locale_specified(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="en-US")
            assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_invoice_locale_error(self, client):
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_pages_kwarg_specified(self, client):
        async with client:
            poller = await client.begin_recognize_invoices_from_url(self.invoice_url_pdf, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
