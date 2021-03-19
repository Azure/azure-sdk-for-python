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
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)

class TestBusinessCardFromUrl(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, polling_interval=6)
        poller.wait()
        self.assertEqual(poller._polling_method._timeout, 6)
        poller2 = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
        poller2.wait()
        self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_cards_encoded_url(self, client):
        try:
            poller = client.begin_recognize_business_cards_from_url("https://fakeuri.com/blank%20space")
        except HttpResponseError as e:
            self.assertIn("https://fakeuri.com/blank%20space", e.response.request.body)

    @FormRecognizerPreparer()
    def test_business_card_url_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)

    @FormRecognizerPreparer()
    def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_business_cards_from_url("https://badurl.jpg")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_url_pass_stream(self, client):
        with open(self.business_card_png, "rb") as business_card:
            with self.assertRaises(HttpResponseError):
                poller = client.begin_recognize_business_cards_from_url(business_card)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_url_transform_png(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        poller = client.begin_recognize_business_cards_from_url(
            business_card_url=self.business_card_url_png,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        business_card = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results

        self.assertFormFieldsTransformCorrect(business_card.fields, actual, read_results)

        # check page range
        self.assertEqual(business_card.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(business_card.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(business_card.pages, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        poller = client.begin_recognize_business_cards_from_url(
            business_card_url=self.business_card_url_jpg,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        business_card = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertFormFieldsTransformCorrect(business_card.fields, actual, read_results)

        # check page range
        self.assertEqual(business_card.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(business_card.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(business_card.pages, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_url_multipage_transform_pdf(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_business_card = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_business_card)

        poller = client.begin_recognize_business_cards_from_url(
            business_card_url=self.business_card_multipage_url_pdf,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertEqual(2, len(returned_model))
        self.assertEqual(2, len(document_results))

        for i in range(len(returned_model)):
            business_card = returned_model[i]
            actual = document_results[i]
            self.assertFormFieldsTransformCorrect(business_card.fields, actual.fields, read_results)
            self.assertEqual(i + 1, business_card.page_range.first_page_number)
            self.assertEqual(i + 1, business_card.page_range.last_page_number)

        # Check page metadata
        self.assertFormPagesTransformCorrect(returned_model, read_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_png(self, client):
        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_png)

        result = poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]
        # check dict values
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value_data.page_number, 1)
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

        # FIXME: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
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

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_multipage_pdf(self, client):

        poller = client.begin_recognize_business_cards_from_url(self.business_card_multipage_url_pdf, include_field_elements=True)
        result = poller.result()

        self.assertEqual(len(result), 2)
        business_card = result[0]
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value_data.page_number, 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['FirstName'].value, 'JOHN')
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value['LastName'].value, 'SINGER')

        self.assertEqual(len(business_card.fields.get("JobTitles").value), 1)
        self.assertEqual(business_card.fields.get("JobTitles").value[0].value, "Software Engineer")

        self.assertEqual(len(business_card.fields.get("Emails").value), 1)
        self.assertEqual(business_card.fields.get("Emails").value[0].value, "johnsinger@contoso.com")

        self.assertEqual(len(business_card.fields.get("Websites").value), 1)
        self.assertEqual(business_card.fields.get("Websites").value[0].value, "https://www.contoso.com")

        # FIXME: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
        # self.assertEqual(len(business_card.fields.get("OtherPhones").value), 1)
        # self.assertEqual(business_card.fields.get("OtherPhones").value[0].value, "https://www.contoso.com/")

        business_card = result[1]
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value_data.page_number, 2)
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

        # FIXME: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
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

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_jpg_include_field_elements(self, client):
        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, include_field_elements=True)

        result = poller.result()
        self.assertEqual(len(result), 1)
        business_card = result[0]

        self.assertFormPagesHasValues(business_card.pages)

        for name, field in business_card.fields.items():
            for f in field.value:
                self.assertFieldElementsHasValues(f.value_data.field_elements, business_card.page_range.first_page_number)
        
        # check dict values
        self.assertEqual(len(business_card.fields.get("ContactNames").value), 1)
        self.assertEqual(business_card.fields.get("ContactNames").value[0].value_data.page_number, 1)
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

        # FIXME: uncomment https://github.com/Azure/azure-sdk-for-python/issues/14300
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

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_business_card_continuation_token(self, client):

        initial_poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_business_cards_from_url(None, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_business_card_v2(self, client):
        with pytest.raises(ValueError) as e:
            client.begin_recognize_business_cards_from_url(self.business_card_url_jpg)
        assert "Method 'begin_recognize_business_cards_from_url' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_locale_specified(self, client):
        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, locale="en-IN")
        assert 'en-IN' == poller._polling_method._initial_response.http_response.request.query['locale']
        result = poller.result()
        assert result

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_business_card_locale_error(self, client):
        with pytest.raises(HttpResponseError) as e:
            client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, locale="not a locale")
        assert "locale" in e.value.error.message

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_pages_kwarg_specified(self, client):
        poller = client.begin_recognize_business_cards_from_url(self.business_card_url_jpg, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
