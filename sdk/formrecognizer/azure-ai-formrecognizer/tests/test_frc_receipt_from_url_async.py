# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date, time
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_custom_default_matcher
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerApiVersion
from azure.ai.formrecognizer.aio import FormRecognizerClient
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)

class TestReceiptFromUrlAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_transform_png(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
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
        assert receipt.page_range.first_page_number ==  document_results[0].page_range[0]
        assert receipt.page_range.last_page_number ==  document_results[0].page_range[1]

        # Check page metadata
        self.assertFormPagesTransformCorrect(receipt.pages, read_results)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_receipt_url_include_field_elements(self, client):
        # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
        )
        
        async with client:
            poller = await client.begin_recognize_receipts_from_url(
                self.receipt_url_jpg,
                include_field_elements=True
            )
            result = await poller.result()

        assert len(result) == 1
        receipt = result[0]

        self.assertFormPagesHasValues(receipt.pages)

        for name, field in receipt.fields.items():
            if field.value_type not in ["list", "dictionary"] and name != "ReceiptType":  # receipt cases where value_data is None
                self.assertFieldElementsHasValues(field.value_data.field_elements, receipt.page_range.first_page_number)
        
        assert receipt.fields.get("MerchantAddress").value, '123 Main Street Redmond ==  WA 98052'
        assert receipt.fields.get("MerchantName").value ==  'Contoso'
        assert receipt.fields.get("MerchantPhoneNumber").value ==  '+19876543210'
        assert receipt.fields.get("Subtotal").value ==  11.7
        assert receipt.fields.get("Tax").value ==  1.17
        assert receipt.fields.get("Tip").value ==  1.63
        assert receipt.fields.get("Total").value ==  14.5
        assert receipt.fields.get("TransactionDate").value == date(year=2019, month=6, day=10)
        assert receipt.fields.get("TransactionTime").value ==  time(hour=13, minute=59, second=0)
        assert receipt.page_range.first_page_number ==  1
        assert receipt.page_range.last_page_number ==  1
        receipt_type = receipt.fields.get("ReceiptType")
        assert receipt_type.confidence is not None
        assert receipt_type.value ==  'Itemized'
        self.assertReceiptItemsHasValues(receipt.fields["Items"].value, receipt.page_range.first_page_number, True)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_receipt_locale_v2(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_receipts_from_url(self.receipt_url_jpg, locale="en-US")
        assert "'locale' is only available for API version V2_1 and up" in str(e.value)
