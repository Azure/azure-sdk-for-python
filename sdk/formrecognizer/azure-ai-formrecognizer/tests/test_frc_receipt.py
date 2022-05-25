# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date, time
from devtools_testutils import recorded_by_proxy
from azure.ai.formrecognizer import FormRecognizerClient, FormContentType, FormRecognizerApiVersion
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)

class TestReceiptFromStream(FormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_passing_enum_content_type_v2(self, client):
        with open(self.receipt_png, "rb") as fd:
            my_file = fd.read()
        poller = client.begin_recognize_receipts(
            my_file,
            content_type=FormContentType.IMAGE_PNG
        )
        result = poller.result()
        assert result is not None

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_bytes_fails_autodetect_content_type(self, **kwargs):
        client = kwargs.pop("client")
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            poller = client.begin_recognize_receipts(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    # TODO should there be a v3 version of this test?
    def test_damaged_file_bytes_io_fails_autodetect(self, **kwargs):
        client = kwargs.pop("client")
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            poller = client.begin_recognize_receipts(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.receipt_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            poller = client.begin_recognize_receipts(
                my_file,
                content_type="application/jpeg"
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_unsupported_url_content_type(self, **kwargs):
        client = kwargs.pop("client")
        with pytest.raises(TypeError):
            poller = client.begin_recognize_receipts(
                "https://badurl.jpg",
                content_type="application/json"
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy
    def test_receipt_jpg_include_field_elements(self, client):
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()
        poller = client.begin_recognize_receipts(receipt, include_field_elements=True)

        result = poller.result()
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
        assert receipt.fields.get("TransactionTime").value == time(hour=13, minute=59, second=0)
        assert receipt.page_range.first_page_number ==  1
        assert receipt.page_range.last_page_number ==  1
        self.assertFormPagesHasValues(receipt.pages)
        receipt_type = receipt.fields.get("ReceiptType")
        assert receipt_type.confidence is not None
        assert receipt_type.value ==  'Itemized'

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_receipt_locale_v2(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.receipt_jpg, "rb") as fd:
            receipt = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_receipts(receipt, locale="en-US")
        assert "'locale' is only available for API version V2_1 and up" in str(e.value)
