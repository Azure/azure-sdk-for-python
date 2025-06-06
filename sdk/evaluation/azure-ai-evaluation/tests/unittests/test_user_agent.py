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


def test_prompty_evaluator_user_agent_context():
    """Test that PromptyEvaluatorBase uses custom user_agent from context."""
    from azure.ai.evaluation._context import set_current_user_agent, get_current_user_agent
    
    # Test the user_agent construction logic from PromptyEvaluatorBase
    try:
        from azure.ai.evaluation._user_agent import USER_AGENT
    except ImportError:
        USER_AGENT = "azure-ai-evaluation/unknown"
    
    # Save original context
    original_user_agent = get_current_user_agent()
    
    try:
        # Test without custom user_agent
        set_current_user_agent(None)
        subclass_name = "TestPromptyEvaluator"
        base_user_agent = f"{USER_AGENT} (type=evaluator; subtype={subclass_name})"
        custom_user_agent = get_current_user_agent()
        user_agent_without = f"{base_user_agent} {custom_user_agent}" if custom_user_agent else base_user_agent
        
        expected_without = f"{USER_AGENT} (type=evaluator; subtype={subclass_name})"
        assert user_agent_without == expected_without
        
        # Test with custom user_agent
        set_current_user_agent("TestApp/1.5.0")
        custom_user_agent = get_current_user_agent()
        user_agent_with = f"{base_user_agent} {custom_user_agent}" if custom_user_agent else base_user_agent
        
        expected_with = f"{USER_AGENT} (type=evaluator; subtype={subclass_name}) TestApp/1.5.0"
        assert user_agent_with == expected_with
        
        # Verify the custom user_agent is appended correctly
        assert user_agent_with.endswith(" TestApp/1.5.0")
        assert "(type=evaluator; subtype=TestPromptyEvaluator)" in user_agent_with
        
    finally:
        # Restore original context
        set_current_user_agent(original_user_agent)