# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date
from azure.core.exceptions import ServiceRequestError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._generated.v2021_09_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormRecognizerApiVersion, DocumentAnalysisClient, AnalyzeResult
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)
DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestInvoice(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_invoice_bad_endpoint(self, formrecognizer_test_api_key):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_invoices(myfile)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_enum_content_type(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = client.begin_recognize_invoices(
            myfile,
            content_type=FormContentType.APPLICATION_PDF
        )
        result = poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_bad_content_type_param_passed(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                myfile,
                content_type="application/jpeg"
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_auto_detect_unsupported_stream_content(self, client):

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                myfile
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_stream_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_recognize_invoices(
            invoice=myfile,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
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
    @DocumentAnalysisClientPreparer()
    def test_invoice_stream_transform_tiff(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_invoice = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.invoice_tiff, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_analyze_document(
            model="prebuilt-invoice",
            document=myfile,
            cls=callback
        )

        result = poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_stream_multipage_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.multipage_vendor_pdf, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_recognize_invoices(
            invoice=myfile,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
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
    @FormRecognizerClientPreparer()
    def test_invoice_tiff(self, client):

        with open(self.invoice_tiff, "rb") as stream:
            poller = client.begin_recognize_invoices(stream)

        result = poller.result()
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
    @FormRecognizerClientPreparer()
    def test_invoice_multipage_pdf(self, client):

        with open(self.multipage_vendor_pdf, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_invoices(invoice)
        result = poller.result()

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
    @DocumentAnalysisClientPreparer()
    def test_invoice_jpg(self, client):
        with open(self.invoice_jpg, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_analyze_document("prebuilt-invoice", invoice)

        result = poller.result()
        assert len(result.documents) == 1
        invoice = result.documents[0]

        assert result.pages

        # check dict values
        self.assertEqual(invoice.fields.get("AmountDue").value, 610.0)
        self.assertEqual(invoice.fields.get("BillingAddress").value, "123 Bill St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("BillingAddressRecipient").value, "Microsoft Finance")
        self.assertEqual(invoice.fields.get("CustomerAddress").value, "123 Other St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("CustomerAddressRecipient").value, "Microsoft Corp")
        self.assertEqual(invoice.fields.get("CustomerId").value, "CID-12345")
        self.assertEqual(invoice.fields.get("CustomerName").value, "MICROSOFT CORPORATION")
        self.assertEqual(invoice.fields.get("DueDate").value, date(2019, 12, 15))
        self.assertEqual(invoice.fields.get("InvoiceDate").value, date(2019, 11, 15))
        self.assertEqual(invoice.fields.get("InvoiceId").value, "INV-100")
        self.assertEqual(invoice.fields.get("InvoiceTotal").value, 110.0)
        self.assertEqual(invoice.fields.get("PreviousUnpaidBalance").value, 500.0)
        self.assertEqual(invoice.fields.get("PurchaseOrder").value, "PO-3333")
        self.assertEqual(invoice.fields.get("RemittanceAddress").value, "123 Remit St New York, NY, 10001")
        self.assertEqual(invoice.fields.get("RemittanceAddressRecipient").value, "Contoso Billing")
        self.assertEqual(invoice.fields.get("ServiceAddress").value, "123 Service St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("ServiceAddressRecipient").value, "Microsoft Services")
        self.assertEqual(invoice.fields.get("ServiceEndDate").value, date(2019, 11, 14))
        self.assertEqual(invoice.fields.get("ServiceStartDate").value, date(2019, 10, 14))
        self.assertEqual(invoice.fields.get("ShippingAddress").value, "123 Ship St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("ShippingAddressRecipient").value, "Microsoft Delivery")
        self.assertEqual(invoice.fields.get("SubTotal").value, 100.0)
        self.assertEqual(invoice.fields.get("TotalTax").value, 10.0)
        self.assertEqual(invoice.fields.get("VendorName").value, "CONTOSO LTD.")
        self.assertEqual(invoice.fields.get("VendorAddress").value, "123 456th St New York, NY, 10001")
        self.assertEqual(invoice.fields.get("VendorAddressRecipient").value, "Contoso Headquarters")
        self.assertEqual(invoice.fields.get("Items").value[0].value["Amount"].value, 100.0)
        self.assertEqual(invoice.fields.get("Items").value[0].value["Description"].value, "Consulting service")
        self.assertEqual(invoice.fields.get("Items").value[0].value["Quantity"].value, 1.0)
        self.assertEqual(invoice.fields.get("Items").value[0].value["UnitPrice"].value, 1.0)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_jpg_include_field_elements(self, client):
        with open(self.invoice_jpg, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_invoices(invoice, include_field_elements=True)

        result = poller.result()
        self.assertEqual(len(result), 1)
        invoice = result[0]

        self.assertFormPagesHasValues(invoice.pages)

        for field in invoice.fields.values():
            if field.name == "Items":
                continue
            self.assertFieldElementsHasValues(field.value_data.field_elements, invoice.page_range.first_page_number)
        self.assertInvoiceItemsHasValues(invoice.fields["Items"].value, invoice.page_range.first_page_number, True)

        # check dict values
        self.assertEqual(invoice.fields.get("AmountDue").value, 610.0)
        self.assertEqual(invoice.fields.get("BillingAddress").value, "123 Bill St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("BillingAddressRecipient").value, "Microsoft Finance")
        self.assertEqual(invoice.fields.get("CustomerAddress").value, "123 Other St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("CustomerAddressRecipient").value, "Microsoft Corp")
        self.assertEqual(invoice.fields.get("CustomerId").value, "CID-12345")
        self.assertEqual(invoice.fields.get("CustomerName").value, "MICROSOFT CORPORATION")
        self.assertEqual(invoice.fields.get("DueDate").value, date(2019, 12, 15))
        self.assertEqual(invoice.fields.get("InvoiceDate").value, date(2019, 11, 15))
        self.assertEqual(invoice.fields.get("InvoiceId").value, "INV-100")
        self.assertEqual(invoice.fields.get("InvoiceTotal").value, 110.0)
        self.assertEqual(invoice.fields.get("PreviousUnpaidBalance").value, 500.0)
        self.assertEqual(invoice.fields.get("PurchaseOrder").value, "PO-3333")
        self.assertEqual(invoice.fields.get("RemittanceAddress").value, "123 Remit St New York, NY, 10001")
        self.assertEqual(invoice.fields.get("RemittanceAddressRecipient").value, "Contoso Billing")
        self.assertEqual(invoice.fields.get("ServiceAddress").value, "123 Service St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("ServiceAddressRecipient").value, "Microsoft Services")
        self.assertEqual(invoice.fields.get("ServiceEndDate").value, date(2019, 11, 14))
        self.assertEqual(invoice.fields.get("ServiceStartDate").value, date(2019, 10, 14))
        self.assertEqual(invoice.fields.get("ShippingAddress").value, "123 Ship St, Redmond WA, 98052")
        self.assertEqual(invoice.fields.get("ShippingAddressRecipient").value, "Microsoft Delivery")
        self.assertEqual(invoice.fields.get("SubTotal").value, 100.0)
        self.assertEqual(invoice.fields.get("TotalTax").value, 10.0)
        self.assertEqual(invoice.fields.get("VendorName").value, "CONTOSO LTD.")
        self.assertEqual(invoice.fields.get("VendorAddress").value, "123 456th St New York, NY, 10001")
        self.assertEqual(invoice.fields.get("VendorAddressRecipient").value, "Contoso Headquarters")
        self.assertEqual(invoice.fields.get("Items").value[0].value["Amount"].value, 100.0)
        self.assertEqual(invoice.fields.get("Items").value[0].value["Description"].value, "Consulting service")
        self.assertEqual(invoice.fields.get("Items").value[0].value["Quantity"].value, 1.0)
        self.assertEqual(invoice.fields.get("Items").value[0].value["UnitPrice"].value, 1.0)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_continuation_token(self, client):

        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()

        initial_poller = client.begin_recognize_invoices(invoice)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_invoices(None, continuation_token=cont_token)
        result = poller.result()
        assert result is not None
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_invoice_v2(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_invoices(invoice)
        assert "Method 'begin_recognize_invoices' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_locale_specified(self, client):
        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_invoices(invoice, locale="en-US")
        assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_invoice_locale_error(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_invoices(invoice, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_pages_kwarg_specified(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()

        poller = client.begin_recognize_invoices(invoice, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
