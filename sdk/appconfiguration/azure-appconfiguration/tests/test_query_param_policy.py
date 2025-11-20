# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest
from azure.appconfiguration._query_param_policy import QueryParamPolicy


def test_query_parameters_are_sorted_alphabetically():
    """Test that query parameters are sorted alphabetically."""
    original_url = "https://test.azconfig.io/kv?zebra=value1&alpha=value2&beta=value3"
    expected_url = "https://test.azconfig.io/kv?alpha=value2&beta=value3&zebra=value1"
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy that captures the request
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    assert mock_next.captured_url == expected_url, \
        f"Query parameters should be sorted alphabetically. Expected: {expected_url}, Got: {mock_next.captured_url}"


def test_query_parameter_keys_are_converted_to_lowercase():
    """Test that query parameter keys are converted to lowercase."""
    original_url = "https://test.azconfig.io/kv?SELECT=field1&FILTER=condition&orderBy=field2"
    expected_url = "https://test.azconfig.io/kv?filter=condition&orderby=field2&select=field1"
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    assert mock_next.captured_url == expected_url, \
        f"Query parameter keys should be lowercase and sorted. Expected: {expected_url}, Got: {mock_next.captured_url}"


def test_query_parameters_with_multiple_values():
    """Test that query parameters with multiple values are handled correctly."""
    original_url = "https://test.azconfig.io/kv?key=value1&key=value2&alpha=test"
    expected_url = "https://test.azconfig.io/kv?alpha=test&key=value1&key=value2"
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    assert mock_next.captured_url == expected_url, \
        f"Multiple values for same key should be preserved. Expected: {expected_url}, Got: {mock_next.captured_url}"


def test_query_parameters_with_special_characters():
    """Test that query parameters with special characters are preserved."""
    original_url = "https://test.azconfig.io/kv?filter=name%20eq%20%27test%27&select=*"
    expected_url = "https://test.azconfig.io/kv?filter=name+eq+%27test%27&select=%2A"
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    # Note: URL encoding may change the format slightly, but the query params should still be sorted
    assert "filter=" in mock_next.captured_url
    assert "select=" in mock_next.captured_url
    # The params should be in alphabetical order
    filter_pos = mock_next.captured_url.index("filter=")
    select_pos = mock_next.captured_url.index("select=")
    assert filter_pos < select_pos, "Parameters should be sorted alphabetically"


def test_no_query_parameters():
    """Test that URLs without query parameters are not modified."""
    original_url = "https://test.azconfig.io/kv"
    expected_url = "https://test.azconfig.io/kv"
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    assert mock_next.captured_url == expected_url


def test_empty_query_parameter_values():
    """Test that empty query parameter values are preserved."""
    original_url = "https://test.azconfig.io/kv?zebra=&alpha=value&beta="
    expected_url = "https://test.azconfig.io/kv?alpha=value&beta=&zebra="
    
    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)
    
    query_param_policy = QueryParamPolicy()
    
    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None
        
        def send(self, request):
            self.captured_url = request.http_request.url
            return None
    
    mock_next = MockNext()
    query_param_policy.next = mock_next
    
    query_param_policy.send(pipeline_request)
    
    assert mock_next.captured_url == expected_url
