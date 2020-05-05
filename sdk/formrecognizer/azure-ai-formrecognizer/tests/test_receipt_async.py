# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from io import BytesIO
from datetime import date, time
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_us_receipt
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest


class TestReceiptFromStreamAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.receipt_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            result = await client.recognize_receipts(myfile)

    @GlobalFormRecognizerAccountPreparer()
    async def test_authentication_successful_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_jpg, "rb") as fd:
            myfile = fd.read()
        result = await client.recognize_receipts(myfile)

    @GlobalFormRecognizerAccountPreparer()
    async def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            result = await client.recognize_receipts(b"xx", content_type="image/jpeg")

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_enum_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_png, "rb") as fd:
            myfile = fd.read()
        result = await client.recognize_receipts(
            myfile,
            content_type=FormContentType.image_png
        )
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_passed_as_bytes(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = await client.recognize_receipts(
                damaged_pdf,
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = await client.recognize_receipts(
                damaged_pdf,
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_passed_as_bytes_io(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            poller = await client.recognize_receipts(
                damaged_pdf,
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = await client.recognize_receipts(
                damaged_pdf,
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_blank_page(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        result = await client.recognize_receipts(
            blank,
        )
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_bad_content_type_param_passed(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            result = await client.recognize_receipts(
                myfile,
                content_type="application/jpeg"
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_passing_unsupported_url_content_type(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with self.assertRaises(TypeError):
            result = await client.recognize_receipts("https://badurl.jpg", content_type="application/json")

    @GlobalFormRecognizerAccountPreparer()
    async def test_auto_detect_unsupported_stream_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            result = await client.recognize_receipts(
                myfile,
            )

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_stream_transform_png(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_us_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.receipt_png, "rb") as fd:
            myfile = fd.read()

        result = await client.recognize_receipts(
            stream=myfile,
            include_text_content=True,
            cls=callback
        )

        raw_response = responses[0]
        returned_model = responses[1]
        receipt = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        # check hardcoded values
        self.assertFormFieldTransformCorrect(receipt.merchant_address, actual.get("MerchantAddress"), read_results)
        self.assertFormFieldTransformCorrect(receipt.merchant_name, actual.get("MerchantName"), read_results)
        self.assertFormFieldTransformCorrect(receipt.merchant_phone_number, actual.get("MerchantPhoneNumber"), read_results)
        self.assertFormFieldTransformCorrect(receipt.subtotal, actual.get("Subtotal"), read_results)
        self.assertFormFieldTransformCorrect(receipt.tax, actual.get("Tax"), read_results)
        self.assertFormFieldTransformCorrect(receipt.tip, actual.get("Tip"), read_results)
        self.assertFormFieldTransformCorrect(receipt.total, actual.get("Total"), read_results)
        self.assertFormFieldTransformCorrect(receipt.transaction_date, actual.get("TransactionDate"), read_results)
        self.assertFormFieldTransformCorrect(receipt.transaction_time, actual.get("TransactionTime"), read_results)

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
        self.assertEqual(receipt.page_range.first_page, document_results[0].page_range[0])
        self.assertEqual(receipt.page_range.last_page, document_results[0].page_range[1])

        # check receipt type
        self.assertEqual(receipt.receipt_type.confidence, actual["ReceiptType"].confidence)
        self.assertEqual(receipt.receipt_type.type, actual["ReceiptType"].value_string)

        # check receipt items
        self.assertReceiptItemsTransformCorrect(receipt.receipt_items, actual["Items"], read_results)

        # Check page metadata
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_stream_transform_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_us_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.receipt_jpg, "rb") as fd:
            myfile = fd.read()

        result = await client.recognize_receipts(
            stream=myfile,
            include_text_content=True,
            cls=callback
        )

        raw_response = responses[0]
        returned_model = responses[1]
        receipt = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        # check hardcoded values
        self.assertFormFieldTransformCorrect(receipt.merchant_address, actual.get("MerchantAddress"), read_results)
        self.assertFormFieldTransformCorrect(receipt.merchant_name, actual.get("MerchantName"), read_results)
        self.assertFormFieldTransformCorrect(receipt.merchant_phone_number, actual.get("MerchantPhoneNumber"), read_results)
        self.assertFormFieldTransformCorrect(receipt.subtotal, actual.get("Subtotal"), read_results)
        self.assertFormFieldTransformCorrect(receipt.tax, actual.get("Tax"), read_results)
        self.assertFormFieldTransformCorrect(receipt.tip, actual.get("Tip"), read_results)
        self.assertFormFieldTransformCorrect(receipt.total, actual.get("Total"), read_results)
        self.assertFormFieldTransformCorrect(receipt.transaction_date, actual.get("TransactionDate"), read_results)
        self.assertFormFieldTransformCorrect(receipt.transaction_time, actual.get("TransactionTime"), read_results)

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
        self.assertEqual(receipt.page_range.first_page, document_results[0].page_range[0])
        self.assertEqual(receipt.page_range.last_page, document_results[0].page_range[1])

        # check receipt type
        self.assertEqual(receipt.receipt_type.confidence, actual["ReceiptType"].confidence)
        self.assertEqual(receipt.receipt_type.type, actual["ReceiptType"].value_string)

        # check receipt items
        self.assertReceiptItemsTransformCorrect(receipt.receipt_items, actual["Items"], read_results)

        # Check form pages
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_jpg(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()

        result = await client.recognize_receipts(receipt)

        self.assertEqual(len(result), 1)
        receipt = result[0]
        self.assertEqual(receipt.merchant_address.value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.merchant_name.value, 'Contoso Contoso')
        self.assertEqual(receipt.merchant_phone_number.value, '+19876543210')
        self.assertEqual(receipt.subtotal.value, 11.7)
        self.assertEqual(receipt.tax.value, 1.17)
        self.assertEqual(receipt.tip.value, 1.63)
        self.assertEqual(receipt.total.value, 14.5)
        self.assertEqual(receipt.transaction_date.value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.transaction_time.value, time(hour=13, minute=59, second=0))
        self.assertEqual(receipt.page_range.first_page, 1)
        self.assertEqual(receipt.page_range.last_page, 1)
        self.assertFormPagesHasValues(receipt.pages)
        self.assertIsNotNone(receipt.receipt_type.confidence)
        self.assertEqual(receipt.receipt_type.type, 'Itemized')
        self.assertReceiptItemsHasValues(receipt.receipt_items, receipt.page_range.first_page, False)

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_png(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        with open(self.receipt_png, "rb") as fd:
            receipt = fd.read()

        result = await client.recognize_receipts(receipt)
        self.assertEqual(len(result), 1)
        receipt = result[0]
        self.assertEqual(receipt.merchant_address.value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.merchant_name.value, 'Contoso Contoso')
        self.assertEqual(receipt.subtotal.value, 1098.99)
        self.assertEqual(receipt.tax.value, 104.4)
        self.assertEqual(receipt.total.value, 1203.39)
        self.assertEqual(receipt.transaction_date.value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.transaction_time.value, time(hour=13, minute=59, second=0))
        self.assertEqual(receipt.page_range.first_page, 1)
        self.assertEqual(receipt.page_range.last_page, 1)
        self.assertFormPagesHasValues(receipt.pages)
        self.assertIsNotNone(receipt.receipt_type.confidence)
        self.assertEqual(receipt.receipt_type.type, 'Itemized')

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_jpg_include_text_content(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()
        result = await client.recognize_receipts(receipt, include_text_content=True)

        self.assertEqual(len(result), 1)
        receipt = result[0]

        self.assertFormPagesHasValues(receipt.pages)
        for field, value in receipt.__dict__.items():
            if field not in ["receipt_type", "receipt_items", "page_range", "pages", "fields", "form_type", "receipt_locale"]:
                form_field = getattr(receipt, field)
                self.assertTextContentHasValues(form_field.value_data.text_content, receipt.page_range.first_page)

        for field, value in receipt.fields.items():
            self.assertTextContentHasValues(value.value_data.text_content, receipt.page_range.first_page)

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_multipage(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))
        with open(self.multipage_invoice_pdf, "rb") as fd:
            receipt = fd.read()
        result = await client.recognize_receipts(receipt, include_text_content=True)

        self.assertEqual(len(result), 3)
        receipt = result[0]
        self.assertEqual(receipt.merchant_address.value, '123 Hobbit Lane 567 Main St. Redmond, WA Redmond, WA')
        self.assertEqual(receipt.merchant_name.value, 'Bilbo Baggins')
        self.assertEqual(receipt.merchant_phone_number.value, '+15555555555')
        self.assertEqual(receipt.subtotal.value, 300.0)
        # TODO: revert after service side fix
        self.assertIsNotNone(receipt.total.value)
        self.assertEqual(receipt.page_range.first_page, 1)
        self.assertEqual(receipt.page_range.last_page, 1)
        self.assertFormPagesHasValues(receipt.pages)
        self.assertIsNotNone(receipt.receipt_type.confidence)
        self.assertEqual(receipt.receipt_type.type, 'Itemized')
        receipt = result[2]
        self.assertEqual(receipt.merchant_address.value, '123 Hobbit Lane 567 Main St. Redmond, WA Redmond, WA')
        self.assertEqual(receipt.merchant_name.value, 'Frodo Baggins')
        self.assertEqual(receipt.merchant_phone_number.value, '+15555555555')
        self.assertEqual(receipt.subtotal.value, 3000.0)
        self.assertEqual(receipt.total.value, 1000.0)
        self.assertEqual(receipt.page_range.first_page, 3)
        self.assertEqual(receipt.page_range.last_page, 3)
        self.assertFormPagesHasValues(receipt.pages)
        self.assertIsNotNone(receipt.receipt_type.confidence)
        self.assertEqual(receipt.receipt_type.type, 'Itemized')

    @GlobalFormRecognizerAccountPreparer()
    async def test_receipt_multipage_transform(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key))

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_us_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            myfile = fd.read()

        result = await client.recognize_receipts(
            stream=myfile,
            include_text_content=True,
            cls=callback
        )

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
            self.assertFormFieldTransformCorrect(receipt.merchant_address, actual.fields.get("MerchantAddress"), read_results)
            self.assertFormFieldTransformCorrect(receipt.merchant_name, actual.fields.get("MerchantName"), read_results)
            self.assertFormFieldTransformCorrect(receipt.merchant_phone_number, actual.fields.get("MerchantPhoneNumber"), read_results)
            self.assertFormFieldTransformCorrect(receipt.subtotal, actual.fields.get("Subtotal"), read_results)
            self.assertFormFieldTransformCorrect(receipt.tax, actual.fields.get("Tax"), read_results)
            self.assertFormFieldTransformCorrect(receipt.tip, actual.fields.get("Tip"), read_results)
            self.assertFormFieldTransformCorrect(receipt.total, actual.fields.get("Total"), read_results)
            self.assertFormFieldTransformCorrect(receipt.transaction_date, actual.fields.get("TransactionDate"), read_results)
            self.assertFormFieldTransformCorrect(receipt.transaction_time, actual.fields.get("TransactionTime"), read_results)

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
            self.assertEqual(receipt.page_range.first_page, actual.page_range[0])
            self.assertEqual(receipt.page_range.last_page, actual.page_range[1])

            # check receipt type
            self.assertEqual(receipt.receipt_type.confidence, actual.fields["ReceiptType"].confidence)
            self.assertEqual(receipt.receipt_type.type, actual.fields["ReceiptType"].value_string)

            # check receipt items
            self.assertReceiptItemsTransformCorrect(receipt.receipt_items, actual.fields["Items"], read_results)

        # Check form pages
        self.assertFormPagesTransformCorrect(returned_model, read_results)
