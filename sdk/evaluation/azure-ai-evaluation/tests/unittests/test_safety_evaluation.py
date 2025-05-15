import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialScenarioJailbreak, AdversarialSimulator
from azure.ai.evaluation._model_configurations import EvaluationResult
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
def mock_async_target():
    async def mock_async_target_fn(query: str) -> str:
        return "mock async response"

    return mock_async_target_fn


@pytest.fixture
def mock_async_target_with_context():
    async def mock_async_target_with_context_fn(query: str) -> tuple:
        return ("mock async response", "mock async context")

    return mock_async_target_with_context_fn


@pytest.fixture
def mock_eval_result_dict():
    jailbreak = {
        "rows": [
            {
                "outputs.content_safety.hate_unfairness_score": 0.0,
                "outputs.content_safety.self_harm_score": 0.0,
                "outputs.content_safety.sexual_score": 0.0,
                "outputs.content_safety.violence_score": 0.0,
            }
        ],
        "metrics": {},
        "studio_url": "some url",
    }
    regular = {
        "rows": [
            {
                "outputs.content_safety.hate_unfairness_score": 0.0,
                "outputs.content_safety.self_harm_score": 0.0,
                "outputs.content_safety.sexual_score": 0.0,
                "outputs.content_safety.violence_score": 0.0,
            }
        ],
        "metrics": {},
        "studio_url": "some url",
    }
    return {
        "Mock_Jailbreak": jailbreak, 
        "Mock_Regular": regular
    }


@pytest.fixture
def safety_eval(mock_model_config_dict_valid, mock_credential):
    return _SafetyEvaluation(
        azure_ai_project={"subscription_id": "mock-sub", "resource_group_name": "mock-rg", "project_name": "mock-proj"},
        credential=mock_credential,
        model_config=mock_model_config_dict_valid,
    )


@pytest.fixture
def safety_eval_no_model_config(mock_credential):
    return _SafetyEvaluation(
        azure_ai_project={"subscription_id": "mock-sub", "resource_group_name": "mock-rg", "project_name": "mock-proj"},
        credential=mock_credential,
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

    def test_check_target_returns_context_async(self, safety_eval, mock_async_target, mock_async_target_with_context):
        # Test that async function without context returns False
        assert not safety_eval._check_target_returns_context(mock_async_target)
        # Test that async function with context returns True
        assert safety_eval._check_target_returns_context(mock_async_target_with_context)

    def test_check_target_returns_str_async(self, safety_eval, mock_async_target):
        # Test that async function returning string returns True
        assert safety_eval._check_target_returns_str(mock_async_target)

    def test_validate_inputs_groundedness_no_source(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                evaluators=[_SafetyEvaluator.GROUNDEDNESS],
                target=mock_target,
                source_text=None,
            )
        assert "GroundednessEvaluator requires" in str(exc_info.value)

    def test_validate_inputs_multi_turn_scenario(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                target=mock_target,
                evaluators=[_SafetyEvaluator.CONTENT_SAFETY],
                scenario=AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
                num_turns=3,
            )
        assert "not supported for content safety evaluation with more than 1 turn" in str(exc_info.value)

    def test_validate_inputs_no_model_config(self, safety_eval_no_model_config, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval_no_model_config._validate_inputs(
                target=mock_target,
                evaluators=[_SafetyEvaluator.COHERENCE],
            )
        assert "Model configuration is required" in str(exc_info.value)

    def test_validate_inputs_scenario_not_content_safety(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                target=mock_target,
                evaluators=[_SafetyEvaluator.PROTECTED_MATERIAL],
                scenario=AdversarialScenario.ADVERSARIAL_SUMMARIZATION,
            )
        assert "not supported without content safety evaluation" in str(exc_info.value)

    def test_calculate_defect_rate(self, safety_eval, mock_eval_result_dict):
        eval_result = safety_eval._calculate_defect_rate(mock_eval_result_dict)
        assert eval_result is not None
        assert isinstance(eval_result["metrics"]["content_safety.violence_defect_rate"], float)
        assert eval_result["metrics"]["content_safety.violence_defect_rate"] == 0.0

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._simulator.Simulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_simulate_no_scenario(self, mock_open, mock__call__, safety_eval, mock_target):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock__call__.return_value = [JsonLineChatProtocol({"messages": []})]
        
        results = await safety_eval._simulate(target=mock_target)
        assert isinstance(results, dict)
        # Test that it returns simulator data paths
        assert isinstance(next(iter(results.values())), str)
        assert "_Data.jsonl" in next(iter(results.values()))

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_simulate_direct_attack(self, mock_open, mock_call, mock_init, safety_eval, mock_target):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_call.return_value = {
            "jailbreak": JsonLineList([{"messages": []}]),
            "regular": JsonLineList([{"messages": []}]),
        }

        results = await safety_eval._simulate(
            target=mock_target, direct_attack=True, adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA
        )
        assert isinstance(results, dict)
        # Test that the function returns paths with expected file naming patterns
        for path in results.values():
            assert isinstance(path, str)
            assert "_Data.jsonl" in path

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.IndirectAttackSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.IndirectAttackSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_simulate_indirect_jailbreak(self, mock_open, mock_call, mock_init, safety_eval, mock_target):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_call.return_value = JsonLineList([{"messages": []}])

        results = await safety_eval._simulate(
            target=mock_target, adversarial_scenario=AdversarialScenarioJailbreak.ADVERSARIAL_INDIRECT_JAILBREAK
        )
        assert isinstance(results, dict)
        # Test that the function returns a path to a data file
        assert isinstance(next(iter(results.values())), str)
        assert "_Data.jsonl" in next(iter(results.values()))

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_simulate_adversarial(self, mock_open, mock_call, mock_init, safety_eval, mock_target):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_call.return_value = JsonLineList([{"messages": []}])
        
        results = await safety_eval._simulate(
            target=mock_target, adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA
        )
        assert isinstance(results, dict)
        # Test that the function returns a path to a data file
        assert isinstance(next(iter(results.values())), str)
        assert "_Data.jsonl" in next(iter(results.values()))

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    async def test_simulate_no_results(self, mock_call, mock_init, safety_eval, mock_target):
        mock_call.return_value = None
        with pytest.raises(EvaluationException) as exc_info:
            results = await safety_eval._simulate(
                target=mock_target, adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA
            )
        assert "outputs generated by the simulator" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_simulate_passes_randomization_seed(self, mock_open, mock_call, mock_init, safety_eval, mock_target):
        """Tests if randomization_seed is passed correctly to the simulator."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_call.return_value = JsonLineList([{"messages": []}])
        seed_value = 42

        await safety_eval._simulate(
            target=mock_target, 
            adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA,
            randomization_seed=seed_value
        )
        
        # Check if the simulator was called with the correct randomization_seed
        mock_call.assert_called_once()
        call_args, call_kwargs = mock_call.call_args
        assert call_kwargs.get("randomization_seed") == seed_value

    def test_is_async_function(self, safety_eval, mock_target, mock_async_target):
        # Test that sync function returns False
        assert not safety_eval._is_async_function(mock_target)
        # Test that async function returns True
        assert safety_eval._is_async_function(mock_async_target)

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._safety_evaluation._safety_evaluation._SafetyEvaluation._simulate")
    @patch("azure.ai.evaluation._evaluate._evaluate.evaluate")
    async def test_call_with_async_target(self, mock_evaluate, mock_simulate, safety_eval, mock_async_target):
        # Setup mocks
        mock_simulate.return_value = {"MockSimulator": "MockSimulator_Data.jsonl"}
        mock_evaluate.return_value = {
            "metrics": {},
            "rows": [],
            "studio_url": "test_url"
        }
        
        # Call the __call__ method with an async target
        result = await safety_eval(target=mock_async_target)
        
        # Verify the results
        assert isinstance(result, dict)
        assert "MockSimulator" in result
        
        # Verify that _simulate was called with the async target
        mock_simulate.assert_called_once()
        assert mock_simulate.call_args[1]["target"] == mock_async_target

    def test_get_scenario_code_vulnerability(self, safety_eval):
        scenario = safety_eval._get_scenario([_SafetyEvaluator.CODE_VULNERABILITY])
        assert scenario == AdversarialScenario.ADVERSARIAL_CODE_VULNERABILITY

    def test_get_scenario_ungrounded_attributes(self, safety_eval):
        scenario = safety_eval._get_scenario([_SafetyEvaluator.UNGROUNDED_ATTRIBUTES])
        assert scenario == AdversarialScenario.ADVERSARIAL_UNGROUNDED_ATTRIBUTES

    def test_get_evaluators_code_vulnerability(self, safety_eval):
        evaluators = safety_eval._get_evaluators([_SafetyEvaluator.CODE_VULNERABILITY])
        assert "code_vulnerability" in evaluators
        assert evaluators["code_vulnerability"].__class__.__name__ == "CodeVulnerabilityEvaluator"

    def test_get_evaluators_ungrounded_attributes(self, safety_eval):
        evaluators = safety_eval._get_evaluators([_SafetyEvaluator.UNGROUNDED_ATTRIBUTES])
        assert "ungrounded_attributes" in evaluators
        assert evaluators["ungrounded_attributes"].__class__.__name__ == "UngroundedAttributesEvaluator"

    def test_validate_inputs_code_vulnerability_multi_turn(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                target=mock_target,
                evaluators=[_SafetyEvaluator.CODE_VULNERABILITY],
                num_turns=3,
            )
        assert "Code vulnerability evaluation only supports single-turn conversations" in str(exc_info.value)

    def test_validate_inputs_ungrounded_attributes_multi_turn(self, safety_eval, mock_target):
        with pytest.raises(EvaluationException) as exc_info:
            safety_eval._validate_inputs(
                target=mock_target,
                evaluators=[_SafetyEvaluator.UNGROUNDED_ATTRIBUTES],
                num_turns=3,
            )
        assert "Ungrounded attributes evaluation only supports single-turn conversations" in str(exc_info.value)
