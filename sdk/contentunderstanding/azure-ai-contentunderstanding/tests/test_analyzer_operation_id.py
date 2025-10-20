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
from azure.ai.contentunderstanding.operations._patch import (
    AnalyzeLROPoller,
    _parse_operation_id,
)


class TestParseOperationId:
    """Test the operation ID parsing function."""

    def test_parse_analyze_operation_id(self):
        """Test parsing operation ID from analyze operation location."""
        url = "https://endpoint/contentunderstanding/analyzerResults/12345-67890-abcdef?api-version=2025-05-01-preview"
        operation_id = _parse_operation_id(url)
        assert operation_id == "12345-67890-abcdef"

    def test_parse_operation_id_with_different_endpoints(self):
        """Test parsing operation ID from different endpoint formats."""
        urls = [
            "https://ai-foundry-mock.services.ai.azure.com/contentunderstanding/analyzerResults/b0fdb7d6-6fa7-4b43-af09-1b14e84cedce?api-version=2025-05-01-preview",
            "https://my-resource.cognitiveservices.azure.com/contentunderstanding/analyzerResults/abc123?api-version=2025-05-01-preview",
            "https://localhost:8080/contentunderstanding/analyzerResults/test-op-id?api-version=2025-05-01-preview"
        ]
        
        expected_ids = ["b0fdb7d6-6fa7-4b43-af09-1b14e84cedce", "abc123", "test-op-id"]
        
        for url, expected_id in zip(urls, expected_ids):
            operation_id = _parse_operation_id(url)
            assert operation_id == expected_id

    def test_parse_operation_id_no_match(self):
        """Test parsing operation ID when no match is found."""
        url = "https://endpoint/contentunderstanding/something-else/12345?api-version=2025-05-01-preview"
        
        with pytest.raises(ValueError, match="Could not extract operation ID"):
            _parse_operation_id(url)


class TestAnalyzeLROPoller:
    """Test the AnalyzeLROPoller class."""

    def test_details_property_success(self):
        """Test the details property when operation ID can be extracted."""
        # Mock the polling method and initial response
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/contentunderstanding/analyzerResults/test-op-id?api-version=2025-05-01-preview"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create poller instance
        poller = AnalyzeLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method
        )

        # Test details property
        details = poller.details
        assert details["operation_id"] == "test-op-id"
        assert details["operation_type"] == "analyze"

    def test_details_property_missing_header(self):
        """Test the details property when Operation-Location header is missing."""
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
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method
        )

        # Test details property
        details = poller.details
        assert details["operation_id"] is None
        assert details["operation_type"] == "analyze"
        assert "error" in details

    def test_details_property_invalid_url(self):
        """Test the details property when URL format is invalid."""
        # Mock the polling method and initial response
        mock_polling_method = Mock()
        mock_initial_response = Mock()
        mock_http_response = Mock()
        mock_http_response.headers = {
            "Operation-Location": "https://endpoint/invalid/path/12345?api-version=2025-05-01-preview"
        }
        mock_initial_response.http_response = mock_http_response
        mock_polling_method.return_value = mock_polling_method
        mock_polling_method._initial_response = mock_initial_response

        # Create poller instance
        poller = AnalyzeLROPoller(
            client=Mock(),
            initial_response=Mock(),
            deserialization_callback=Mock(),
            polling_method=mock_polling_method
        )

        # Test details property
        details = poller.details
        assert details["operation_id"] is None
        assert details["operation_type"] == "analyze"
        assert "error" in details

    def test_from_continuation_token(self):
        """Test the from_continuation_token class method."""
        # Mock the polling method
        mock_polling_method = Mock()
        mock_polling_method.from_continuation_token.return_value = (
            Mock(),  # client
            Mock(),  # initial_response
            Mock()   # deserialization_callback
        )

        # Test the class method
        poller = AnalyzeLROPoller.from_continuation_token(
            polling_method=mock_polling_method,
            continuation_token="test-token"
        )

        assert isinstance(poller, AnalyzeLROPoller)
        mock_polling_method.from_continuation_token.assert_called_once_with("test-token")


class TestPollerIntegration:
    """Test integration with the operations classes."""

    def test_analyze_operation_returns_custom_poller(self):
        """Test that begin_analyze returns AnalyzeLROPoller."""
        from azure.ai.contentunderstanding.operations._patch import ContentAnalyzersOperations
        
        # Mock the operations class with proper parameters
        operations = ContentAnalyzersOperations(client=Mock(), config=Mock(), serializer=Mock(), deserializer=Mock())
        
        # Mock the super().begin_analyze call
        with patch.object(ContentAnalyzersOperations.__bases__[0], 'begin_analyze') as mock_begin_analyze:
            mock_poller = Mock(spec=LROPoller)
            mock_poller._polling_method = Mock()
            mock_poller._polling_method._initial_response = Mock()
            mock_poller._polling_method._deserialization_callback = Mock()
            mock_begin_analyze.return_value = mock_poller
            
            # Call begin_analyze
            result = operations.begin_analyze("test-analyzer", url="https://example.com/doc.pdf")
            
            # Verify it returns the custom poller
            assert isinstance(result, AnalyzeLROPoller)

    def test_classify_operation_returns_generic_poller(self):
        """Test that begin_classify returns generic LROPoller (no custom functionality)."""
        from azure.ai.contentunderstanding.operations._patch import ContentClassifiersOperations
        
        # Mock the operations class with proper parameters
        operations = ContentClassifiersOperations(client=Mock(), config=Mock(), serializer=Mock(), deserializer=Mock())
        
        # Mock the super().begin_classify call
        with patch.object(ContentClassifiersOperations.__bases__[0], 'begin_classify') as mock_begin_classify:
            mock_poller = Mock(spec=LROPoller)
            mock_begin_classify.return_value = mock_poller
            
            # Call begin_classify
            result = operations.begin_classify("test-classifier", url="https://example.com/doc.pdf")
            
            # Verify it returns the generic poller (not custom)
            assert isinstance(result, LROPoller)
            assert not isinstance(result, AnalyzeLROPoller)
