# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeDocumentRequest
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

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            features=[DocumentAnalysisFeature.STYLE_FONT],
            content_type="application/octet-stream",
        )
        result = poller.result()
        assert result.model_id == "prebuilt-layout"
        assert len(result.pages) == 1
        assert len(result.tables) == 1
        assert len(result.paragraphs) == 15
        assert len(result.styles) == 20
        assert result.string_index_type == "textElements"
        assert result.content_format == "text"

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
        )
        result = poller.result()
        assert result.model_id == "prebuilt-layout"
        assert len(result.pages) == 1
        assert len(result.tables) == 2
        assert len(result.paragraphs) == 41
        assert len(result.styles) == 1
        assert result.string_index_type == "textElements"
        assert result.content_format == "text"

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy
    def test_layout_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        poller = client.begin_analyze_document(
            "prebuilt-layout",
            document,
            content_type="application/octet-stream",
        )
        result = poller.result()
        assert result.model_id == "prebuilt-layout"
        assert len(result.pages) == 2
        assert len(result.tables) == 1
        assert len(result.paragraphs) == 40
        assert len(result.styles) == 0
        assert result.string_index_type == "textElements"
        assert result.content_format == "text"

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
