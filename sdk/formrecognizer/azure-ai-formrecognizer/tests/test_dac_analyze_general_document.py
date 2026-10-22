# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
import sys
from devtools_testutils import recorded_by_proxy
from azure.ai.formrecognizer._generated.models import AnalyzeResultOperation
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.formrecognizer import AnalyzeResult
from preparers import FormRecognizerPreparer, get_sync_client
from testcase import FormRecognizerTest
from conftest import skip_flaky_test


get_da_client = functools.partial(get_sync_client, DocumentAnalysisClient)


class TestDACAnalyzeDocument(FormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_document_stream_transform_pdf(self):
        client = get_da_client()
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        poller = client.begin_analyze_document("prebuilt-document", document, cls=callback)
        result = poller.result()
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
    @recorded_by_proxy
    def test_document_stream_transform_jpg(self):
        client = get_da_client()
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        poller = client.begin_analyze_document("prebuilt-document", document, cls=callback)
        result = poller.result()
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
    @recorded_by_proxy
    def test_document_multipage_transform(self):
        client = get_da_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        poller = client.begin_analyze_document("prebuilt-document", document, cls=callback)
        result = poller.result()
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

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_document_multipage_table_span_pdf(self):
        client = get_da_client()
        with open(self.multipage_table_pdf, "rb") as fd:
            my_file = fd.read()
        poller = client.begin_analyze_document("prebuilt-document", my_file)
        document = poller.result()
        assert len(document.tables) == 3
        assert document.tables[0].row_count == 30
        assert document.tables[0].column_count == 5
        assert document.tables[1].row_count == 6
        assert document.tables[1].column_count == 5
        assert document.tables[2].row_count == 24
        assert document.tables[2].column_count == 5

    @skip_flaky_test
    @FormRecognizerPreparer()
    @recorded_by_proxy
    def test_document_specify_pages(self):
        client = get_da_client()
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document("prebuilt-document", document, pages="1")
        result = poller.result()
        assert len(result.pages) == 1

        poller = client.begin_analyze_document("prebuilt-document", document, pages="1, 3")
        result = poller.result()
        assert len(result.pages) == 2

        poller = client.begin_analyze_document("prebuilt-document", document, pages="1-2")
        result = poller.result()
        assert len(result.pages) == 2

        poller = client.begin_analyze_document("prebuilt-document", document, pages="1-2, 3")
        result = poller.result()
        assert len(result.pages) == 3
