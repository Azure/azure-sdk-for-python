# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date, time
from azure.core.exceptions import HttpResponseError, ServiceRequestError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._generated.v2021_09_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerApiVersion, AnalyzeResult
from azure.ai.formrecognizer.aio import FormRecognizerClient, DocumentAnalysisClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)
GlobalClientPreparerV2 = functools.partial(_GlobalClientPreparer, FormRecognizerClient)

class TestReceiptFromUrlAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, polling_interval=6)
            await poller.wait()
            self.assertEqual(poller._polling_method._timeout, 6)
            poller2 = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
            await poller2.wait()
            self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @pytest.mark.skip("aad not enabled yet in v2021-07-30")
    async def test_active_directory_auth_async(self):
        token = self.generate_oauth_token()
        endpoint = self.get_oauth_endpoint()
        client = DocumentAnalysisClient(endpoint, token)
        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.receipt_url_jpg
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipts_encoded_url(self, client):
        with pytest.raises(HttpResponseError) as e:
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", "https://fakeuri.com/blank%20space")
        self.assertIn("https://fakeuri.com/blank%20space", e.value.response.request.body)

    @FormRecognizerPreparer()
    async def test_receipt_url_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with self.assertRaises(ServiceRequestError):
            client = DocumentAnalysisClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_analyze_document_from_url(
                    "prebuilt-receipt",
                    self.receipt_url_jpg
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    async def test_receipt_url_auth_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_analyze_document_from_url(
                    "prebuilt-receipt",
                    self.receipt_url_jpg
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", "https://badurl.jpg")
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_url_pass_stream(self, client):

        with open(self.receipt_png, "rb") as fd:
            receipt = fd.read(4)  # makes the recording smaller

        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_analyze_document_from_url("prebuilt-receipt", receipt)
                result = await poller.result()

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_url_transform_jpg(self, client):

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.receipt_url_jpg,
                cls=callback
            )
            result = await poller.result()

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
    @GlobalClientPreparerV2()
    async def test_receipt_url_transform_png(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        async with client:
            poller = await client.begin_recognize_receipts_from_url(
                self.receipt_url_png,
                include_field_elements=True,
                cls=callback
            )
            result = await poller.result()

        raw_response = responses[0]
        returned_model = responses[1]
        receipt = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        # check dict values
        self.assertFormFieldsTransformCorrect(receipt.fields, actual, read_results)

        # check page range
        self.assertEqual(receipt.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(receipt.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparerV2()
    async def test_receipt_url_include_field_elements(self, client):

        async with client:
            poller = await client.begin_recognize_receipts_from_url(
                self.receipt_url_jpg,
                include_field_elements=True
            )
            result = await poller.result()

        self.assertEqual(len(result), 1)
        receipt = result[0]

        self.assertFormPagesHasValues(receipt.pages)

        for name, field in receipt.fields.items():
            if field.value_type not in ["list", "dictionary"] and name != "ReceiptType":  # receipt cases where value_data is None
                self.assertFieldElementsHasValues(field.value_data.field_elements, receipt.page_range.first_page_number)
        
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso')
        self.assertEqual(receipt.fields.get("MerchantPhoneNumber").value, '+19876543210')
        self.assertEqual(receipt.fields.get("Subtotal").value, 11.7)
        self.assertEqual(receipt.fields.get("Tax").value, 1.17)
        self.assertEqual(receipt.fields.get("Tip").value, 1.63)
        self.assertEqual(receipt.fields.get("Total").value, 14.5)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        self.assertEqual(receipt.page_range.first_page_number, 1)
        self.assertEqual(receipt.page_range.last_page_number, 1)
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')
        self.assertReceiptItemsHasValues(receipt.fields["Items"].value, receipt.page_range.first_page_number, True)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_url_png(self, client):

        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_png)
            result = await poller.result()

        self.assertEqual(len(result.documents), 1)
        receipt = result.documents[0]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso')
        self.assertEqual(receipt.fields.get("Subtotal").value, 1098.99)
        self.assertEqual(receipt.fields.get("Tax").value, 104.4)
        self.assertEqual(receipt.fields.get("Total").value, 1203.39)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')

        self.assertEqual(len(result.pages), 1)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_multipage_url(self, client):

        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.multipage_receipt_url_pdf)
            result = await poller.result()

        self.assertEqual(len(result.documents), 2)
        receipt = result.documents[0]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso')
        self.assertEqual(receipt.fields.get("MerchantPhoneNumber").value, '+19876543210')
        self.assertEqual(receipt.fields.get("Subtotal").value, 11.7)
        self.assertEqual(receipt.fields.get("Tax").value, 1.17)
        self.assertEqual(receipt.fields.get("Tip").value, 1.63)
        self.assertEqual(receipt.fields.get("Total").value, 14.5)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')
        receipt = result.documents[1]
        self.assertEqual(receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond, WA 98052')
        self.assertEqual(receipt.fields.get("MerchantName").value, 'Contoso')
        self.assertEqual(receipt.fields.get("Subtotal").value, 1098.99)
        self.assertEqual(receipt.fields.get("Tax").value, 104.4)
        self.assertEqual(receipt.fields.get("Total").value, 1203.39)
        self.assertEqual(receipt.fields.get("TransactionDate").value, date(year=2019, month=6, day=10))
        self.assertEqual(receipt.fields.get("TransactionTime").value, time(hour=13, minute=59, second=0))
        receipt_type = receipt.fields.get("ReceiptType")
        self.assertIsNotNone(receipt_type.confidence)
        self.assertEqual(receipt_type.value, 'Itemized')

        self.assertEqual(len(result.pages), 2)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_multipage_transform_url(self, client):

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_receipt = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_receipt)

        async with client:
            poller = await client.begin_analyze_document_from_url(
                "prebuilt-receipt",
                self.multipage_receipt_url_pdf,
                cls=callback
            )

            result = await poller.result()
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
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_receipt_continuation_token(self, client):

        async with client:
            initial_poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_receipt_locale_specified(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, locale="en-IN")
            assert 'en-IN' == poller._polling_method._initial_response.http_response.request.query['locale']
            result = await poller.result()
            assert result

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.skip("different error code being returned")
    async def test_receipt_locale_error(self, client):
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, locale="not a locale")
        assert "InvalidArgument" == e.value.error.code

    @FormRecognizerPreparer()
    @GlobalClientPreparerV2(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_receipt_locale_v2(self, client):
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_receipts_from_url(self.receipt_url_jpg, locale="en-US")
        assert "'locale' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_pages_kwarg_specified(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-receipt", self.receipt_url_jpg, pages="1")
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
