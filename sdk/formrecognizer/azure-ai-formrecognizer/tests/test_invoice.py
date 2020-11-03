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
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormRecognizerApiVersion
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestInvoice(FormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    def test_invoice_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            poller = client.begin_recognize_invoices(myfile)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_authentication_successful_key(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = client.begin_recognize_invoices(myfile)
        result = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_invoices(b"xx", content_type="image/jpeg")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_passing_enum_content_type(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        poller = client.begin_recognize_invoices(
            myfile,
            content_type=FormContentType.APPLICATION_PDF
        )
        result = poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_damaged_file_passed_as_bytes_io(self, client):
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                damaged_pdf
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_blank_page(self, client):

        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        poller = client.begin_recognize_invoices(
            blank
        )
        result = poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_passing_bad_content_type_param_passed(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                myfile,
                content_type="application/jpeg"
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_passing_unsupported_url_content_type(self, client):
        with self.assertRaises(TypeError):
            poller = client.begin_recognize_invoices("https://badurl.jpg", content_type="application/json")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_auto_detect_unsupported_stream_content(self, client):

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_invoices(
                myfile
            )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
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

        self.assertInvoiceTransformCorrect(invoice, actual, read_results)

        # check page range
        self.assertEqual(invoice.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(invoice.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(invoice.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_invoice_stream_transform_tiff(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_invoice = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_invoice)

        with open(self.invoice_tiff, "rb") as fd:
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

        self.assertInvoiceTransformCorrect(invoice, actual, read_results)

        # check page range
        self.assertEqual(invoice.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(invoice.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(invoice.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_invoice_pdf(self, client):

        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()

        poller = client.begin_recognize_invoices(invoice)

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
        self.assertEqual(invoice.fields.get("InvoiceTotal").value, 56651.49)
        self.assertEqual(invoice.fields.get("DueDate").value, date(2017, 6, 24))

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
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
        self.assertEqual(invoice.fields.get("InvoiceTotal").value, 56651.49)
        self.assertEqual(invoice.fields.get("DueDate").value, date(2017, 6, 24))

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_invoice_pdf_include_field_elements(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_invoices(invoice, include_field_elements=True)

        result = poller.result()
        self.assertEqual(len(result), 1)
        invoice = result[0]

        self.assertFormPagesHasValues(invoice.pages)

        for field in invoice.fields.values():
            self.assertFieldElementsHasValues(field.value_data.field_elements, invoice.page_range.first_page_number)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_invoice_continuation_token(self, client):

        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()

        initial_poller = client.begin_recognize_invoices(invoice)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_invoices(invoice, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_invoice_v2(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_invoices(invoice)
        assert "Method 'begin_recognize_invoices' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_invoice_locale_specified(self, client):
        with open(self.invoice_tiff, "rb") as fd:
            invoice = fd.read()
        poller = client.begin_recognize_invoices(invoice, locale="en-US")
        assert 'en-US' == poller._polling_method._initial_response.http_response.request.query['locale']
        poller.wait()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    def test_invoice_locale_error(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            invoice = fd.read()
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_invoices(invoice, locale="not a locale")
        assert "locale" in e.value.error.message
