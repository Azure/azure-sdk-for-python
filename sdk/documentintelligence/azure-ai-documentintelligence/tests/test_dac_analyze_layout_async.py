# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeDocumentRequest
from asynctestcase import AsyncDocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparer as _GlobalClientPreparer


DocumentIntelligenceClientPreparer = functools.partial(_GlobalClientPreparer, DocumentIntelligenceClient)


class TestDACAnalyzeLayoutAsync(AsyncDocumentIntelligenceTest):
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_incorrect_feature_format(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()
        async with client:
            with pytest.raises(TypeError) as e:
                poller = await client.begin_analyze_document(
                    "prebuilt-layout",
                    document,
                    features=DocumentAnalysisFeature.STYLE_FONT,
                    content_type="application/octet-stream",
                )
            assert "features must be type [str]." in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                features=[DocumentAnalysisFeature.STYLE_FONT],
                content_type="application/octet-stream",
            )
            result = await poller.result()
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
    @recorded_by_proxy_async
    async def test_layout_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                content_type="application/octet-stream",
            )
            result = await poller.result()
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
    @recorded_by_proxy_async
    async def test_layout_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout", document, content_type="application/octet-stream"
            )
            result = await poller.result()
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
    @recorded_by_proxy_async
    async def test_layout_multipage_table_span_pdf(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            document = fd.read()
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                content_type="application/octet-stream",
            )
            layout = await poller.result()
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
    @recorded_by_proxy_async
    async def test_layout_url_barcodes(self, client):
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                AnalyzeDocumentRequest(url_source=self.barcode_url_tif),
                features=[DocumentAnalysisFeature.BARCODES],
            )
            layout = await poller.result()
        assert len(layout.pages) > 0
        assert len(layout.pages[0].barcodes) == 2
        assert layout.pages[0].barcodes[0].kind == "Code39"
        assert layout.pages[0].barcodes[0].polygon
        assert layout.pages[0].barcodes[0].confidence > 0.8
    
    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @recorded_by_proxy_async
    async def test_polling_interval(self, documentintelligence_endpoint, documentintelligence_api_key, **kwargs):
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key)
        )
        assert client._config.polling_interval ==  5
        
        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, AzureKeyCredential(documentintelligence_api_key), polling_interval=7
        )
        assert client._config.polling_interval ==  7
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-receipt",
                AnalyzeDocumentRequest(url_source=self.receipt_url_jpg),
                polling_interval=6
            )
            await poller.wait()
            assert poller._polling_method._timeout ==  6
            poller2 = await client.begin_analyze_document(
                "prebuilt-receipt",
                AnalyzeDocumentRequest(url_source=self.receipt_url_jpg),
            )
            await poller2.wait()
            assert poller2._polling_method._timeout ==  7  # goes back to client default
