# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import ServiceRequestError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer


FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestInvoiceAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @pytest.mark.skip()
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_invoice_bad_endpoint(self, **kwargs):
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_invoices(my_file)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_enum_content_type(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_recognize_invoices(
                my_file,
                content_type=FormContentType.APPLICATION_PDF
            )
            result = await poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, **kwargs):
        client = kwargs.pop("client")
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_invoices(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, **kwargs):
        client = kwargs.pop("client")
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_invoices(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_invoices(
                    my_file,
                    content_type="application/jpeg"
                )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_auto_detect_unsupported_stream_content(self, **kwargs):
        client = kwargs.pop("client")

        with open(self.unsupported_content_py, "rb") as fd:
            my_file = fd.read()

        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_invoices(
                    my_file
                )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_stream_transform_pdf(self, **kwargs):
        client = kwargs.pop("client")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.invoice_pdf, "rb") as fd:
            my_file = fd.read()

        async with client:
            poller = await client.begin_recognize_invoices(
                invoice=my_file,
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
        assert invoice.page_range.first_page_number ==  document_results[0].page_range[0]
        assert invoice.page_range.last_page_number ==  document_results[0].page_range[1]

        # Check page metadata
        self.assertFormPagesTransformCorrect(invoice.pages, read_results, page_results)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_stream_multipage_transform_pdf(self, **kwargs):
        client = kwargs.pop("client")
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            my_file = fd.read()

        async with client:
            poller = await client.begin_recognize_invoices(
                invoice=my_file,
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

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_tiff(self, **kwargs):
        client = kwargs.pop("client")

        with open(self.invoice_tiff, "rb") as fd:
            stream = fd.read()

        async with client:
            poller = await client.begin_recognize_invoices(stream)
            result = await poller.result()
        assert len(result) == 1
        invoice = result[0]
        # check dict values

        assert invoice.fields.get("VendorName").value ==  "Contoso"
        assert invoice.fields.get("VendorAddress").value, '1 Redmond way Suite 6000 Redmond ==  WA 99243'
        assert invoice.fields.get("CustomerAddressRecipient").value ==  "Microsoft"
        assert invoice.fields.get("CustomerAddress").value, '1020 Enterprise Way Sunnayvale ==  CA 87659'
        assert invoice.fields.get("CustomerName").value ==  "Microsoft"
        assert invoice.fields.get("InvoiceId").value ==  '34278587'
        assert invoice.fields.get("InvoiceDate").value, date(2017, 6 ==  18)
        assert invoice.fields.get("Items").value[0].value["Amount"].value ==  56651.49
        assert invoice.fields.get("DueDate").value, date(2017, 6 ==  24)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_multipage_pdf(self, **kwargs):
        client = kwargs.pop("client")

        with open(self.multipage_vendor_pdf, "rb") as fd:
            invoice = fd.read()

        async with client:
            poller = await client.begin_recognize_invoices(invoice)
            result = await poller.result()

        assert len(result) == 1
        invoice = result[0]
        assert "prebuilt:invoice" ==  invoice.form_type
        assert 1 ==  invoice.page_range.first_page_number
        assert 2 ==  invoice.page_range.last_page_number

        vendor_name = invoice.fields["VendorName"]
        assert vendor_name.value ==  'Southridge Video'
        assert vendor_name.value_data.page_number ==  2

        remittance_address_recipient = invoice.fields["RemittanceAddressRecipient"]
        assert remittance_address_recipient.value ==  "Contoso Ltd."
        assert remittance_address_recipient.value_data.page_number ==  1

        remittance_address = invoice.fields["RemittanceAddress"]
        assert remittance_address.value, '2345 Dogwood Lane Birch ==  Kansas 98123'
        assert remittance_address.value_data.page_number ==  1

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_jpg_include_field_elements(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_jpg, "rb") as fd:
            invoice = fd.read()

        async with client:
            poller = await client.begin_recognize_invoices(invoice, include_field_elements=True)

            result = await poller.result()
        assert len(result) == 1
        invoice = result[0]

        self.assertFormPagesHasValues(invoice.pages)

        for field in invoice.fields.values():
            if field.name == "Items":
                continue
            self.assertFieldElementsHasValues(field.value_data.field_elements, invoice.page_range.first_page_number)
        self.assertInvoiceItemsHasValues(invoice.fields["Items"].value, invoice.page_range.first_page_number, True)

        assert invoice.fields.get("AmountDue").value ==  610.0
        assert invoice.fields.get("BillingAddress").value, "123 Bill St, Redmond WA ==  98052"
        assert invoice.fields.get("BillingAddressRecipient").value ==  "Microsoft Finance"
        assert invoice.fields.get("CustomerAddress").value, "123 Other St, Redmond WA ==  98052"
        assert invoice.fields.get("CustomerAddressRecipient").value ==  "Microsoft Corp"
        assert invoice.fields.get("CustomerId").value ==  "CID-12345"
        assert invoice.fields.get("CustomerName").value ==  "MICROSOFT CORPORATION"
        assert invoice.fields.get("DueDate").value, date(2019, 12 ==  15)
        assert invoice.fields.get("InvoiceDate").value, date(2019, 11 ==  15)
        assert invoice.fields.get("InvoiceId").value ==  "INV-100"
        assert invoice.fields.get("InvoiceTotal").value ==  110.0
        assert invoice.fields.get("PreviousUnpaidBalance").value ==  500.0
        assert invoice.fields.get("PurchaseOrder").value ==  "PO-3333"
        assert invoice.fields.get("RemittanceAddress").value, "123 Remit St New York, NY ==  10001"
        assert invoice.fields.get("RemittanceAddressRecipient").value ==  "Contoso Billing"
        assert invoice.fields.get("ServiceAddress").value, "123 Service St, Redmond WA ==  98052"
        assert invoice.fields.get("ServiceAddressRecipient").value ==  "Microsoft Services"
        assert invoice.fields.get("ServiceEndDate").value, date(2019, 11 ==  14)
        assert invoice.fields.get("ServiceStartDate").value, date(2019, 10 ==  14)
        assert invoice.fields.get("ShippingAddress").value, "123 Ship St, Redmond WA ==  98052"
        assert invoice.fields.get("ShippingAddressRecipient").value ==  "Microsoft Delivery"
        assert invoice.fields.get("SubTotal").value ==  100.0
        assert invoice.fields.get("TotalTax").value ==  10.0
        assert invoice.fields.get("VendorName").value ==  "CONTOSO LTD."
        assert invoice.fields.get("VendorAddress").value, "123 456th St New York, NY ==  10001"
        assert invoice.fields.get("VendorAddressRecipient").value ==  "Contoso Headquarters"
        assert invoice.fields.get("Items").value[0].value["Amount"].value ==  100.0
        assert invoice.fields.get("Items").value[0].value["Description"].value ==  "Consulting service"
        assert invoice.fields.get("Items").value[0].value["Quantity"].value ==  1.0
        assert invoice.fields.get("Items").value[0].value["UnitPrice"].value ==  1.0

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_invoice_continuation_token(self, **kwargs):
        client = kwargs.pop("client")

        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()
        async with client:
            initial_poller = await client.begin_recognize_invoices(invoice)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_invoices(None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_invoice_v2(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_invoices(invoice)
        assert "Method 'begin_recognize_invoices' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_locale_specified(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()
        async with client:
            poller = await client.begin_recognize_invoices(invoice, locale="en-US")
            assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_invoice_locale_error(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_recognize_invoices(invoice, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        async with client:
            poller = await client.begin_recognize_invoices(invoice, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
