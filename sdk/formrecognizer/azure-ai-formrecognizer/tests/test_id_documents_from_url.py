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


class TestIdDocumentsFromUrl(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg, polling_interval=6)
        poller.wait()
        self.assertEqual(poller._polling_method._timeout, 6)
        poller2 = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg)
        poller2.wait()
        self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_encoded_url(self, client):
        try:
            poller = client.begin_recognize_id_documents_from_url("https://fakeuri.com/blank%20space")
        except HttpResponseError as e:
            self.assertIn("https://fakeuri.com/blank%20space", e.response.request.body)

    @FormRecognizerPreparer()
    def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_bad_url(self, client):
        with self.assertRaises(HttpResponseError):
            poller = client.begin_recognize_id_documents_from_url("https://badurl.jpg")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_url_pass_stream(self, client):
        with open(self.id_document_license_jpg, "rb") as id_document:
            with self.assertRaises(HttpResponseError):
                poller = client.begin_recognize_id_documents_from_url(id_document)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        poller = client.begin_recognize_id_documents_from_url(
            id_document_url=self.id_document_url_jpg,
            include_field_elements=True,
            cls=callback
        )

        result = poller.result()
        raw_response = responses[0]
        returned_model = responses[1]
        id_document = returned_model[0]
        actual = raw_response.analyze_result.document_results[0].fields
        read_results = raw_response.analyze_result.read_results
        document_results = raw_response.analyze_result.document_results
        page_results = raw_response.analyze_result.page_results

        self.assertFormFieldsTransformCorrect(id_document.fields, actual, read_results)

        # check page range
        self.assertEqual(id_document.page_range.first_page_number, document_results[0].page_range[0])
        self.assertEqual(id_document.page_range.last_page_number, document_results[0].page_range[1])

        # Check page metadata
        self.assertFormPagesTransformCorrect(id_document.pages, read_results, page_results)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_jpg_passport(self, client):
        poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg_passport)

        result = poller.result()
        self.assertEqual(len(result), 1)
    
        id_document = result[0]
        # check dict values

        passport = id_document.fields.get("MachineReadableZone").value
        self.assertEqual(passport["LastName"].value, "MARTIN")
        self.assertEqual(passport["FirstName"].value, "SARAH")
        self.assertEqual(passport["DocumentNumber"].value, "ZE000509")
        self.assertEqual(passport["DateOfBirth"].value, date(1985,1,1))
        self.assertEqual(passport["DateOfExpiration"].value, date(2023,1,14))
        self.assertEqual(passport["Sex"].value, "F")
        self.assertEqual(passport["Country"].value, "CAN")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_jpg(self, client):
        poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg)

        result = poller.result()
        self.assertEqual(len(result), 1)
        id_document = result[0]

        # check dict values
        self.assertEqual(id_document.fields.get("LastName").value, "TALBOT")
        self.assertEqual(id_document.fields.get("FirstName").value, "LIAM R.")
        # FIXME service error when reading the license number returns 'LICWDLACD5DG'
        # self.assertEqual(id_document.fields.get("DocumentNumber").value, "WDLABCD456DG")
        self.assertEqual(id_document.fields.get("DateOfBirth").value, date(1958,1,6))
        self.assertEqual(id_document.fields.get("DateOfExpiration").value, date(2020,8,12))
        self.assertEqual(id_document.fields.get("Sex").value, "M")
        self.assertEqual(id_document.fields.get("Address").value, "123 STREET ADDRESS YOUR CITY WA 99999-1234")
        self.assertEqual(id_document.fields.get("Country").value, "USA")
        self.assertEqual(id_document.fields.get("Region").value, "Washington")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_id_document_jpg_include_field_elements(self, client):
        poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg, include_field_elements=True)

        result = poller.result()
        self.assertEqual(len(result), 1)
        id_document = result[0]

        self.assertFormPagesHasValues(id_document.pages)

        for field in id_document.fields.values():
            if field.name == "Country":
                self.assertEqual(field.value, "USA")
                continue
            elif field.name == "Region":
                self.assertEqual(field.value, "Washington")
            else:
                self.assertFieldElementsHasValues(field.value_data.field_elements, id_document.page_range.first_page_number)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    def test_id_document_continuation_token(self, client):
        initial_poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_id_documents_from_url(None, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_id_document_v2(self, client):
        with pytest.raises(ValueError) as e:
            client.begin_recognize_id_documents_from_url(self.id_document_url_jpg)
        assert "Method 'begin_recognize_id_documents_from_url' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    def test_pages_kwarg_specified(self, client):
        poller = client.begin_recognize_id_documents_from_url(self.id_document_url_jpg, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
