import pytest
from azure.ai.evaluation._common.rai_service import get_common_headers


def test_get_common_headers_default():
    """Test get_common_headers with default parameters."""
    token = "test_token"
    headers = get_common_headers(token)
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert "User-Agent" in headers
    assert "azure-ai-evaluation" in headers["User-Agent"]


def test_get_common_headers_with_evaluator_name():
    """Test get_common_headers with evaluator name."""
    token = "test_token"
    evaluator_name = "TestEvaluator"
    headers = get_common_headers(token, evaluator_name)
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert "User-Agent" in headers
    assert "azure-ai-evaluation" in headers["User-Agent"]
    assert f"(type=evaluator; subtype={evaluator_name})" in headers["User-Agent"]


def test_get_common_headers_with_custom_user_agent():
    """Test get_common_headers with custom user agent."""
    token = "test_token"
    custom_user_agent = "MyApp/1.0.0"
    headers = get_common_headers(token, user_agent=custom_user_agent)
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert "User-Agent" in headers
    assert "azure-ai-evaluation" in headers["User-Agent"]
    assert custom_user_agent in headers["User-Agent"]
    # Verify format: "azure-ai-evaluation/<version> MyApp/1.0.0"
    assert headers["User-Agent"].endswith(f" {custom_user_agent}")


def test_get_common_headers_with_evaluator_name_and_custom_user_agent():
    """Test get_common_headers with both evaluator name and custom user agent."""
    token = "test_token"
    evaluator_name = "TestEvaluator"
    custom_user_agent = "MyApp/1.0.0"
    headers = get_common_headers(token, evaluator_name, custom_user_agent)
    
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token"
    assert "User-Agent" in headers
    assert "azure-ai-evaluation" in headers["User-Agent"]
    assert f"(type=evaluator; subtype={evaluator_name})" in headers["User-Agent"]
    assert custom_user_agent in headers["User-Agent"]
    # Verify format: "azure-ai-evaluation/<version> (type=evaluator; subtype=TestEvaluator) MyApp/1.0.0"
    assert headers["User-Agent"].endswith(f" {custom_user_agent}")