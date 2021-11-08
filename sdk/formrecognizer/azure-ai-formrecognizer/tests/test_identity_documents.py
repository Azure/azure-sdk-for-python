# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from datetime import date, time
from azure.core.exceptions import ServiceRequestError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiVersion, DocumentAnalysisClient
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer

DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)
FormRecognizerClientPreparer = functools.partial(_GlobalClientPreparer, FormRecognizerClient)


class TestIdDocument(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_identity_document_bad_endpoint(self, formrecognizer_test_api_key):
        with open(self.identity_document_license_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            poller = client.begin_recognize_identity_documents(myfile)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_bytes_fails_autodetect_content_type(self, client):
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_identity_documents(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_damaged_file_bytes_io_fails_autodetect(self, client):
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_identity_documents(
                damaged_pdf
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_passing_bad_content_type_param_passed(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            myfile = fd.read()
        with self.assertRaises(ValueError):
            poller = client.begin_recognize_identity_documents(
                myfile,
                content_type="application/jpeg"
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_auto_detect_unsupported_stream_content(self, client):
        with open(self.unsupported_content_py, "rb") as fd:
            myfile = fd.read()

        with self.assertRaises(ValueError):
            poller = client.begin_recognize_identity_documents(
                myfile
            )

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_identity_document_stream_transform_jpg(self, client):
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        with open(self.identity_document_license_jpg, "rb") as fd:
            myfile = fd.read()

        poller = client.begin_recognize_identity_documents(
            identity_document=myfile,
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
    @DocumentAnalysisClientPreparer()
    def test_identity_document_jpg_passport(self, client):
        with open(self.identity_document_passport_jpg, "rb") as fd:
            id_document = fd.read()

        poller = client.begin_analyze_document("prebuilt-idDocument", id_document)

        result = poller.result()
        assert len(result.documents) == 1

        id_document = result.documents[0]

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
    def test_identity_document_jpg(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()

        poller = client.begin_analyze_document("prebuilt-idDocument", id_document)

        result = poller.result()
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
    def test_identity_document_jpg_include_field_elements(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        poller = client.begin_recognize_identity_documents(id_document, include_field_elements=True)

        result = poller.result()
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
    def test_identity_document_continuation_token(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()

        initial_poller = client.begin_recognize_identity_documents(id_document)
        cont_token = initial_poller.continuation_token()
        poller = client.begin_recognize_identity_documents(None, continuation_token=cont_token)
        result = poller.result()
        self.assertIsNotNone(result)
        initial_poller.wait()  # necessary so azure-devtools doesn't throw assertion error

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer(client_kwargs={"api_version": FormRecognizerApiVersion.V2_0})
    def test_identity_document_v2(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        with pytest.raises(ValueError) as e:
            client.begin_recognize_identity_documents(id_document)
        assert "Method 'begin_recognize_identity_documents' is only available for API version V2_1 and up" in str(e.value)

    @FormRecognizerPreparer()
    @FormRecognizerClientPreparer()
    def test_pages_kwarg_specified(self, client):
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        poller = client.begin_recognize_identity_documents(id_document, pages=["1"])
        assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
        result = poller.result()
        assert result
