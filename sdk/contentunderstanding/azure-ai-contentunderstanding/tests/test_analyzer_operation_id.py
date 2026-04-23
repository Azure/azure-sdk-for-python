# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Tests for Content Understanding analyzer operation ID functionality.
"""

import pytest
from unittest.mock import Mock, patch
from azure.core.polling import LROPoller, PollingMethod
from azure.ai.contentunderstanding.models._patch import (
    AnalyzeLROPoller,
    _parse_operation_id,
)
from azure.ai.contentunderstanding.models import AnalysisInput, UsageDetails
from azure.ai.contentunderstanding import ContentUnderstandingClient


class TestParseOperationId:
    """Test the operation ID parsing function."""

    def test_parse_analyze_operation_id(self):
        """Test parsing operation ID from analyze operation location."""
        url = "https://endpoint/contentunderstanding/analyzerResults/12345-67890-abcdef?api-version=2025-11-01"
        operation_id = _parse_operation_id(url)
        assert operation_id == "12345-67890-abcdef"

    def test_parse_operation_id_with_different_endpoints(self):
        """Test parsing operation ID from different endpoint formats."""
        urls = [
            "https://ai-foundry-mock.services.ai.azure.com/contentunderstanding/analyzerResults/b0fdb7d6-6fa7-4b43-af09-1b14e84cedce?api-version=2025-11-01",
            "https://my-resource.cognitiveservices.azure.com/contentunderstanding/analyzerResults/abc123?api-version=2025-11-01",
            "https://localhost:8080/contentunderstanding/analyzerResults/test-op-id?api-version=2025-11-01",
        ]

        expected_ids = ["b0fdb7d6-6fa7-4b43-af09-1b14e84cedce", "abc123", "test-op-id"]

        for url, expected_id in zip(urls, expected_ids):
            operation_id = _parse_operation_id(url)
            assert operation_id == expected_id

    def test_parse_operation_id_no_match(self):
        """Test parsing operation ID when no match is found."""
        url = "https://endpoint/contentunderstanding/something-else/12345?api-version=2025-11-01"

        with pytest.raises(ValueError, match="Could not extract operation ID"):
            _parse_operation_id(url)


class TestAnalyzeLROPoller:
    """Test the AnalyzeLROPoller class."""

    def test_operation_id_property_success(self):
        """Test the operation_id property when operation ID can be extracted."""
        # Mock the polling method and initial response
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/contentunderstanding/analyzerResults/test-op-id?api-version=2025-11-01"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create poller instance
        poller = AnalyzeLROPoller(
            client=Mock(), initial_response=Mock(), deserialization_callback=Mock(), polling_method=mock_polling_method
        )

        # Test operation_id property
        operation_id = poller.operation_id
        assert operation_id == "test-op-id"

    def test_operation_id_property_missing_header(self):
        """Test the operation_id property when Operation-Location header is missing."""
        # Mock the polling method and initial response
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {}  # Missing Operation-Location header
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create poller instance
        poller = AnalyzeLROPoller(
            client=Mock(), initial_response=Mock(), deserialization_callback=Mock(), polling_method=mock_polling_method
        )

        # Test operation_id property raises ValueError when header is missing
        with pytest.raises(ValueError, match="Could not extract operation ID"):
            _ = poller.operation_id

    def test_operation_id_property_invalid_url(self):
        """Test the operation_id property when URL format is invalid."""
        # Mock the polling method and initial response
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/invalid/path/12345?api-version=2025-11-01"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create poller instance
        poller = AnalyzeLROPoller(
            client=Mock(), initial_response=Mock(), deserialization_callback=Mock(), polling_method=mock_polling_method
        )

        # Test operation_id property raises ValueError when URL format is invalid
        with pytest.raises(ValueError, match="Could not extract operation ID"):
            _ = poller.operation_id

    def test_from_continuation_token(self):
        """Test the from_continuation_token class method."""
        # Mock the polling method
        mock_polling_method = Mock()
        mock_polling_method.from_continuation_token.return_value = (
            Mock(),  # client
            Mock(),  # initial_response
            Mock(),  # deserialization_callback
        )

        # Test the class method
        poller = AnalyzeLROPoller.from_continuation_token(
            polling_method=mock_polling_method, continuation_token="test-token"
        )

        assert isinstance(poller, AnalyzeLROPoller)
        mock_polling_method.from_continuation_token.assert_called_once_with("test-token")


class TestPollerIntegration:
    """Test integration with the operations classes."""

    def test_analyze_operation_returns_custom_poller(self):
        """Test that begin_analyze returns AnalyzeLROPoller with operation_id property."""
        # Create a mock client
        mock_client = Mock(spec=ContentUnderstandingClient)

        # Create a mock poller with the required structure
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint.com/analyzerResults/test-op-id-123?api-version=2025-11-01"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create actual AnalyzeLROPoller instance
        result = AnalyzeLROPoller(mock_client, mock_initial_response, Mock(), mock_polling_method)

        # Verify it has the operation_id property
        assert isinstance(result, AnalyzeLROPoller)
        assert hasattr(result, "operation_id")
        operation_id = result.operation_id
        assert operation_id == "test-op-id-123"


class TestAnalyzeLROPollerUsage:
    """Test the usage property on AnalyzeLROPoller (GitHub issue #46249)."""

    def _make_poller_with_usage(self, usage_json):
        """Helper to create an AnalyzeLROPoller with a mocked final response containing usage data."""
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/contentunderstanding/analyzerResults/test-op-id?api-version=2025-11-01"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Mock the final pipeline response (used by .usage property)
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

        return AnalyzeLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method,
        )

    def test_usage_with_full_data(self):
        """Test usage property returns UsageDetails with all fields populated."""
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

        poller = self._make_poller_with_usage(usage_json)
        usage = poller.usage

        assert usage is not None
        assert isinstance(usage, UsageDetails)
        assert usage.document_pages_standard == 2
        assert usage.document_pages_minimal == 0
        assert usage.document_pages_basic == 0
        assert usage.contextualization_tokens == 1500
        assert usage.tokens == {
            "gpt-4.1-input": 500,
            "gpt-4.1-output": 200,
            "text-embedding-3-large-input": 300,
        }

    def test_usage_with_partial_data(self):
        """Test usage property with only some fields populated."""
        usage_json = {
            "documentPagesStandard": 1,
            "contextualizationTokens": 100,
        }

        poller = self._make_poller_with_usage(usage_json)
        usage = poller.usage

        assert usage is not None
        assert usage.document_pages_standard == 1
        assert usage.contextualization_tokens == 100
        assert usage.document_pages_minimal is None
        assert usage.tokens is None

    def test_usage_returns_none_when_not_present(self):
        """Test usage property returns None when usage is not in the response."""
        poller = self._make_poller_with_usage(None)
        usage = poller.usage

        assert usage is None

    def test_usage_returns_none_before_completion(self):
        """Test usage property returns None when the polling has not yet completed."""
        mock_polling_method = Mock()

        poller = AnalyzeLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method,
        )

        # Simulate an in-progress operation: LROPoller.done() returns True when
        # _thread is None, so set _thread to a mock with is_alive() returning True.
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True
        poller._thread = mock_thread

        assert not poller.done()
        usage = poller.usage
        assert usage is None
