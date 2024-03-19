# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    DocumentAnalysisFeature,
    AnalyzeDocumentRequest,
    AnalyzeResultOperation,
)
from testcase import DocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer


DocumentIntelligenceClientPreparer = functools.partial(_GlobalClientPreparer, DocumentIntelligenceClient)


class TestDACAnalyzeLayout(DocumentIntelligenceTest):
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_incorrect_feature_format(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        with pytest.raises(TypeError) as e:
            poller = client.begin_analyze_document(
                "prebuilt-layout",
                document,
                features=DocumentAnalysisFeature.STYLE_FONT,
                content_type="application/octet-stream",
            )
        assert "features must be type [str]." in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            features=[DocumentAnalysisFeature.STYLE_FONT],
            content_type="application/octet-stream",
            cls=callback,
        )
        raw_response = poller.result()
        raw_analyze_result = AnalyzeResultOperation._deserialize(raw_response.http_response.json(), []).analyze_result

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            features=[DocumentAnalysisFeature.STYLE_FONT],
            content_type="application/octet-stream",
        )
        returned_model = poller.result()

        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        assert len(returned_model.pages) == len(raw_analyze_result.pages)
        assert len(returned_model.tables) == len(raw_analyze_result.tables)
        assert len(returned_model.paragraphs) == len(raw_analyze_result.paragraphs)
        assert len(returned_model.styles) == len(raw_analyze_result.styles)

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(
            returned_model.key_value_pairs, raw_analyze_result.key_value_pairs
        )
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
            cls=callback,
        )
        raw_response = poller.result()
        raw_analyze_result = AnalyzeResultOperation._deserialize(raw_response.http_response.json(), []).analyze_result

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
        )
        returned_model = poller.result()

        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        assert len(returned_model.pages) == len(raw_analyze_result.pages)
        assert len(returned_model.tables) == len(raw_analyze_result.tables)
        assert len(returned_model.paragraphs) == len(raw_analyze_result.paragraphs)
        assert len(returned_model.styles) == len(raw_analyze_result.styles)

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(
            returned_model.key_value_pairs, raw_analyze_result.key_value_pairs
        )
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
            cls=callback,
        )
        raw_response = poller.result()
        raw_analyze_result = AnalyzeResultOperation._deserialize(raw_response.http_response.json(), []).analyze_result

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
        )
        returned_model = poller.result()

        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content

        assert len(returned_model.pages) == len(raw_analyze_result.pages)
        assert len(returned_model.tables) == len(raw_analyze_result.tables)
        assert len(returned_model.paragraphs) == len(raw_analyze_result.paragraphs)
        assert len(returned_model.styles) == len(raw_analyze_result.styles)

        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(
            returned_model.key_value_pairs, raw_analyze_result.key_value_pairs
        )
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_multipage_table_span_pdf(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            document = fd.read()
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
        )
        layout = poller.result()
        assert len(layout.tables) == 3
        assert layout.tables[0].row_count == 30
        assert layout.tables[0].column_count == 5
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count == 5
        assert layout.tables[2].row_count == 24
        assert layout.tables[2].column_count == 5

    @pytest.mark.live_test_only
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_url_barcode(self, client):
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(url_source=self.barcode_url_tif),
            features=[DocumentAnalysisFeature.BARCODES],
        )
        layout = poller.result()
        assert len(layout.pages) > 0
        assert len(layout.pages[0].barcodes) == 2
        assert layout.pages[0].barcodes[0].kind == "Code39"
        assert layout.pages[0].barcodes[0].polygon
        assert layout.pages[0].barcodes[0].confidence > 0.8

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy
    def test_polling_interval(self, documentintelligence_endpoint, documentintelligence_api_key, **kwargs):
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        assert client._config.polling_interval == 5

        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key), polling_interval=7
        )
        assert client._config.polling_interval == 7
        poller = client.begin_analyze_document(
            "prebuilt-receipt", AnalyzeDocumentRequest(url_source=self.receipt_url_jpg), polling_interval=6
        )
        poller.wait()
        assert poller._polling_method._timeout == 6
        poller2 = client.begin_analyze_document(
            "prebuilt-receipt",
            AnalyzeDocumentRequest(url_source=self.receipt_url_jpg),
        )
        poller2.wait()
        assert poller2._polling_method._timeout == 7  # goes back to client default
