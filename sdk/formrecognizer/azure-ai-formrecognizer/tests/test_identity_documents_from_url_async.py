# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from datetime import date
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerApiVersion
from azure.ai.formrecognizer.aio import FormRecognizerClient, DocumentAnalysisClient
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer

DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)
FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestIdDocumentsFromUrlAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_polling_interval(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key), polling_interval=7)
        self.assertEqual(client._client._config.polling_interval, 7)

        async with client:
            poller = await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, polling_interval=6)
            await poller.wait()
            self.assertEqual(poller._polling_method._timeout, 6)
            poller2 = await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
            await poller2.wait()
            self.assertEqual(poller2._polling_method._timeout, 7)  # goes back to client default

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_identity_document_url_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        async with client:
            poller = await client.begin_recognize_identity_documents_from_url(
                identity_document_url=self.identity_document_url_jpg,
                include_field_elements=True,
                cls=callback
            )

            result = await poller.result()
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
    @DocumentAnalysisClientPreparer()
    async def test_identity_document_jpg_passport(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-idDocument", self.identity_document_url_jpg_passport)

            result = await poller.result()
            assert len(result.documents) == 1
        
            id_document = result.documents[0]
            # check dict values

            passport = id_document.fields.get("MachineReadableZone").value
            assert passport["LastName"].value == "MARTIN"
            assert passport["FirstName"].value == "SARAH"
            assert passport["DocumentNumber"].value == "ZE000509"
            assert passport["DateOfBirth"].value == date(1985,1,1)
            assert passport["DateOfExpiration"].value == date(2023,1,14)
            assert passport["Sex"].value == "F"
            assert passport["CountryRegion"].value == "CAN"

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    async def test_identity_document_jpg(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-idDocument", self.identity_document_url_jpg)

            result = await poller.result()
        assert len(result.documents) == 1
        id_document = result.documents[0]

        # check dict values
        assert id_document.fields.get("LastName").value == "TALBOT"
        assert id_document.fields.get("FirstName").value == "LIAM R."
        assert id_document.fields.get("DocumentNumber").value == "WDLABCD456DG"
        assert id_document.fields.get("DateOfBirth").value == date(1958,1,6)
        assert id_document.fields.get("DateOfExpiration").value == date(2020,8,12)
        assert id_document.fields.get("Sex").value == "M"
        assert id_document.fields.get("Address").value == "123 STREET ADDRESS YOUR CITY WA 99999-1234"
        assert id_document.fields.get("CountryRegion").value == "USA"
        assert id_document.fields.get("Region").value == "Washington"


    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_identity_document_jpg_include_field_elements(self, client):
        async with client:
            poller = await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, include_field_elements=True)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        id_document = result[0]

        self.assertFormPagesHasValues(id_document.pages)

        for field in id_document.fields.values():
            if field.name == "CountryRegion":
                self.assertEqual(field.value, "USA")
                continue
            elif field.name == "Region":
                self.assertEqual(field.value, "Washington")
            else:
                self.assertFieldElementsHasValues(field.value_data.field_elements, id_document.page_range.first_page_number)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    @pytest.mark.live_test_only
    async def test_identity_document_continuation_token(self, client):
        async with client:
            initial_poller = await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_identity_documents_from_url(None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_identity_document_v2(self, client):
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg)
        assert "Method 'begin_recognize_identity_documents_from_url' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    async def test_pages_kwarg_specified(self, client):
        async with client:
            poller = await client.begin_recognize_identity_documents_from_url(self.identity_document_url_jpg, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
