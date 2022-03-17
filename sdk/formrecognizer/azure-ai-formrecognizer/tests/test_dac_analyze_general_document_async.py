# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.formrecognizer._generated.models import AnalyzeResultOperation
from azure.ai.formrecognizer.aio import DocumentAnalysisClient
from azure.ai.formrecognizer import AnalyzeResult
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestDACAnalyzeDocumentAsync(AsyncFormRecognizerTest):

    def teardown(self):
        self.sleep(4)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_document_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        async with client:
            poller = await client.begin_analyze_document("prebuilt-document", document, cls=callback)
            result = await poller.result()
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
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_document_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        async with client:
            poller = await client.begin_analyze_document("prebuilt-document", document, cls=callback)
            result = await poller.result()
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
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_document_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_document = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_document)

        async with client:
            poller = await client.begin_analyze_document("prebuilt-document", document, cls=callback)
            result = await poller.result()
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
        self.assertDocumentEntitiesTransformCorrect(returned_model.entities, raw_analyze_result.entities)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @pytest.mark.live_test_only
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_document_multipage_table_span_pdf(self, client, **kwargs):

        with open(self.multipage_table_pdf, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_analyze_document("prebuilt-document", my_file)
            document = await poller.result()
        assert len(document.tables) == 3
        assert document.tables[0].row_count == 30
        assert document.tables[0].column_count == 5
        assert document.tables[1].row_count == 6
        assert document.tables[1].column_count == 5
        assert document.tables[2].row_count == 23
        assert document.tables[2].column_count == 5

    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_document_specify_pages(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        async with client:
            poller = await client.begin_analyze_document("prebuilt-document", document, pages="1")
            result = await poller.result()
            assert len(result.pages) == 1

            poller = await client.begin_analyze_document("prebuilt-document", document, pages="1, 3")
            result = await poller.result()
            assert len(result.pages) == 2

            poller = await client.begin_analyze_document("prebuilt-document", document, pages="1-2")
            result = await poller.result()
            assert len(result.pages) == 2

            poller = await client.begin_analyze_document("prebuilt-document", document, pages="1-2, 3")
            result = await poller.result()
            assert len(result.pages) == 3
