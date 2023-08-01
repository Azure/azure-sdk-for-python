# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, DocumentModelAdministrationClient, AnalyzeResult
from azure.ai.formrecognizer._generated.v2023_07_31.models import AnalyzeResultOperation
from testcase import FormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from preparers import FormRecognizerPreparer
from conftest import skip_flaky_test

DocumentModelAdministrationClientPreparer = functools.partial(_GlobalClientPreparer, DocumentModelAdministrationClient)

class TestDACAnalyzeCustomModelFromUrl(FormRecognizerTest):

    @FormRecognizerPreparer()
    def test_document_analysis_none_model(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document_from_url(model_id=None, document_url="https://badurl.jpg")
        assert "model_id cannot be None or empty." in str(e.value)

    @FormRecognizerPreparer()
    def test_document_analysis_empty_model_id(self, **kwargs):
        formrecognizer_test_endpoint = kwargs.pop("formrecognizer_test_endpoint")
        formrecognizer_test_api_key = kwargs.pop("formrecognizer_test_api_key")
        client = DocumentAnalysisClient(formrecognizer_test_endpoint, AzureKeyCredential(formrecognizer_test_api_key))
        with pytest.raises(ValueError) as e:
            client.begin_analyze_document_from_url(model_id="", document_url="https://badurl.jpg")
        assert "model_id cannot be None or empty." in str(e.value)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_custom_document_selection_mark(self, client, formrecognizer_selection_mark_storage_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_selection_mark_storage_container_sas_url)
        model = poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        poller = da_client.begin_analyze_document_from_url(
            model_id=model.model_id,
            document_url=self.selection_mark_url_pdf,
            cls=callback
        )
        document = poller.result()

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

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_label_tables_variable_rows(self, client, formrecognizer_table_variable_rows_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        build_poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_table_variable_rows_container_sas_url)
        model = build_poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        poller = da_client.begin_analyze_document_from_url(
            model.model_id,
            self.label_table_variable_row_url_pdf,
            cls=callback
        )
        document = poller.result()
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

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentModelAdministrationClientPreparer()
    @recorded_by_proxy
    def test_label_tables_fixed_rows(self, client, formrecognizer_table_fixed_rows_container_sas_url, **kwargs):
        set_bodiless_matcher()
        da_client = client.get_document_analysis_client()

        build_poller = client.begin_build_document_model("template", blob_container_url=formrecognizer_table_fixed_rows_container_sas_url)
        model = build_poller.result()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = da_client._deserialize(AnalyzeResultOperation, raw_response)
            document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(document)

        poller = da_client.begin_analyze_document_from_url(
            model.model_id,
            self.label_table_fixed_row_url_pdf,
            cls=callback
        )
        document = poller.result()
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
