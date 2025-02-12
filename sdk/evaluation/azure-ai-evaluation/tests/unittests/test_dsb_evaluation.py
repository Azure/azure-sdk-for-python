import pytest
from unittest.mock import MagicMock
from azure.ai.evaluation._dsb_evaluation._dsb_evaluation import _DSBEvaluation, _DSBEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialScenarioJailbreak
from azure.ai.evaluation._exceptions import EvaluationException
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
def dsb_eval(mock_model_config_dict_valid, mock_credential):
    return _DSBEvaluation(
        azure_ai_project={"subscription_id": "mock-sub", "resource_group_name": "mock-rg", "project_name": "mock-proj"},
        credential=mock_credential,
        model_config=mock_model_config_dict_valid,
    )

@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestDSBEvaluation:
    def test_validate_model_config_missing_keys(self, mock_credential, mock_model_config_dict_invalid):
        with pytest.raises(ValueError) as exc_info:
            _DSBEvaluation(
                azure_ai_project={"subscription_id": "sub", "resource_group_name": "rg", "project_name": "proj"},
                credential=mock_credential,
                model_config=mock_model_config_dict_invalid,
            )
        assert "missing required keys" in str(exc_info.value)
    
    def test_get_evaluators_invalid(self, dsb_eval):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._get_evaluators([None])  # type: ignore
        assert "Invalid evaluator:" in str(exc_info.value)

    def test_check_target_returns_context_false(self, dsb_eval, mock_target):
        assert not dsb_eval._check_target_returns_context(mock_target)

    def test_check_target_returns_context_true(self, dsb_eval, mock_target_with_context):
        assert dsb_eval._check_target_returns_context(mock_target_with_context)

    def test_validate_inputs_groundedness_no_source(self, dsb_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.GROUNDEDNESS],
                target=mock_target,
                adversarial_scenario=None,
                source_text=None,
            )
        assert "requires either source_text" in str(exc_info.value)

    def test_validate_inputs_indirect_attack_scenario_invalid(self, dsb_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.INDIRECT_ATTACK],
                target=mock_target,
                adversarial_scenario=[AdversarialScenario.ADVERSARIAL_QA],
            )
        assert "requires adversarial_scenario to be set to ADVERSARIAL_INDIRECT_JAILBREAK" in str(exc_info.value)

    def test_validate_inputs_indirect_attack_evaluator_invalid(self, dsb_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.DIRECT_ATTACK],
                target=mock_target,
                adversarial_scenario=AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK,
            )
        assert "IndirectAttackEvaluator should be used" in str(exc_info.value)

    def test_validate_inputs_protected_material_scenario_invalid(self, dsb_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.PROTECTED_MATERIAL],
                target=mock_target,
                adversarial_scenario=[AdversarialScenario.ADVERSARIAL_QA],
            )
        assert "requires adversarial_scenario to be set to ADVERSARIAL_CONTENT_PROTECTED_MATERIAL" in str(exc_info.value)
    
    def test_validate_inputs_protected_material_evaluator_invalid(self, dsb_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.DIRECT_ATTACK],
                target=mock_target,
                adversarial_scenario=AdversarialScenario.ADVERSARIAL_CONTENT_PROTECTED_MATERIAL,
            )
        assert "ProtectedMaterialEvaluator should be used" in str(exc_info.value)

    def test_direct_attack_standalone_raises(self, dsb_eval):
        with pytest.raises(EvaluationException) as exc_info:
            dsb_eval._validate_inputs(
                evaluators=[_DSBEvaluator.DIRECT_ATTACK],
                target=lambda x: {"response": "test"},
            )
        assert "DirectAttack should be used along with other evaluators" in str(exc_info.value)