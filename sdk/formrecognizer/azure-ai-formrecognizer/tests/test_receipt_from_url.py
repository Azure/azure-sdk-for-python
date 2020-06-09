# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from datetime import date, time
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_receipt
from azure.ai.formrecognizer import FormRecognizerClient
from testcase import FormRecognizerTest, GlobalFormRecognizerAccountPreparer


class TestReceiptFromUrl(FormRecognizerTest):

    @pytest.mark.live_test_only
    def test_active_directory_auth(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = FormRecognizerClient(endpoint, token)
        poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)
        result = poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_auth_successful_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)
        result = poller.result()

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_auth_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_bad_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_receipts_from_url("https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_pass_stream(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_png, "rb") as receipt:
            with self.assertRaises(HttpResponseError):
                poller = client.begin_recognize_receipts_from_url(receipt)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_transform_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        poller = client.begin_recognize_receipts_from_url(
            receipt_url=self.receipt_url_jpg,
            include_text_content=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        receipt = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        # check dict values
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantAddress"), actual.get("MerchantAddress"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantName"), actual.get("MerchantName"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantPhoneNumber"), actual.get("MerchantPhoneNumber"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Subtotal"), actual.get("Subtotal"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Tax"), actual.get("Tax"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Tip"), actual.get("Tip"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Total"), actual.get("Total"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionDate"), actual.get("TransactionDate"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionTime"), actual.get("TransactionTime"), read_results)

        # check page range
        self.assertEqual(receipt.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(receipt.page_range.last_page_number, document_results[0].page_range[1])

        # check receipt type
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertEqual(receipt_type.confidence, actual["ReceiptType"].confidence)
        self.assertEqual(receipt_type.value, actual["ReceiptType"].value_string)

        # check receipt items
        self.assertReceiptItemsTransformCorrect(receipt.fields["Items"].value, actual["Items"], read_results)

        # Check page metadata
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_transform_png(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        poller = client.begin_recognize_receipts_from_url(
            receipt_url=self.receipt_url_png,
            include_text_content=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        receipt = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        # check dict values
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantAddress"), actual.get("MerchantAddress"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantName"), actual.get("MerchantName"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantPhoneNumber"), actual.get("MerchantPhoneNumber"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Subtotal"), actual.get("Subtotal"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Tax"), actual.get("Tax"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Tip"), actual.get("Tip"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("Total"), actual.get("Total"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionDate"), actual.get("TransactionDate"), read_results)
        self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionTime"), actual.get("TransactionTime"), read_results)

        # check page range
        self.assertEqual(receipt.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(receipt.page_range.last_page_number, document_results[0].page_range[1])

        # check receipt type
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertEqual(receipt_type.confidence, actual["ReceiptType"].confidence)
        self.assertEqual(receipt_type.value, actual["ReceiptType"].value_string)

        # check receipt items
        self.assertReceiptItemsTransformCorrect(receipt.fields["Items"].value, actual["Items"], read_results)

        # Check page metadata
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_include_text_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        poller = client.begin_recognize_receipts_from_url(
            self.receipt_url_jpg,
            include_text_content=True
        )

        result = poller.result()
        self.assertEqual(len(result), 1)
        receipt = result[0]

        self.assertFormPagesHasValues(receipt.pages)
        for field, value in receipt.__dict__.items():
            if field not in ["receipt_items", "page_range", "pages", "fields", "form_type"]:
                field = getattr(receipt, field)
                self.assertTextContentHasValues(field.value_data.text_content, receipt.page_range.first_page_number)

        for field, value in receipt.fields.items():
            self.assertTextContentHasValues(value.value_data.text_content, receipt.page_range.first_page_number)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)

        result = poller.result()
        self.assertEqual(len(result), 1)
        receipt = result[0]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso Contoso')
        self.assertEqual(receipt.fields.get("MerchantPhoneNumber").value, '+19876543210')
        self.assertEqual(receipt.fields.get("Subtotal").value, 11.7)
        self.assertEqual(receipt.fields.get("Tax").value, 1.17)
        self.assertEqual(receipt.fields.get("Tip").value, 1.63)
        self.assertEqual(receipt.fields.get("Total").value, 14.5)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        self.assertEqual(receipt.page_range.first_page_number, 1)
        self.assertEqual(receipt.page_range.last_page_number, 1)
        self.assertFormPagesHasValues(receipt.pages)
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')
        self.assertReceiptItemsHasValues(receipt.fields["Items"].value, receipt.page_range.first_page_number, False)

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_url_png(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        poller = client.begin_recognize_receipts_from_url(self.receipt_url_png)

        result = poller.result()
        self.assertEqual(len(result), 1)
        receipt = result[0]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso Contoso')
        self.assertEqual(receipt.fields.get("Subtotal").value, 1098.99)
        self.assertEqual(receipt.fields.get("Tax").value, 104.4)
        self.assertEqual(receipt.fields.get("Total").value, 1203.39)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        self.assertEqual(receipt.page_range.first_page_number, 1)
        self.assertEqual(receipt.page_range.last_page_number, 1)
        self.assertFormPagesHasValues(receipt.pages)
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_multipage_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        poller = client.begin_recognize_receipts_from_url(self.multipage_url_pdf, include_text_content=True)
        result = poller.result()

        self.assertEqual(len(result), 3)
        receipt = result[0]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Hobbit Lane 567 Main St. Redmond, WA Redmond, WA')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Bilbo Baggins')
        self.assertEqual(receipt.fields.get("MerchantPhoneNumber").value, '+15555555555')
        self.assertEqual(receipt.fields.get("Subtotal").value, 300.0)
        self.assertEqual(receipt.fields.get("Total").value, 100.0)
        self.assertEqual(receipt.page_range.first_page_number, 1)
        self.assertEqual(receipt.page_range.last_page_number, 1)
        self.assertFormPagesHasValues(receipt.pages)
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')
        receipt = result[2]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Hobbit Lane 567 Main St. Redmond, WA Redmond, WA')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Frodo Baggins')
        self.assertEqual(receipt.fields.get("MerchantPhoneNumber").value, '+15555555555')
        self.assertEqual(receipt.fields.get("Subtotal").value, 3000.0)
        self.assertEqual(receipt.fields.get("Total").value, 1000.0)
        self.assertEqual(receipt.page_range.first_page_number, 3)
        self.assertEqual(receipt.page_range.last_page_number, 3)
        self.assertFormPagesHasValues(receipt.pages)
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')

    @GlobalFormRecognizerAccountPreparer()
    def test_receipt_multipage_transform_url(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        poller = client.begin_recognize_receipts_from_url(
            self.multipage_url_pdf,
            include_text_content=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        actual = raw_response.analyze_result.document_results
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        # check hardcoded values
        for receipt, actual in zip(returned_model, actual):
            if actual.fields is None:  # second page is blank
                continue

            # check dict values
            self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantAddress"), actual.fields.get("MerchantAddress"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantName"), actual.fields.get("MerchantName"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("MerchantPhoneNumber"), actual.fields.get("MerchantPhoneNumber"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("Subtotal"), actual.fields.get("Subtotal"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("Tax"), actual.fields.get("Tax"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("Tip"), actual.fields.get("Tip"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("Total"), actual.fields.get("Total"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionDate"), actual.fields.get("TransactionDate"), read_results)
            self.assertFormFieldTransformCorrect(receipt.fields.get("TransactionTime"), actual.fields.get("TransactionTime"), read_results)

            # check page range
            self.assertEqual(receipt.page_range.first_page_number, actual.page_range[0])
            self.assertEqual(receipt.page_range.last_page_number, actual.page_range[1])

            # check receipt type
            receipt_type = receipt.fields.get("ReceiptType")
            self.assertEqual(receipt_type.confidence, actual.fields["ReceiptType"].confidence)
            self.assertEqual(receipt_type.value, actual.fields["ReceiptType"].value_string)

            # check receipt items
            self.assertReceiptItemsTransformCorrect(receipt.fields["Items"].value, actual.fields["Items"], read_results)

        # Check form pages
        self.assertFormPagesTransformCorrect(returned_model, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @pytest.mark.live_test_only
    def test_receipt_continuation_token(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        initial_poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_receipts_from_url(self.receipt_url_jpg, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error
