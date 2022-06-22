# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer

FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestBusinessCardAsync(AsyncFormRecognizerTest):

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_passing_enum_content_type(self, client):
        with open(self.business_card_png, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(
                my_file,
                content_type=FormContentType.IMAGE_PNG
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
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, **kwargs):
        client = kwargs.pop("client")
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )
                result = await poller.result()

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.business_card_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    my_file,
                    content_type="application/jpeg"
                )

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @recorded_by_proxy_async
    async def test_business_card_jpg_include_field_elements(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(business_card, include_field_elements=True)
            result = await poller.result()
        assert len(result) == 1
        business_card = result[0]

        self.assertFormPagesHasValues(business_card.pages)

        for name, field in business_card.fields.items():
            for f in field.value:
                self.assertFieldElementsHasValues(f.value_data.field_elements, business_card.page_range.first_page_number)

        # check dict values
        assert len(business_card.fields.get("ContactNames").value) == 1
        assert business_card.fields.get("ContactNames").value[0].value_data.page_number == 1
        assert business_card.fields.get("ContactNames").value[0].value['FirstName'].value == 'Avery'
        assert business_card.fields.get("ContactNames").value[0].value['LastName'].value == 'Smith'

        assert len(business_card.fields.get("JobTitles").value) == 1
        assert business_card.fields.get("JobTitles").value[0].value == "Senior Researcher"

        assert len(business_card.fields.get("Departments").value) == 1
        assert business_card.fields.get("Departments").value[0].value == "Cloud & Al Department"

        assert len(business_card.fields.get("Emails").value) == 1
        assert business_card.fields.get("Emails").value[0].value == "avery.smith@contoso.com"

        assert len(business_card.fields.get("Websites").value) == 1
        assert business_card.fields.get("Websites").value[0].value == "https://www.contoso.com/"

        # The phone number values are not getting normalized to a phone number type. Just assert on text.
        assert len(business_card.fields.get("MobilePhones").value) == 1
        assert business_card.fields.get("MobilePhones").value[0].value_data.text == "+44 (0) 7911 123456"

        assert len(business_card.fields.get("WorkPhones").value) == 1
        assert business_card.fields.get("WorkPhones").value[0].value_data.text == "+44 (0) 20 9876 5432"

        assert len(business_card.fields.get("Faxes").value) == 1
        assert business_card.fields.get("Faxes").value[0].value_data.text == "+44 (0) 20 6789 2345"

        assert len(business_card.fields.get("Addresses").value) == 1
        assert business_card.fields.get("Addresses").value[0].value == "2 Kingdom Street Paddington, London, W2 6BD"

        assert len(business_card.fields.get("CompanyNames").value) == 1
        assert business_card.fields.get("CompanyNames").value[0].value == "Contoso"

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_business_card_v2(self, **kwargs):
        client = kwargs.pop("client")
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_business_cards(business_card)
        assert "Method 'begin_recognize_business_cards' is only available for API version V2_1 and up" in str(e.value)
