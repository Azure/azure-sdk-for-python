# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date, time
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_receipt
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormField, FormRecognizerApiVersion
from testcase import GlobalFormRecognizerAccountPreparer
from asynctestcase import AsyncFormRecognizerTest
from testcase import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestBusinessCardAsync(AsyncFormRecognizerTest):

    @GlobalFormRecognizerAccountPreparer()
    async def test_business_card_bad_endpoint(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        with open(self.business_card_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(form_recognizer_account_key))
            async with client:
                poller = await client.begin_recognize_business_cards(myfile)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_authentication_successful_key(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            myfile = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(myfile)
            result = await poller.result()

    @GlobalFormRecognizerAccountPreparer()
    async def test_authentication_bad_key(self, resource_group, location, form_recognizer_account, form_recognizer_account_key):
        client = FormRecognizerClient(form_recognizer_account, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_business_cards(b"xx", content_type="image/jpeg")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_passing_enum_content_type(self, client):
        with open(self.business_card_png, "rb") as fd:
            myfile = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(
                myfile,
                content_type=FormContentType.IMAGE_PNG
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes_io(self, client):
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    damaged_pdf
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_blank_page(self, client):

        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(
                blank
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_passing_bad_content_type_param_passed(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    myfile,
                    content_type="application/jpeg"
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_passing_unsupported_url_content_type(self, client):
        with self.assertRaises(TypeError):
            async with client:
                poller = await client.begin_recognize_business_cards("https://badurl.jpg", content_type="application/json")

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_auto_detect_unsupported_stream_content(self, client):

        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_business_cards(
                    myfile
                )

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_stream_transform_png(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        with open(self.business_card_png, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_recognize_business_cards(
                business_card=myfile,
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
    async def test_business_card_stream_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_receipt(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        with open(self.business_card_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_recognize_business_cards(
                business_card=myfile,
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

        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()

        async with client:
            poller = await client.begin_recognize_business_cards(business_card)
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
        with open(self.business_card_png, "rb") as fd:
            stream = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(stream)
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
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(business_card, include_field_elements=True)
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

        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()

        async with client:
            initial_poller = await client.begin_recognize_business_cards(business_card)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_business_cards(business_card, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_business_card_v2(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_business_cards(business_card)
        assert "Method 'begin_recognize_business_cards' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_locale_specified(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        async with client:
            poller = await client.begin_recognize_business_cards(business_card, locale="en-IN")
            assert 'en-IN' == poller._polling_method._initial_response.http_response.request.query['locale']
            await poller.wait()

    @GlobalFormRecognizerAccountPreparer()
    @GlobalClientPreparer()
    async def test_business_card_locale_error(self, client):
        with open(self.business_card_jpg, "rb") as fd:
            business_card = fd.read()
        with pytest.raises(HttpResponseError) as e:
            async with client:
                await client.begin_recognize_business_cards(business_card, locale="not a locale")
        assert "locale" in e.value.error.message
