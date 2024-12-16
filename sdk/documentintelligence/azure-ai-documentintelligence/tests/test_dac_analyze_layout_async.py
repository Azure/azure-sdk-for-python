# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils import get_credential, set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    DocumentAnalysisFeature,
    AnalyzeDocumentRequest,
    AnalyzeResult,
    AnalyzeOutputOption,
)
from asynctestcase import AsyncDocumentIntelligenceTest
from conftest import skip_flaky_test
from preparers import DocumentIntelligencePreparer, GlobalClientPreparerAsync as _GlobalClientPreparer


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
                )
            assert "features must be type [str]." in str(e.value)

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                features=[DocumentAnalysisFeature.STYLE_FONT],
                cls=callback,
            )
            raw_response = await poller.result()
            raw_analyze_result = AnalyzeResult._deserialize(raw_response.http_response.json()["analyzeResult"], [])

            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                features=[DocumentAnalysisFeature.STYLE_FONT],
            )
            returned_model = await poller.result()

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
    @recorded_by_proxy_async
    async def test_layout_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                cls=callback,
            )
            raw_response = await poller.result()
            raw_analyze_result = AnalyzeResult._deserialize(raw_response.http_response.json()["analyzeResult"], [])

            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
            )
            returned_model = await poller.result()

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
    @recorded_by_proxy_async
    async def test_layout_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        def callback(raw_response, _, headers):
            return raw_response

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                cls=callback,
            )
            raw_response = await poller.result()
            raw_analyze_result = AnalyzeResult._deserialize(raw_response.http_response.json()["analyzeResult"], [])

            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
            )
            returned_model = await poller.result()

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
    @recorded_by_proxy_async
    async def test_layout_multipage_table_span_pdf(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            document = fd.read()
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
            )
            layout = await poller.result()
        assert len(layout.tables) == 3
        assert layout.tables[0].row_count == 30
        assert layout.tables[0].column_count == 5
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count == 5
        assert layout.tables[2].row_count == 24
        assert layout.tables[2].column_count == 5

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_multipage_table_span_pdf_continuation_token(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            document = fd.read()
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
            )
            continuation_token = poller.continuation_token()
            layout = await (
                await client.begin_analyze_document(None, None, continuation_token=continuation_token)
            ).result()
        assert len(layout.tables) == 3
        assert layout.tables[0].row_count == 30
        assert layout.tables[0].column_count == 5
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count == 5
        assert layout.tables[2].row_count == 24
        assert layout.tables[2].column_count == 5

    @skip_flaky_test
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_url_barcodes(self, client):
        set_bodiless_matcher()
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
    async def test_polling_interval(self, documentintelligence_endpoint, **kwargs):
        client = DocumentIntelligenceClient(documentintelligence_endpoint, get_credential(is_async=True))
        assert client._config.polling_interval == 1

        client = DocumentIntelligenceClient(
            documentintelligence_endpoint, get_credential(is_async=True), polling_interval=7
        )
        assert client._config.polling_interval == 7
        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-receipt", AnalyzeDocumentRequest(url_source=self.receipt_url_jpg), polling_interval=6
            )
            await poller.wait()
            assert poller._polling_method._timeout == 6
            poller2 = await client.begin_analyze_document(
                "prebuilt-receipt",
                AnalyzeDocumentRequest(url_source=self.receipt_url_jpg),
            )
            await poller2.wait()
            assert poller2._polling_method._timeout == 7  # goes back to client default

    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_get_analyze_result_pdf(self, client):
        with open(self.layout_sample, "rb") as fd:
            document = fd.read()
        poller = await client.begin_analyze_document(
            "prebuilt-read",
            document,
            output=[AnalyzeOutputOption.PDF],
        )
        result = await poller.result()
        response = await client.get_analyze_result_pdf(
            model_id=result.model_id, result_id=poller.details["operation_id"]
        )
        first_chunk_pdf_bytes = await response.__anext__()
        assert first_chunk_pdf_bytes.startswith(b"%PDF-")  # A PDF's header is expected to be: %PDF-

    @pytest.mark.live_test_only("Needs to remove sanitizer on figure id in request url.")
    @DocumentIntelligencePreparer()
    @DocumentIntelligenceClientPreparer()
    @recorded_by_proxy_async
    async def test_get_analyze_result_figures(self, client):
        with open(self.layout_sample, "rb") as fd:
            document = fd.read()
        poller = await client.begin_analyze_document(
            "prebuilt-layout",
            document,
            output=[AnalyzeOutputOption.FIGURES],
        )
        result = await poller.result()
        assert result.figures is not None
        figure_id = result.figures[0].id
        response = await client.get_analyze_result_figure(
            model_id=result.model_id, result_id=poller.details["operation_id"], figure_id=figure_id
        )
        first_chunk_figure_bytes = await response.__anext__()
        assert first_chunk_figure_bytes.startswith(b"\x89PNG")  # A PNG's header is expected to start with: ‰PNG
