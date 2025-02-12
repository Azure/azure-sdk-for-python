import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialScenarioJailbreak, AdversarialSimulator
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation.simulator._utils import JsonLineChatProtocol, JsonLineList
from azure.core.credentials import TokenCredential

@pytest.fixture
def mock_credential():
    return MagicMock(spec=TokenCredential)

@pytest.fixture
def mock_model_config_dict_valid():
    return {
        "azure_deployment": "test_deployment",
        "azure_endpoint": "https://example.azure.com/",
        "type": "azure_openai",
    }

@pytest.fixture
def mock_model_config_dict_invalid():
    return {
        "type": "azure_openai",
    }

@pytest.fixture
def mock_target():
    def mock_target_fn() -> str:
        return "mock response"
    return mock_target_fn

@pytest.fixture
def mock_target_with_context():
    def mock_target_with_context_fn() -> tuple:
        return ("mock response", "mock context")
    return mock_target_with_context_fn

@pytest.fixture
def safety_eval(mock_model_config_dict_valid, mock_credential):
    return _SafetyEvaluation(
        azure_ai_project={"subscription_id": "mock-sub", "resource_group_name": "mock-rg", "project_name": "mock-proj"},
        credential=mock_credential,
        model_config=mock_model_config_dict_valid,
    )

@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestSafetyEvaluation:
    def test_validate_model_config_missing_keys(self, mock_credential, mock_model_config_dict_invalid):
        with pytest.raises(ValueError) as exc_info:
            _SafetyEvaluation(
                azure_ai_project={"subscription_id": "sub", "resource_group_name": "rg", "project_name": "proj"},
                credential=mock_credential,
                model_config=mock_model_config_dict_invalid,
            )
        assert "missing required keys" in str(exc_info.value)
    
    def test_get_evaluators_invalid(self, safety_eval):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._get_evaluators([None])  # type: ignore
        assert "Invalid evaluator:" in str(exc_info.value)

    def test_get_scenario_invalid(self, safety_eval):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._get_scenario([None])  # type: ignore
        assert "Invalid evaluator:" in str(exc_info.value)

    def test_check_target_returns_context_false(self, safety_eval, mock_target):
        assert not safety_eval._check_target_returns_context(mock_target)

    def test_check_target_returns_context_true(self, safety_eval, mock_target_with_context):
        assert safety_eval._check_target_returns_context(mock_target_with_context)

    def test_validate_inputs_groundedness_no_source(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                evaluators=[_SafetyEvaluator.GROUNDEDNESS],
                target=mock_target,
                source_text=None,
            )
        assert "requires either source_text" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator.__call__", new_callable=AsyncMock)
    async def test_simulate_no_scenario(self, mock__call__, safety_eval, mock_target):
        mock__call__.return_value = [JsonLineChatProtocol({"messages":[]})]
        results = await safety_eval._simulate(target=mock_target)
        assert isinstance(results, dict)
        assert isinstance(results["regular"], str)