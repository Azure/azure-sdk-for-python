\
import pytest
import unittest.mock as mock
from unittest.mock import MagicMock
import json
from azure.core.credentials import TokenCredential

try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:
    from azure.ai.evaluation.red_team._utils._rai_service_eval_chat_target import RAIServiceEvalChatTarget
    from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory
    from pyrit.models import PromptRequestResponse, PromptRequestPiece
    from pyrit.common import initialize_pyrit, IN_MEMORY

    initialize_pyrit(memory_db_type=IN_MEMORY)

# Create mock objects for testing
@pytest.fixture
def mock_azure_ai_project():
    return {
        "subscription_id": "test-subscription",
        "resource_group_name": "test-resource-group",
        "project_name": "test-project",
    }
MockCredential = MagicMock(spec=TokenCredential)
MockLogger = MagicMock()


@pytest.fixture
def mock_credential():
    return MagicMock(spec=TokenCredential)

@pytest.fixture
def mock_prompt_request():
    piece = PromptRequestPiece(
        role="user",
        original_value="Test prompt",
        converted_value="Test prompt",
        conversation_id="test_conv_id",
        sequence=1,
        original_value_data_type="text",
        converted_value_data_type="text",
    )
    return PromptRequestResponse(request_pieces=[piece])

@pytest.mark.asyncio
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_eval_chat_target.evaluate_with_rai_service')
async def test_send_prompt_async_success(mock_evaluate, mock_prompt_request, mock_azure_ai_project):
    """Tests successful evaluation and response formatting."""    
    target = RAIServiceEvalChatTarget(
        credential=MockCredential,
        azure_ai_project=mock_azure_ai_project,
        risk_category=RiskCategory.HateUnfairness,
        logger=MockLogger
    )

    # Mock the evaluation result from RAI service
    mock_evaluate.return_value = {
        "hate_fairness_score": 5,
        "hate_fairness_reason": "Detected hateful content.",
        "hate_fairness_threshold": 3,
        "hate_fairness": "High Severity"
    }

    response = await target.send_prompt_async(prompt_request=mock_prompt_request)
    
    mock_evaluate.assert_called_once_with(
        {"query": "", "response": "Test prompt"},
        metric_name="hate_fairness",
        project_scope=mock_azure_ai_project,
        credential=MockCredential
    )

    assert len(response.request_pieces) == 1
    response_piece = response.request_pieces[0]
    assert response_piece.role == "assistant"

    expected_response_data = {"score_value": True, "description": "Threshold: 3, Result: High Severity", "rationale": "Detected hateful content.", "metadata": {"raw_score": 5, "threshold": 3, "result": "High Severity", "risk_category": "hate_unfairness"}}
    assert json.loads(response_piece.converted_value) == expected_response_data
    MockLogger.info.assert_called() # Check if logger was called

@pytest.mark.asyncio
@mock.patch('azure.ai.evaluation.red_team._utils._rai_service_eval_chat_target.evaluate_with_rai_service')
async def test_send_prompt_async_fail_score(mock_evaluate, mock_prompt_request, mock_azure_ai_project):
    """Tests evaluation resulting in a 'false' score."""    
    target = RAIServiceEvalChatTarget(
        credential=mock_credential,
        azure_ai_project=mock_azure_ai_project,
        risk_category=RiskCategory.Violence,
        logger=MockLogger
    )

    mock_evaluate.return_value = {
        "violence_score": 2,
        "violence_reason": "No violent content detected.",
        "violence_threshold": 4,
        "violence": "Very Low Severity"
    }

    response = await target.send_prompt_async(prompt_request=mock_prompt_request)

    assert len(response.request_pieces) == 1
    response_piece = response.request_pieces[0]
    response_data = json.loads(response_piece.converted_value)
    assert response_data["score_value"] == False # 2 <= 4
    assert response_data["metadata"]["raw_score"] == 2

def test_validate_request_success(mock_prompt_request, mock_azure_ai_project):
    """Tests successful validation."""
    target = RAIServiceEvalChatTarget(MockCredential, mock_azure_ai_project, RiskCategory.HateUnfairness, MockLogger)
    try:
        target._validate_request(prompt_request=mock_prompt_request)
    except ValueError:
        pytest.fail("_validate_request raised ValueError unexpectedly")

def test_validate_request_invalid_pieces(mock_prompt_request, mock_azure_ai_project):
    """Tests validation failure with multiple pieces."""
    target = RAIServiceEvalChatTarget(MockCredential, mock_azure_ai_project, RiskCategory.HateUnfairness, MockLogger)
    mock_prompt_request.request_pieces.append(mock_prompt_request.request_pieces[0]) # Add a second piece
    with pytest.raises(ValueError, match="only supports a single prompt request piece"):
        target._validate_request(prompt_request=mock_prompt_request)

def test_validate_request_invalid_type(mock_prompt_request, mock_azure_ai_project):
    """Tests validation failure with non-text data type."""
    target = RAIServiceEvalChatTarget(MockCredential, mock_azure_ai_project, RiskCategory.HateUnfairness, MockLogger)
    mock_prompt_request.request_pieces[0].converted_value_data_type = "image"
    with pytest.raises(ValueError, match="only supports text prompt input"):
        target._validate_request(prompt_request=mock_prompt_request)

def test_is_json_response_supported(mock_azure_ai_project):
    """Tests if JSON response is supported."""
    target = RAIServiceEvalChatTarget(MockCredential, mock_azure_ai_project, RiskCategory.HateUnfairness, MockLogger)
    assert target.is_json_response_supported() is True

# TODO: Add tests for error handling in evaluate_with_rai_service if needed
