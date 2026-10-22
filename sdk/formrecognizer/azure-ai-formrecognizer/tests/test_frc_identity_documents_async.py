# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from io import BytesIO
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import ServiceRequestError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2_1.models import AnalyzeOperationResult
from azure.ai.formrecognizer._response_handlers import prepare_prebuilt_models
from azure.ai.formrecognizer.aio import FormRecognizerClient
from azure.ai.formrecognizer import FormRecognizerApiVersion
from asynctestcase import AsyncFormRecognizerTest
from preparers import FormRecognizerPreparer, get_async_client
from conftest import skip_flaky_test

get_fr_client = functools.partial(get_async_client, FormRecognizerClient)


class TestIdDocumentsAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_identity_document_bad_endpoint(self, **kwargs):
        formrecognizer_test_api_key = "fakeZmFrZV9hY29jdW50X2tleQ=="
        with open(self.identity_document_license_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ServiceRequestError):
            client = FormRecognizerClient("http://notreal.azure.com", AzureKeyCredential(formrecognizer_test_api_key))
            async with client:
                poller = await client.begin_recognize_identity_documents(my_file)

    @FormRecognizerPreparer()
    async def test_damaged_file_bytes_fails_autodetect_content_type(self, **kwargs):
        client = get_fr_client()
        damaged_pdf = b"\x50\x44\x46\x55\x55\x55"  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_identity_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    async def test_damaged_file_bytes_io_fails_autodetect(self, **kwargs):
        client = get_fr_client()
        damaged_pdf = BytesIO(b"\x50\x44\x46\x55\x55\x55")  # doesn't match any magic file numbers
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_identity_documents(
                    damaged_pdf
                )

    @FormRecognizerPreparer()
    async def test_passing_bad_content_type_param_passed(self, **kwargs):
        client = get_fr_client()
        with open(self.identity_document_license_jpg, "rb") as fd:
            my_file = fd.read()
        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_identity_documents(
                    my_file,
                    content_type="application/jpeg"
                )

    @FormRecognizerPreparer()
    async def test_auto_detect_unsupported_stream_content(self, **kwargs):
        client = get_fr_client()
        with open(self.unsupported_content_py, "rb") as fd:
            my_file = fd.read()

        with pytest.raises(ValueError):
            async with client:
                poller = await client.begin_recognize_identity_documents(
                    my_file
                )

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_identity_document_stream_transform_jpg(self):
        client = get_fr_client()
        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_id_document = prepare_prebuilt_models(analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_id_document)

        with open(self.identity_document_license_jpg, "rb") as fd:
            my_file = fd.read()

        async with client:
            poller = await client.begin_recognize_identity_documents(
                identity_document=my_file,
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
        assert id_document.page_range.first_page_number ==  document_results[0].page_range[0]
        assert id_document.page_range.last_page_number ==  document_results[0].page_range[1]

        # Check page metadata
        self.assertFormPagesTransformCorrect(id_document.pages, read_results, page_results)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_identity_document_jpg_include_field_elements(self):
        client = get_fr_client()
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            poller = await client.begin_recognize_identity_documents(id_document, include_field_elements=True)

            result = await poller.result()
        assert len(result) == 1
        id_document = result[0]

        self.assertFormPagesHasValues(id_document.pages)

        for field in id_document.fields.values():
            if field.name == "CountryRegion":
                assert field.value ==  "USA"
                continue
            elif field.name == "Region":
                assert field.value ==  "Washington"
            else:
                self.assertFieldElementsHasValues(field.value_data.field_elements, id_document.page_range.first_page_number)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    async def test_identity_document_continuation_token(self, **kwargs):
        client = get_fr_client()
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            initial_poller = await client.begin_recognize_identity_documents(id_document)
            cont_token = initial_poller.continuation_token()
            poller = await client.begin_recognize_identity_documents(None, continuation_token=cont_token)
            result = await poller.result()
            assert result is not None
            await initial_poller.wait()  # necessary so devtools_testutils doesn't throw assertion error

    @FormRecognizerPreparer()
    async def test_identity_document_v2(self, **kwargs):
        client = get_fr_client(api_version=FormRecognizerApiVersion.V2_0)
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        with pytest.raises(ValueError) as e:
            async with client:
                await client.begin_recognize_identity_documents(id_document)
        assert "Method 'begin_recognize_identity_documents' is only available for API version V2_1 and up" in str(e.value)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self):
        client = get_fr_client()
        with open(self.identity_document_license_jpg, "rb") as fd:
            id_document = fd.read()
        async with client:
            poller = await client.begin_recognize_identity_documents(id_document, pages=["1"])
            assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
            result = await poller.result()
            assert result
