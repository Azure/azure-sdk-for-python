# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer._generated.v2022_06_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer.aio import DocumentAnalysisClient, DocumentModelAdministrationClient
from azure.ai.formrecognizer._generated.v2022_06_30_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer import AnalyzeResult
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)

class TestDACAnalyzeCustomModelAsync(AsyncFormRecognizerTest):

    @FormRecognizerPreparer()
    async def test_analyze_document_none_model_id(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with pytest.raises(ValueError):
            async with client:
                await client.begin_analyze_document(model_id=None, document=b"xx")

    @FormRecognizerPreparer()
    async def test_analyze_document_empty_model_id(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with pytest.raises(ValueError):
            async with client:
                await client.begin_analyze_document(model_id="", document=b"xx")

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_document_transform(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()

        async with client:
            build_polling = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await build_polling.result()

            async with da_client:
                poller = await da_client.begin_analyze_document(
                    model.model_id,
                    my_file,
                    cls=callback
                )
                document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_document_multipage_transform(self, client, formrecognizer_multipage_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        with open(self.multipage_invoice_pdf, "rb") as fd:
            my_file = fd.read()

        async with client:
            build_poller = await client.begin_build_model("template", blob_container_url=formrecognizer_multipage_storage_container_sas_url)
            model = await build_poller.result()

            async with da_client:
                poller = await da_client.begin_analyze_document(
                    model.model_id,
                    my_file,
                    cls=callback
                )
                document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_document_selection_mark(self, client, formrecognizer_selection_mark_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()
        with open(self.selection_form_pdf, "rb") as fd:
            my_file = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        async with client:
            poller = await client.begin_build_model("template", blob_container_url=formrecognizer_selection_mark_storage_container_sas_url)
            model = await poller.result()

            poller = await da_client.begin_analyze_document(
                model.model_id,
                my_file,
                cls=callback
            )
            document = await poller.result()

        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_pages_kwarg_specified(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()

        async with client:
            build_poller = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await build_poller.result()

            async with da_client:
                poller = await da_client.begin_analyze_document(model.model_id, my_file, pages="1")
                assert '1' == poller._polling_method._initial_response.http_response.request.query['pages']
                result = await poller.result()
                assert result

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_document_signature_field(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        with open(self.form_jpg, "rb") as fd:
            my_file = fd.read()

        async with client:
            build_polling = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url, )
            model = await build_polling.result()

            async with da_client:
                poller = await da_client.begin_analyze_document(
                    model.model_id,
                    my_file,
                )
                result = await poller.result()

        assert result.documents[0].fields.get("FullSignature").value == "signed"
        assert result.documents[0].fields.get("FullSignature").value_type == "signature"
        # this will notify us of changes in the service, currently expecting to get a None content for signature type fields
        assert result.documents[0].fields.get("FullSignature").content == None

    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy_async
    async def test_custom_document_blank_pdf(self, client, formrecognizer_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        with open(self.blank_pdf, "rb") as fd:
            my_file = fd.read()

        async with client:
            build_polling = await client.begin_build_model("template", blob_container_url=formrecognizer_storage_container_sas_url)
            model = await build_polling.result()

            async with da_client:
                poller = await da_client.begin_analyze_document(
                    model.model_id,
                    my_file,
                )
                result = await poller.result()

        assert result is not None
        assert len(result.pages) == 1
        assert len(result.pages[0].lines) == 0
