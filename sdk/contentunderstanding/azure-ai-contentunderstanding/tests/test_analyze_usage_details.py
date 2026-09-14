# pylint: disable=line-too-long,useless-suppression,protected-access
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Offline and live tests for analyze usage details (AnalyzeLROPoller.usage and
ContentAnalyzerInlineResponse.usage).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from devtools_testutils import is_live

from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    ContentAnalyzerInlineResponse,
    UsageDetails,
)
from azure.ai.contentunderstanding.models._patch import AnalyzeLROPoller
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from testpreparer_async import ContentUnderstandingClientTestBaseAsync

_INVOICE_URL = (
    "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/" "main/document/invoice.pdf"
)
_INLINE_LAYOUT_URL = (
    "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/" "refs/heads/main/data/invoice.pdf"
)


def _make_poller_with_usage(usage_json: Any) -> AnalyzeLROPoller[Any]:
    """Build an AnalyzeLROPoller whose final response envelope includes usage."""
    mock_polling_method = Mock()
    mock_initial_response = Mock()
    mock_http_response = Mock()
    mock_http_response.headers = {
        "Operation-Location": (
            "https://endpoint/contentunderstanding/analyzerResults/test-op-id" "?api-version=2026-06-01-preview"
        )
    }
    mock_initial_response.http_response = mock_http_response
    mock_polling_method.return_value = mock_polling_method
    mock_polling_method._initial_response = mock_initial_response

    mock_final_response = Mock()
    mock_final_http_response = Mock()
    response_json: dict[str, Any] = {
        "id": "test-op-id",
        "status": "Succeeded",
        "result": {"contents": []},
    }
    if usage_json is not None:
        response_json["usage"] = usage_json
    mock_final_http_response.json.return_value = response_json
    mock_final_response.http_response = mock_final_http_response
    mock_polling_method._pipeline_response = mock_final_response

    return AnalyzeLROPoller(
        client=Mock(),
        initial_response=Mock(),
        deserialization_callback=Mock(),
        polling_method=mock_polling_method,
    )


def _assert_lro_page_meter_present(usage: UsageDetails) -> None:
    has_pages = (
        (usage.document_pages_standard is not None and usage.document_pages_standard > 0)
        or (usage.document_pages_basic is not None and usage.document_pages_basic > 0)
        or (usage.document_pages_minimal is not None and usage.document_pages_minimal > 0)
    )
    assert has_pages, "LRO usage should report at least one document page meter"


class TestAnalyzeUsageDetailsOffline:
    """Unit tests for usage deserialization on AnalyzeLROPoller."""

    def test_usage_with_full_data(self) -> None:
        usage_json = {
            "documentPagesMinimal": 0,
            "documentPagesBasic": 0,
            "documentPagesStandard": 2,
            "audioHours": 0.0,
            "videoHours": 0.0,
            "contextualizationTokens": 1500,
            "tokens": {
                "gpt-4.1-input": 500,
                "gpt-4.1-output": 200,
                "text-embedding-3-large-input": 300,
            },
        }
        usage = _make_poller_with_usage(usage_json).usage
        assert usage is not None
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard == 2
        assert usage.contextualization_tokens == 1500
        assert usage.tokens == {
            "gpt-4.1-input": 500,
            "gpt-4.1-output": 200,
            "text-embedding-3-large-input": 300,
        }

    def test_usage_with_inline_and_advanced_meters(self) -> None:
        usage_json = {
            "documentPagesStandardInline": 2,
            "contextualizationTokens": 1500,
            "advancedContextualizationTokens": 800,
            "tokens": {"gpt-5.2-input": 500, "gpt-5.2-output": 200},
        }
        usage = _make_poller_with_usage(usage_json).usage
        assert usage is not None
        assert usage.document_pages_standard_inline == 2
        assert usage.document_pages_standard is None
        assert usage.advanced_contextualization_tokens == 800

    def test_usage_lro_style_does_not_set_inline_meters(self) -> None:
        usage = _make_poller_with_usage({"documentPagesStandard": 2, "contextualizationTokens": 1000}).usage
        assert usage is not None
        assert usage.document_pages_standard == 2
        assert usage.document_pages_standard_inline is None

    def test_usage_inline_style_sets_inline_meters(self) -> None:
        usage = _make_poller_with_usage({"documentPagesStandardInline": 1, "contextualizationTokens": 500}).usage
        assert usage is not None
        assert usage.document_pages_standard_inline == 1
        assert usage.document_pages_standard is None

    def test_usage_with_partial_data(self) -> None:
        usage = _make_poller_with_usage({"documentPagesStandard": 1, "contextualizationTokens": 100}).usage
        assert usage is not None
        assert usage.document_pages_standard == 1
        assert usage.document_pages_minimal is None
        assert usage.tokens is None

    def test_usage_returns_none_when_not_present(self) -> None:
        assert _make_poller_with_usage(None).usage is None

    def test_usage_returns_none_before_completion(self) -> None:
        poller = AnalyzeLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=Mock(),
        )
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        poller._thread = mock_thread
        assert not poller.done()
        assert poller.usage is None

    def test_usage_with_empty_dict(self) -> None:
        usage = _make_poller_with_usage({}).usage
        assert usage is not None
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard is None
        assert usage.tokens is None

    def test_usage_with_null_fields_and_float_hours(self) -> None:
        usage = _make_poller_with_usage(
            {
                "documentPagesStandard": None,
                "audioHours": 1.5,
                "videoHours": 0.25,
                "contextualizationTokens": None,
                "tokens": {},
            }
        ).usage
        assert usage is not None
        assert usage.document_pages_standard is None
        assert usage.audio_hours == 1.5
        assert usage.video_hours == 0.25
        assert usage.tokens == {}

    def test_usage_with_empty_tokens(self) -> None:
        usage = _make_poller_with_usage({"tokens": {}}).usage
        assert usage is not None
        assert usage.tokens == {}

    def test_usage_repeated_reads_are_idempotent(self) -> None:
        poller = _make_poller_with_usage(
            {
                "documentPagesStandard": 3,
                "tokens": {"gpt-5.2-input": 10},
            }
        )
        first = poller.usage
        second = poller.usage
        assert first is not None and second is not None
        assert first.document_pages_standard == second.document_pages_standard == 3
        assert first.tokens == second.tokens == {"gpt-5.2-input": 10}

    def test_usage_zero_valued_fields_are_distinct_from_null(self) -> None:
        usage = _make_poller_with_usage(
            {
                "documentPagesMinimal": 0,
                "documentPagesBasic": 0,
                "documentPagesStandard": 0,
                "audioHours": 0.0,
                "videoHours": 0.0,
                "contextualizationTokens": 0,
                "tokens": {"gpt-5.2-input": 0},
            }
        ).usage
        assert usage is not None
        assert usage.document_pages_minimal == 0
        assert usage.document_pages_standard == 0
        assert usage.contextualization_tokens == 0
        assert usage.tokens == {"gpt-5.2-input": 0}

    def test_usage_with_multiple_token_models(self) -> None:
        usage = _make_poller_with_usage(
            {
                "tokens": {
                    "gpt-5.2-input": 1000,
                    "gpt-5.2-cached_input": 200,
                    "gpt-5.2-output": 300,
                    "text-embedding-3-large-input": 500,
                }
            }
        ).usage
        assert usage is not None
        assert usage.tokens is not None
        assert len(usage.tokens) == 4
        assert usage.tokens["gpt-5.2-cached_input"] == 200

    def test_usage_with_unknown_json_properties_ignored(self) -> None:
        usage = _make_poller_with_usage(
            {
                "documentPagesStandard": 1,
                "futureField": "some-value",
                "anotherNewField": 42,
            }
        ).usage
        assert usage is not None
        assert usage.document_pages_standard == 1
        assert usage.document_pages_minimal is None

    def test_usage_with_integer_audio_hours_parses_as_float(self) -> None:
        usage = _make_poller_with_usage({"audioHours": 2, "videoHours": 3}).usage
        assert usage is not None
        assert usage.audio_hours == 2
        assert usage.video_hours == 3

    def test_inline_response_usage_property(self) -> None:
        """ContentAnalyzerInlineResponse exposes usage on the deserialized envelope."""
        inline = ContentAnalyzerInlineResponse(
            {
                "status": "Succeeded",
                "result": {
                    "analyzerId": "prebuilt-layout",
                    "apiVersion": "2026-06-01-preview",
                    "contents": [],
                },
                "usage": {
                    "documentPagesStandardInline": 1,
                    "contextualizationTokens": 250,
                },
            }
        )
        usage = inline.usage
        assert usage is not None
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard_inline == 1
        assert usage.document_pages_standard is None
        assert usage.contextualization_tokens == 250

    def test_usage_malformed_string_does_not_raise(self) -> None:
        usage = _make_poller_with_usage("not-a-usage-object").usage
        assert usage == "not-a-usage-object" or usage is None
        assert not isinstance(usage, UsageDetails)


class TestAnalyzeUsageDetailsLive(ContentUnderstandingClientTestBase):
    """Live tests that run when AZURE_TEST_RUN_LIVE is enabled."""

    @ContentUnderstandingPreparer()
    def test_lro_invoice_usage_after_completion(self, **kwargs) -> None:
        if not is_live():
            pytest.skip("Live-only: validates real service usage on analyze LRO.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_client(endpoint=endpoint)

        poller = client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalysisInput(url=_INVOICE_URL)],
        )
        assert poller.usage is None, "Usage must be None before LRO completes"
        result = poller.result()
        assert result is not None

        usage = poller.usage
        assert usage is not None, "Usage details should be available after LRO completes"
        assert isinstance(usage, UsageDetails)
        _assert_lro_page_meter_present(usage)
        assert usage.document_pages_standard_inline is None
        assert usage.document_pages_minimal_inline is None
        assert usage.document_pages_basic_inline is None
        if usage.tokens:
            assert len(usage.tokens) > 0
            for model, count in usage.tokens.items():
                assert isinstance(model, str)
                assert isinstance(count, int)
                assert count >= 0

        # Idempotent read after completion
        assert poller.usage == usage

    @pytest.mark.preview
    @ContentUnderstandingPreparer()
    def test_inline_layout_usage_on_response(self, **kwargs) -> None:
        if not is_live():
            pytest.skip("Live-only: validates real service usage on inline analyze.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_client(endpoint=endpoint)

        inline_response = client.analyze_inline(
            analyzer_id="prebuilt-layout",
            inputs=[AnalysisInput(url=_INLINE_LAYOUT_URL)],
        )
        usage = inline_response.usage
        assert usage is not None, "Inline usage should be on ContentAnalyzerInlineResponse"
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard_inline is not None
        assert usage.document_pages_standard_inline > 0
        assert usage.document_pages_standard is None
        assert usage.document_pages_minimal_inline is None
        assert usage.document_pages_basic_inline is None


class TestAnalyzeUsageDetailsLiveAsync(ContentUnderstandingClientTestBaseAsync):
    """Async live usage on analyze LRO."""

    @pytest.mark.preview
    @ContentUnderstandingPreparer()
    async def test_async_lro_invoice_usage_after_completion(self, **kwargs) -> None:
        if not is_live():
            pytest.skip("Live-only: validates async poller.usage against the configured service.")
        endpoint = kwargs.pop("contentunderstanding_endpoint")
        client = self.create_preview_async_client(endpoint=endpoint)

        async with client:
            poller = await client.begin_analyze(
                analyzer_id="prebuilt-invoice",
                inputs=[AnalysisInput(url=_INVOICE_URL)],
            )
            assert poller.usage is None
            result = await poller.result()
            assert result is not None

            usage = poller.usage
            assert usage is not None
            assert isinstance(usage, UsageDetails)
            _assert_lro_page_meter_present(usage)
