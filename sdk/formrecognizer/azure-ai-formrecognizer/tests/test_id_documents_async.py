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
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormContentType, FormRecognizerApiVersion
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer
from preparers import GlobalClientPreparer as _GlobalClientPreparer


GlobalClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestIdDocumentsAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_id_document_bad_endpoint(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        with open(self.id_document_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_id_documents(myfile)

    @FormRecognizerPreparer()
    async def test_authentication_bad_key(self, formrecognizer_test_endpoint, formrecognizer_test_api_key):
        client = FormRecognizerClient(formrecognizer_test_endpoint, AzureKeyCredential("xxxx"))
        with self.assertRaises(ClientAuthenticationError):
            async with client:
                poller = await client.begin_recognize_id_documents(b"xx", content_type="image/jpeg")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_passing_enum_content_type(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            myfile = fd.read()
        async with client: 
            poller = await client.begin_recognize_id_documents(
                myfile,
                content_type=FormContentType.IMAGE_JPEG
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes(self, client):
        damaged_pdf = b"\x25\x50\x44\x46\x55\x55\x55"  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_passed_as_bytes_io(self, client):
        damaged_pdf = BytesIO(b"\x25\x50\x44\x46\x55\x55\x55")  # still has correct bytes to be recognized as PDF
        with self.assertRaises(HttpResponseError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_blank_page(self, client):
        with open(self.blank_pdf, "rb") as fd:
            blank = fd.read()
        async with client:
            poller = await client.begin_recognize_id_documents(
                blank
            )
            result = await poller.result()
        self.assertIsNotNone(result)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_passing_bad_content_type_param_passed(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    myfile,
                    content_type="application/jpeg"
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_passing_unsupported_url_content_type(self, client):
        with self.assertRaises(TypeError):
            async with client:
                poller = await client.begin_recognize_id_documents("https://badurl.jpg", content_type="application/json")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_auto_detect_unsupported_stream_content(self, client):
        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            async with client:
                poller = await client.begin_recognize_id_documents(
                    myfile
                )

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_id_document_stream_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        with open(self.id_document_jpg, "rb") as fd:
            myfile = fd.read()

        async with client:
            poller = await client.begin_recognize_id_documents(
                id_document=myfile,
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
    @GlobalClientPreparer()
    async def test_id_document_jpg(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            id_document = fd.read()

        async with client:
            poller = await client.begin_recognize_id_documents(id_document)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        id_document = result[0]
        # check dict values

        self.assertEqual(id_document.fields.get("LastName").value, "TALBOT")
        self.assertEqual(id_document.fields.get("FirstName").value, "LIAM R.")
        # self.assertEqual(id_document.fields.get("DocumentNumber").value, "WDLABCD456DG") # service error when reading the license number returns 'LICWDLACD5DG'
        self.assertEqual(id_document.fields.get("DateOfBirth").value, date(1958,1,6))
        self.assertEqual(id_document.fields.get("DateOfExpiration").value, date(2020,8,12))
        self.assertEqual(id_document.fields.get("Sex").value_data.text, "M")
        self.assertEqual(id_document.fields.get("Address").value, "123 STREET ADDRESS YOUR CITY WA 99999-1234")
        # FIXME: country is not returning a value
        # self.assertEqual(id_document.fields.get("Country").value_data.text, "United States")
        self.assertEqual(id_document.fields.get("Region").value, "Washington")

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_id_document_jpg_include_field_elements(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            poller = await client.begin_recognize_id_documents(id_document, include_field_elements=True)

            result = await poller.result()
        self.assertEqual(len(result), 1)
        id_document = result[0]

        self.assertFormPagesHasValues(id_document.pages)

        for field in id_document.fields.values():
            if field.name == "Country":
                # FIXME: this is different than the other field values
                # self.assertEqual(field.value_data.text, "United States")
                continue
            elif field.name == "Region":
                self.assertEqual(field.value, "Washington")
            else: 
                self.assertFieldElementsHasValues(field.value_data.field_elements, id_document.page_range.first_page_number)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    @pytest.mark.live_test_only
    async def test_id_document_continuation_token(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            initial_poller = await client.begin_recognize_id_documents(id_document)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_id_documents(None, continuation_token=cont_token)
            result = await poller.result()
            self.assertIsNotNone(result)
            await initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @GlobalClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    async def test_id_document_v2(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            id_document = fd.read()
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_id_documents(id_document)
        assert "Method 'begin_recognize_id_documents' is only available for API version V2_1_PREVIEW and up" in str(e.value)

    @FormRecognizerPreparer()
    @GlobalClientPreparer()
    async def test_pages_kwarg_specified(self, client):
        with open(self.id_document_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            poller = await client.begin_recognize_id_documents(id_document, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
