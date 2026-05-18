# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Tests for Content Understanding async analyzer operation ID and usage functionality.
"""

from unittest.mock import Mock
from azure.ai.contentunderstanding.aio.models._patch import AnalyzeAsyncLROPoller
from azure.ai.contentunderstanding.models import UsageDetails


class TestAnalyzeAsyncLROPollerUsage:
    """Test the usage property on AnalyzeAsyncLROPoller (async counterpart)."""

    def _make_async_poller_with_usage(self, usage_json, done=True):
        """Helper to create an AnalyzeAsyncLROPoller with a mocked final response."""
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/contentunderstanding/analyzerResults/test-op-id?api-version=2025-11-01"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        mock_final_response = Mock()
        mock_final_http_response = Mock()
        response_json = {
            "id": "test-op-id",
            "status": "Succeeded",
            "result": {"contents": []},
        }
        if usage_json is not None:
            response_json["usage"] = usage_json
        mock_final_http_response.json.return_value = response_json
        mock_final_response.http_response = mock_final_http_response
        mock_polling_method._pipeline_response = mock_final_response

        poller = AnalyzeAsyncLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method,
        )
        # AsyncLROPoller.done() checks self._done (defaults to False after __init__)
        poller._done = done
        return poller

    def test_async_usage_with_full_data(self):
        """Test async usage property returns UsageDetails with all fields populated."""
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
            },
        }

        poller = self._make_async_poller_with_usage(usage_json)
        usage = poller.usage

        assert usage is not None
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard == 2
        assert usage.contextualization_tokens == 1500
        assert usage.tokens == {"gpt-4.1-input": 500, "gpt-4.1-output": 200}

    def test_async_usage_returns_none_when_not_present(self):
        """Test async usage property returns None when usage is not in the response."""
        poller = self._make_async_poller_with_usage(None)
        usage = poller.usage
        assert usage is None

    def test_async_usage_returns_none_before_completion(self):
        """Test async usage property returns None when the polling has not yet completed."""
        poller = self._make_async_poller_with_usage({"documentPagesStandard": 1}, done=False)
        assert not poller.done()
        usage = poller.usage
        assert usage is None
