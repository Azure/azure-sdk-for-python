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
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_receipt
from azure.ai.formrecognizer.aio import FormRecognizerClient
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestBusinessCardFromUrlAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_polling_interval(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential(form_recognizer_account_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        async with client:
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, polling_interval=6)
            await poller.wait()
            self.assertEqual(poller._polling_method._timeout, 6)
            poller2 = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
            await poller2.wait()
            self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_cards_encoded_url(self, client):
        async with client:
            try:
                poller = await client.begin_recognize_business_cards_from_url("https://fakeuri.com/blank%20space")
            except HttpResponseError as e:
                self.assertIn("https://fakeuri.com/blank%20space", e.response.request.body)

    @GlobalFormRecognizerAccountPreparer()
    async def test_business_card_url_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):

        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            async with client:
                poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_authentication_successful_key(self, client):
        async with client:
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        async with client:
            with self.assertRaises(ClientAuthenticationError):
                poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_bad_url(self, client):
        async with client:
            with self.assertRaises(HttpResponseError):
                poller = await client.begin_recognize_business_cards_from_url("https://badurl.jpg")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_url_pass_stream(self, client):
        async with client:
            with open(self.business_card_png, "rb") as business_card:
                with self.assertRaises(HttpResponseError):
                    poller = await client.begin_recognize_business_cards_from_url(business_card)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_url_transform_png(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        async with client:
            poller = await client.begin_recognize_business_cards_from_url(
                business_card_url=self.business_card_url_png,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        business_card = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        # check dict values
        self.assertFormFieldTransformCorrect(business_card.fields.get("ContactNames"), actual.get("ContactNames"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("JobTitles"), actual.get("JobTitles"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Departments"), actual.get("Departments"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Emails"), actual.get("Emails"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Websites"), actual.get("Websites"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("MobilePhones"), actual.get("MobilePhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("OtherPhones"), actual.get("OtherPhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Faxes"), actual.get("Faxes"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Addresses"), actual.get("Addresses"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("CompanyNames"), actual.get("CompanyNames"), read_results)

        # check page range
        self.assertEqual(business_card.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(business_card.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(business_card.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        async with client:
            poller = await client.begin_recognize_business_cards_from_url(
                business_card_url=self.business_card_url_jpg,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        business_card = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        # check dict values
        self.assertFormFieldTransformCorrect(business_card.fields.get("ContactNames"), actual.get("ContactNames"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("JobTitles"), actual.get("JobTitles"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Departments"), actual.get("Departments"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Emails"), actual.get("Emails"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Websites"), actual.get("Websites"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("MobilePhones"), actual.get("MobilePhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("OtherPhones"), actual.get("OtherPhones"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Faxes"), actual.get("Faxes"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("Addresses"), actual.get("Addresses"), read_results)
        self.assertFormFieldTransformCorrect(business_card.fields.get("CompanyNames"), actual.get("CompanyNames"), read_results)

        # check page range
        self.assertEqual(business_card.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(business_card.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(business_card.pages, read_results)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_jpg(self, client):
        async with client:
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]
        # check dict values
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'Avery')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'Smith')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Senior Researcher")

        self.assertEqual(len(business_card.fields.get("Departments").value), 1)
        self.assertEqual(business_card.fields.get("Departments").value[0].value, "Cloud & Al Department")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "avery.smith@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com/")

        # TODO: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
        # self.assertEqual(len(business_card.fields.get("MobilePhones").value), 1)
        # self.assertEqual(business_card.fields.get("MobilePhones").value[0].value, "https://www.contoso.com/")

        # self.assertEqual(len(business_card.fields.get("OtherPhones").value), 1)
        # self.assertEqual(business_card.fields.get("OtherPhones").value[0].value, "https://www.contoso.com/")

        # self.assertEqual(len(business_card.fields.get("Faxes").value), 1)
        # self.assertEqual(business_card.fields.get("Faxes").value[0].value, "https://www.contoso.com/")

        self.assertEqual(len(business_card.fields.get("Addresses").value), 1)
        self.assertEqual(business_card.fields.get("Addresses").value[0].value, "2 Kingdom Street Paddington, London, W2 6BD")

        self.assertEqual(len(business_card.fields.get("CompanyNames").value), 1)
        self.assertEqual(business_card.fields.get("CompanyNames").value[0].value, "Contoso")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_png(self, client):
        async with client:
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_png)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]
        # check dict values
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'Avery')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'Smith')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Senior Researcher")

        self.assertEqual(len(business_card.fields.get("Departments").value), 1)
        self.assertEqual(business_card.fields.get("Departments").value[0].value, "Cloud & Al Department")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "avery.smith@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com/")

        # TODO: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
        # self.assertEqual(len(business_card.fields.get("MobilePhones").value), 1)
        # self.assertEqual(business_card.fields.get("MobilePhones").value[0].value, "https://www.contoso.com/")

        # self.assertEqual(len(business_card.fields.get("OtherPhones").value), 1)
        # self.assertEqual(business_card.fields.get("OtherPhones").value[0].value, "https://www.contoso.com/")

        # self.assertEqual(len(business_card.fields.get("Faxes").value), 1)
        # self.assertEqual(business_card.fields.get("Faxes").value[0].value, "https://www.contoso.com/")

        self.assertEqual(len(business_card.fields.get("Addresses").value), 1)
        self.assertEqual(business_card.fields.get("Addresses").value[0].value, "2 Kingdom Street Paddington, London, W2 6BD")

        self.assertEqual(len(business_card.fields.get("CompanyNames").value), 1)
        self.assertEqual(business_card.fields.get("CompanyNames").value[0].value, "Contoso")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_jpg_include_field_elements(self, client):
        async with client:
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, include_field_elements=True)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]

        self.assertFormPagesHasValues(business_card.pages)

        for name, field in business_card.fields.items():
            if field.value_type not in ["list", "dictionary"]:
                self.assertFieldElementsHasValues(field.value_data.field_elements, receipt.page_range.first_page_number)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_business_card_continuation_token(self, client):
        async with client:
            initial_poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error
