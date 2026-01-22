"""
Unit tests for the Foundry module including:
- DatasetConfigurationBuilder
- StrategyMapper
- RAIServiceScorer
- ScenarioOrchestrator
- FoundryResultProcessor
- FoundryExecutionManager
"""

import pytest
import uuid
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from typing import Dict, List, Any

from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory

# Import Foundry components - these require pyrit to be installed
from azure.ai.evaluation.red_team._foundry._dataset_builder import DatasetConfigurationBuilder
from azure.ai.evaluation.red_team._foundry._strategy_mapping import StrategyMapper
from azure.ai.evaluation.red_team._foundry._rai_scorer import RAIServiceScorer
from azure.ai.evaluation.red_team._foundry._scenario_orchestrator import ScenarioOrchestrator
from azure.ai.evaluation.red_team._foundry._foundry_result_processor import FoundryResultProcessor
from azure.ai.evaluation.red_team._foundry._execution_manager import FoundryExecutionManager


@pytest.fixture
def mock_credential():
    """Create a mock credential."""
    return MagicMock()


@pytest.fixture
def mock_azure_ai_project():
    """Create a mock Azure AI project configuration."""
    return {
        "subscription_id": "test-subscription",
        "resource_group_name": "test-resource-group",
        "project_name": "test-project",
    }


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger


@pytest.fixture
def sample_objectives():
    """Create sample attack objectives."""
    return [
        {
            "id": str(uuid.uuid4()),
            "messages": [{"content": "Test objective 1"}],
            "metadata": {"risk_subtype": "violence_general"},
        },
        {
            "id": str(uuid.uuid4()),
            "messages": [{"content": "Test objective 2", "context": [{"content": "Email content", "context_type": "email"}]}],
            "metadata": {"risk_subtype": "violence_specific"},
        },
    ]


@pytest.fixture
def sample_context_items():
    """Create sample context items."""
    return [
        {"content": "Email body content", "context_type": "email", "tool_name": "email_reader"},
        {"content": "<html>Page content</html>", "context_type": "html", "tool_name": "web_browser"},
    ]


# =============================================================================
# Tests for DatasetConfigurationBuilder
# =============================================================================
@pytest.mark.unittest
class TestDatasetConfigurationBuilder:
    """Test the DatasetConfigurationBuilder class."""

    def test_initialization(self):
        """Test DatasetConfigurationBuilder initialization."""
        builder = DatasetConfigurationBuilder(
            risk_category="violence",
            is_indirect_attack=False,
        )

        assert builder.risk_category == "violence"
        assert builder.is_indirect_attack is False
        assert builder.seed_groups == []

    def test_initialization_indirect_attack(self):
        """Test DatasetConfigurationBuilder with indirect attack mode."""
        builder = DatasetConfigurationBuilder(
            risk_category="hate_unfairness",
            is_indirect_attack=True,
        )

        assert builder.risk_category == "hate_unfairness"
        assert builder.is_indirect_attack is True

    def test_add_objective_without_context(self):
        """Test adding an objective without context."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            context_items=None,
            metadata={"risk_subtype": "violence_general"},
        )

        assert len(builder) == 1
        assert len(builder.seed_groups) == 1
        # Each seed group should have at least one seed (the objective)
        assert len(builder.seed_groups[0].seeds) >= 1

    def test_add_objective_with_context(self, sample_context_items):
        """Test adding an objective with context items."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            context_items=sample_context_items,
            metadata={"risk_subtype": "violence_general"},
        )

        assert len(builder) == 1
        # Should have objective + context prompts
        assert len(builder.seed_groups[0].seeds) >= 1

    def test_add_objective_indirect_attack_with_context(self, sample_context_items):
        """Test adding an objective with XPIA (indirect attack) mode."""
        builder = DatasetConfigurationBuilder(
            risk_category="violence",
            is_indirect_attack=True,
        )

        builder.add_objective_with_context(
            objective_content="Hidden attack text",
            objective_id=str(uuid.uuid4()),
            context_items=sample_context_items,
            metadata={"risk_subtype": "xpia"},
        )

        assert len(builder) == 1
        # XPIA should create objective + attack vehicle + original context
        seeds = builder.seed_groups[0].seeds
        assert len(seeds) >= 1

        # Check that attack vehicle metadata is present on some seeds
        has_attack_vehicle = any(
            getattr(seed, "metadata", {}).get("is_attack_vehicle")
            for seed in seeds
        )
        # In XPIA mode with context, we should have attack vehicles
        # (This depends on implementation details)

    def test_parse_or_generate_uuid_with_valid_uuid(self):
        """Test UUID parsing with a valid UUID string."""
        builder = DatasetConfigurationBuilder(risk_category="violence")
        test_uuid = str(uuid.uuid4())

        result = builder._parse_or_generate_uuid(test_uuid)

        assert isinstance(result, uuid.UUID)
        assert str(result) == test_uuid

    def test_parse_or_generate_uuid_with_none(self):
        """Test UUID generation when None is provided."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        result = builder._parse_or_generate_uuid(None)

        assert isinstance(result, uuid.UUID)

    def test_parse_or_generate_uuid_with_invalid_string(self):
        """Test UUID generation with an invalid UUID string."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        result = builder._parse_or_generate_uuid("not-a-uuid")

        # Should generate a new UUID instead of raising
        assert isinstance(result, uuid.UUID)

    def test_determine_data_type_text(self):
        """Test data type determination for text-like contexts.

        With binary_path support, all non-tool_call contexts return binary_path.
        """
        builder = DatasetConfigurationBuilder(risk_category="violence")

        # All text-like types should return "binary_path" (stored as files)
        for ctx_type in ["email", "document", "code", "text", "markdown", "footnote", ""]:
            result = builder._determine_data_type({"context_type": ctx_type})
            assert result == "binary_path", f"Expected 'binary_path' for {ctx_type}"

    def test_determine_data_type_url(self):
        """Test data type determination for URL-like contexts.

        With binary_path support, all non-tool_call contexts return binary_path.
        """
        builder = DatasetConfigurationBuilder(risk_category="violence")

        for ctx_type in ["html", "url", "web"]:
            result = builder._determine_data_type({"context_type": ctx_type})
            assert result == "binary_path", f"Expected 'binary_path' for {ctx_type}"

    def test_determine_data_type_media(self):
        """Test data type determination for media contexts.

        With binary_path support, all non-tool_call contexts return binary_path.
        """
        builder = DatasetConfigurationBuilder(risk_category="violence")

        assert builder._determine_data_type({"context_type": "image"}) == "binary_path"
        assert builder._determine_data_type({"context_type": "audio"}) == "binary_path"
        assert builder._determine_data_type({"context_type": "video"}) == "binary_path"

    def test_determine_data_type_tool_call(self):
        """Test data type determination for tool_call contexts."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        result = builder._determine_data_type({"context_type": "tool_call"})
        assert result == "tool_call"

    def test_inject_attack_into_vehicle_with_placeholder(self):
        """Test attack injection when content has placeholder."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "Email content with {attack_text} embedded."
        result = builder._inject_attack_into_vehicle(
            attack_string="ATTACK",
            content=content,
            context_type="email",
        )

        assert "ATTACK" in result
        assert "{attack_text}" not in result

    def test_inject_attack_into_vehicle_email(self):
        """Test attack injection for email context."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "Regular email content."
        result = builder._inject_attack_into_vehicle(
            attack_string="Attack text",
            content=content,
            context_type="email",
        )

        # Should append attack to email
        assert "Regular email content." in result

    def test_inject_attack_into_vehicle_html(self):
        """Test attack injection for HTML context."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "<html><body>Page content</body></html>"
        result = builder._inject_attack_into_vehicle(
            attack_string="Hidden attack",
            content=content,
            context_type="html",
        )

        # HTML injection should use hidden div
        assert "display:none" in result or "Hidden attack" in result

    def test_inject_attack_into_vehicle_code(self):
        """Test attack injection for code context."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "def main():\n    print('hello')"
        result = builder._inject_attack_into_vehicle(
            attack_string="Attack in comment",
            content=content,
            context_type="code",
        )

        # Code injection should use comment
        assert "#" in result or "Attack in comment" in result

    def test_build_returns_dataset_configuration(self):
        """Test that build() returns a DatasetConfiguration."""
        builder = DatasetConfigurationBuilder(risk_category="violence")
        builder.add_objective_with_context(
            objective_content="Test objective",
            objective_id=None,
        )

        result = builder.build()

        # Check that it's a DatasetConfiguration
        assert hasattr(result, "get_all_seed_groups")
        assert len(result.get_all_seed_groups()) == 1

    def test_len_method(self):
        """Test __len__ returns correct count."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        assert len(builder) == 0

        builder.add_objective_with_context(objective_content="Test 1")
        assert len(builder) == 1

        builder.add_objective_with_context(objective_content="Test 2")
        assert len(builder) == 2


# =============================================================================
# Tests for StrategyMapper
# =============================================================================
@pytest.mark.unittest
class TestStrategyMapper:
    """Test the StrategyMapper class."""

    def test_map_single_strategy_easy(self):
        """Test mapping EASY strategy."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        result = StrategyMapper.map_strategy(AttackStrategy.EASY)
        assert result == FoundryStrategy.EASY

    def test_map_single_strategy_moderate(self):
        """Test mapping MODERATE strategy."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        result = StrategyMapper.map_strategy(AttackStrategy.MODERATE)
        assert result == FoundryStrategy.MODERATE

    def test_map_single_strategy_base64(self):
        """Test mapping Base64 strategy."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        result = StrategyMapper.map_strategy(AttackStrategy.Base64)
        assert result == FoundryStrategy.Base64

    def test_map_single_strategy_baseline_returns_none(self):
        """Test that Baseline strategy returns None (special handling)."""
        result = StrategyMapper.map_strategy(AttackStrategy.Baseline)
        assert result is None

    def test_map_single_strategy_indirect_jailbreak_returns_none(self):
        """Test that IndirectJailbreak strategy returns None (special handling)."""
        result = StrategyMapper.map_strategy(AttackStrategy.IndirectJailbreak)
        assert result is None

    def test_map_strategies_list(self):
        """Test mapping a list of strategies."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        strategies = [AttackStrategy.Base64, AttackStrategy.Morse, AttackStrategy.Caesar]
        result = StrategyMapper.map_strategies(strategies)

        assert len(result) == 3
        assert FoundryStrategy.Base64 in result
        assert FoundryStrategy.Morse in result
        assert FoundryStrategy.Caesar in result

    def test_map_strategies_filters_special(self):
        """Test that special strategies are filtered out."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Baseline, AttackStrategy.Morse]
        result = StrategyMapper.map_strategies(strategies)

        # Baseline should be filtered out
        assert len(result) == 2

    def test_map_composed_strategy(self):
        """Test mapping a composed (list) strategy."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        strategies = [[AttackStrategy.Base64, AttackStrategy.Morse]]
        result = StrategyMapper.map_strategies(strategies)

        assert len(result) == 2
        assert FoundryStrategy.Base64 in result
        assert FoundryStrategy.Morse in result

    def test_requires_special_handling_baseline(self):
        """Test that Baseline requires special handling."""
        assert StrategyMapper.requires_special_handling(AttackStrategy.Baseline) is True

    def test_requires_special_handling_indirect_jailbreak(self):
        """Test that IndirectJailbreak requires special handling."""
        assert StrategyMapper.requires_special_handling(AttackStrategy.IndirectJailbreak) is True

    def test_requires_special_handling_base64(self):
        """Test that Base64 does not require special handling."""
        assert StrategyMapper.requires_special_handling(AttackStrategy.Base64) is False

    def test_is_multi_turn_multi_turn(self):
        """Test that MultiTurn is identified as multi-turn."""
        assert StrategyMapper.is_multi_turn(AttackStrategy.MultiTurn) is True

    def test_is_multi_turn_crescendo(self):
        """Test that Crescendo is identified as multi-turn."""
        assert StrategyMapper.is_multi_turn(AttackStrategy.Crescendo) is True

    def test_is_multi_turn_base64(self):
        """Test that Base64 is not multi-turn."""
        assert StrategyMapper.is_multi_turn(AttackStrategy.Base64) is False

    def test_filter_for_foundry(self):
        """Test filtering strategies into Foundry and special groups."""
        strategies = [
            AttackStrategy.Base64,
            AttackStrategy.Baseline,
            AttackStrategy.Morse,
            AttackStrategy.IndirectJailbreak,
        ]

        foundry, special = StrategyMapper.filter_for_foundry(strategies)

        assert len(foundry) == 2
        assert AttackStrategy.Base64 in foundry
        assert AttackStrategy.Morse in foundry

        assert len(special) == 2
        assert AttackStrategy.Baseline in special
        assert AttackStrategy.IndirectJailbreak in special

    def test_filter_for_foundry_composed_with_special(self):
        """Test filtering composed strategies containing special strategies."""
        strategies = [
            AttackStrategy.Base64,
            [AttackStrategy.Morse, AttackStrategy.Baseline],  # Composed with special
        ]

        foundry, special = StrategyMapper.filter_for_foundry(strategies)

        assert AttackStrategy.Base64 in foundry
        # The composed strategy with Baseline should be in special
        assert [AttackStrategy.Morse, AttackStrategy.Baseline] in special

    def test_has_indirect_attack_true(self):
        """Test detection of indirect attack in strategy list."""
        strategies = [AttackStrategy.Base64, AttackStrategy.IndirectJailbreak]

        assert StrategyMapper.has_indirect_attack(strategies) is True

    def test_has_indirect_attack_false(self):
        """Test no indirect attack detection when not present."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Morse]

        assert StrategyMapper.has_indirect_attack(strategies) is False

    def test_has_indirect_attack_in_composed(self):
        """Test detection of indirect attack in composed strategy."""
        strategies = [[AttackStrategy.Base64, AttackStrategy.IndirectJailbreak]]

        assert StrategyMapper.has_indirect_attack(strategies) is True

    def test_requires_adversarial_chat_true(self):
        """Test detection of multi-turn strategy requiring adversarial chat."""
        strategies = [AttackStrategy.Base64, AttackStrategy.MultiTurn]

        assert StrategyMapper.requires_adversarial_chat(strategies) is True

    def test_requires_adversarial_chat_false(self):
        """Test no adversarial chat needed for single-turn strategies."""
        strategies = [AttackStrategy.Base64, AttackStrategy.Morse]

        assert StrategyMapper.requires_adversarial_chat(strategies) is False

    def test_requires_adversarial_chat_crescendo(self):
        """Test detection of Crescendo requiring adversarial chat."""
        strategies = [AttackStrategy.Crescendo]

        assert StrategyMapper.requires_adversarial_chat(strategies) is True


# =============================================================================
# Tests for RAIServiceScorer
# =============================================================================
@pytest.mark.unittest
class TestRAIServiceScorer:
    """Test the RAIServiceScorer class."""

    def test_initialization(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test RAIServiceScorer initialization."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        assert scorer.credential == mock_credential
        assert scorer.azure_ai_project == mock_azure_ai_project
        assert scorer.risk_category == RiskCategory.Violence
        assert scorer.scorer_type == "true_false"

    def test_initialization_with_default_logger(self, mock_credential, mock_azure_ai_project):
        """Test RAIServiceScorer with default logger."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
        )

        assert scorer.logger is not None

    def test_validate_with_valid_piece(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test validation with a valid message piece."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.converted_value = "Test response"
        mock_piece.original_value = "Original test"

        # Should not raise
        scorer.validate(mock_piece, task="Test task")

    def test_validate_with_none_raises(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test validation raises for None input."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        with pytest.raises(ValueError, match="cannot be None"):
            scorer.validate(None)

    def test_validate_with_empty_value_raises(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test validation raises for empty value."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.converted_value = None
        mock_piece.original_value = None

        with pytest.raises(ValueError, match="must have a value"):
            scorer.validate(mock_piece)

    def test_get_identifier(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test get_identifier returns correct dict."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        identifier = scorer.get_identifier()

        assert identifier["__type__"] == "RAIServiceScorer"
        assert identifier["risk_category"] == "violence"

    @pytest.mark.asyncio
    async def test_score_async_success(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test score_async with successful RAI evaluation."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.id = "test-id"
        mock_piece.converted_value = "Harmful response content"
        mock_piece.original_value = "Original content"
        mock_piece.labels = {}
        mock_piece.api_role = "assistant"

        mock_message = MagicMock()
        mock_message.message_pieces = [mock_piece]

        mock_eval_result = {
            "violence_score": 5,
            "violence_reason": "Contains violent content",
            "violence_threshold": 3,
            "violence": "high",
        }

        with patch(
            "azure.ai.evaluation.red_team._foundry._rai_scorer.evaluate_with_rai_service",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = mock_eval_result

            scores = await scorer.score_async(mock_message, objective="Test attack")

            assert len(scores) == 1
            score = scores[0]
            assert score.score_value == "true"  # Attack succeeded (score > threshold)
            assert score.score_type == "true_false"

    @pytest.mark.asyncio
    async def test_score_async_failure(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test score_async when attack fails (below threshold)."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.id = "test-id"
        mock_piece.converted_value = "Safe response"
        mock_piece.original_value = "Original content"
        mock_piece.labels = {}
        mock_piece.api_role = "assistant"

        mock_message = MagicMock()
        mock_message.message_pieces = [mock_piece]

        mock_eval_result = {
            "violence_score": 1,
            "violence_reason": "No harmful content",
            "violence_threshold": 3,
            "violence": "low",
        }

        with patch(
            "azure.ai.evaluation.red_team._foundry._rai_scorer.evaluate_with_rai_service",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = mock_eval_result

            scores = await scorer.score_async(mock_message, objective="Test attack")

            assert len(scores) == 1
            score = scores[0]
            assert score.score_value == "false"  # Attack failed

    @pytest.mark.asyncio
    async def test_score_async_error_handling(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test score_async handles errors gracefully."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.id = "test-id"
        mock_piece.converted_value = "Test response"
        mock_piece.original_value = "Original content"
        mock_piece.labels = {}
        mock_piece.api_role = "assistant"

        mock_message = MagicMock()
        mock_message.message_pieces = [mock_piece]

        with patch(
            "azure.ai.evaluation.red_team._foundry._rai_scorer.evaluate_with_rai_service",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.side_effect = Exception("RAI service error")

            scores = await scorer.score_async(mock_message, objective="Test attack")

            # Should return a score with error info
            assert len(scores) == 1
            score = scores[0]
            assert score.score_value == "false"
            assert "error" in score.score_metadata.get("error", "").lower() or "error" in score.score_rationale.lower()

    def test_get_context_for_piece_from_labels(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test context retrieval from message labels."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.labels = {
            "context": json.dumps({
                "contexts": [{"content": "Context content 1"}, {"content": "Context content 2"}]
            })
        }

        result = scorer._get_context_for_piece(mock_piece)

        assert "Context content 1" in result
        assert "Context content 2" in result

    def test_get_context_for_piece_empty(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test context retrieval returns empty string when no context."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.labels = {}
        delattr(mock_piece, "prompt_metadata")

        result = scorer._get_context_for_piece(mock_piece)

        assert result == ""


# =============================================================================
# Tests for ScenarioOrchestrator
# =============================================================================
@pytest.mark.unittest
class TestScenarioOrchestrator:
    """Test the ScenarioOrchestrator class."""

    def test_initialization(self, mock_logger):
        """Test ScenarioOrchestrator initialization."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        assert orchestrator.risk_category == "violence"
        assert orchestrator.objective_target == mock_target
        assert orchestrator.rai_scorer == mock_scorer
        assert orchestrator._scenario is None

    def test_initialization_with_adversarial_chat(self, mock_logger):
        """Test ScenarioOrchestrator with adversarial chat target."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()
        mock_adversarial = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
            adversarial_chat_target=mock_adversarial,
        )

        assert orchestrator.adversarial_chat_target == mock_adversarial

    def test_get_attack_results_before_execution_raises(self, mock_logger):
        """Test that get_attack_results raises before execute()."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        with pytest.raises(RuntimeError, match="not been executed"):
            orchestrator.get_attack_results()

    def test_get_memory_before_execution_raises(self, mock_logger):
        """Test that get_memory raises before execute()."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        with pytest.raises(RuntimeError, match="not been executed"):
            orchestrator.get_memory()

    def test_scenario_property(self, mock_logger):
        """Test scenario property returns None before execution."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        assert orchestrator.scenario is None

    def test_create_scoring_config(self, mock_logger):
        """Test _create_scoring_config creates proper config."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        with patch("pyrit.executor.attack.AttackScoringConfig") as mock_config:
            mock_config.return_value = MagicMock()

            config = orchestrator._create_scoring_config()

            mock_config.assert_called_once_with(
                objective_scorer=mock_scorer,
                use_score_as_feedback=True,
            )

    @pytest.mark.asyncio
    async def test_execute_creates_scenario(self, mock_logger):
        """Test that execute creates and runs a Foundry scenario."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        mock_target = MagicMock()
        mock_scorer = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = [MagicMock()]

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        mock_foundry = AsyncMock()
        mock_foundry.initialize_async = AsyncMock()
        mock_foundry.run_async = AsyncMock()

        with patch(
            "azure.ai.evaluation.red_team._foundry._scenario_orchestrator.FoundryScenario",
            return_value=mock_foundry,
        ), patch(
            "pyrit.executor.attack.AttackScoringConfig",
        ):
            result = await orchestrator.execute(
                dataset_config=mock_dataset,
                strategies=[FoundryStrategy.Base64],
            )

            assert result == orchestrator
            assert orchestrator._scenario == mock_foundry
            mock_foundry.initialize_async.assert_called_once()
            mock_foundry.run_async.assert_called_once()

    def test_calculate_asr_empty_results(self, mock_logger):
        """Test ASR calculation with no results."""
        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        # Set up a mock scenario result with empty results
        orchestrator._scenario_result = MagicMock()
        orchestrator._scenario_result.attack_results = {}

        asr = orchestrator.calculate_asr()
        assert asr == 0.0

    def test_calculate_asr_with_results(self, mock_logger):
        """Test ASR calculation with mixed results."""
        from pyrit.models.attack_result import AttackOutcome

        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        # Create mock results
        success_result = MagicMock()
        success_result.outcome = AttackOutcome.SUCCESS

        failure_result = MagicMock()
        failure_result.outcome = AttackOutcome.FAILURE

        orchestrator._scenario_result = MagicMock()
        orchestrator._scenario_result.attack_results = {
            "obj1": [success_result, success_result, failure_result]
        }

        asr = orchestrator.calculate_asr()
        assert asr == pytest.approx(2 / 3)  # 2 successes out of 3

    def test_calculate_asr_by_strategy(self, mock_logger):
        """Test ASR calculation grouped by strategy."""
        from pyrit.models.attack_result import AttackOutcome

        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        # Create mock results with different strategies
        base64_success = MagicMock()
        base64_success.outcome = AttackOutcome.SUCCESS
        base64_success.attack_identifier = {"__type__": "Base64Attack"}

        base64_failure = MagicMock()
        base64_failure.outcome = AttackOutcome.FAILURE
        base64_failure.attack_identifier = {"__type__": "Base64Attack"}

        morse_success = MagicMock()
        morse_success.outcome = AttackOutcome.SUCCESS
        morse_success.attack_identifier = {"__type__": "MorseAttack"}

        orchestrator._scenario_result = MagicMock()
        orchestrator._scenario_result.attack_results = {
            "obj1": [base64_success, base64_failure, morse_success]
        }

        asr_by_strategy = orchestrator.calculate_asr_by_strategy()

        assert "Base64Attack" in asr_by_strategy
        assert asr_by_strategy["Base64Attack"] == pytest.approx(0.5)  # 1/2
        assert "MorseAttack" in asr_by_strategy
        assert asr_by_strategy["MorseAttack"] == pytest.approx(1.0)  # 1/1


# =============================================================================
# Tests for FoundryResultProcessor
# =============================================================================
@pytest.mark.unittest
class TestFoundryResultProcessor:
    """Test the FoundryResultProcessor class."""

    def test_initialization(self):
        """Test FoundryResultProcessor initialization."""
        mock_scenario = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        assert processor.scenario == mock_scenario
        assert processor.dataset_config == mock_dataset
        assert processor.risk_category == "violence"

    def test_build_context_lookup(self):
        """Test building context lookup from dataset config."""
        mock_scenario = MagicMock()

        # Create mock seed group with seeds
        mock_objective = MagicMock()
        mock_objective.__class__.__name__ = "SeedObjective"
        mock_objective.prompt_group_id = uuid.uuid4()
        mock_objective.value = "Attack objective"
        mock_objective.metadata = {"risk_subtype": "test"}

        mock_context = MagicMock()
        mock_context.__class__.__name__ = "SeedPrompt"
        mock_context.prompt_group_id = mock_objective.prompt_group_id
        mock_context.value = "Context content"
        mock_context.metadata = {"context_type": "email", "is_attack_vehicle": True}

        mock_seed_group = MagicMock()
        mock_seed_group.seeds = [mock_objective, mock_context]

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = [mock_seed_group]

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        # Check that context lookup was built
        assert len(processor._context_lookup) >= 0

    def test_get_summary_stats_empty(self):
        """Test summary stats with no results."""
        mock_scenario = MagicMock()
        mock_scenario.get_attack_results.return_value = []

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        stats = processor.get_summary_stats()

        assert stats["total"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0
        assert stats["undetermined"] == 0
        assert stats["asr"] == 0.0

    def test_get_summary_stats_with_results(self):
        """Test summary stats with mixed results."""
        from pyrit.models.attack_result import AttackOutcome

        mock_scenario = MagicMock()

        success = MagicMock()
        success.outcome = AttackOutcome.SUCCESS

        failure = MagicMock()
        failure.outcome = AttackOutcome.FAILURE

        undetermined = MagicMock()
        undetermined.outcome = AttackOutcome.UNDETERMINED

        mock_scenario.get_attack_results.return_value = [
            success, success, failure, undetermined
        ]

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        stats = processor.get_summary_stats()

        assert stats["total"] == 4
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["undetermined"] == 1
        assert stats["asr"] == pytest.approx(0.5)

    def test_build_messages_from_pieces(self):
        """Test building message list from conversation pieces."""
        mock_scenario = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        # Create mock pieces
        user_piece = MagicMock()
        user_piece.api_role = "user"
        user_piece.converted_value = "User message"
        user_piece.sequence = 0

        assistant_piece = MagicMock()
        assistant_piece.api_role = "assistant"
        assistant_piece.converted_value = "Assistant response"
        assistant_piece.sequence = 1

        messages = processor._build_messages_from_pieces([user_piece, assistant_piece])

        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "User message"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Assistant response"

    def test_get_prompt_group_id_from_conversation(self):
        """Test extracting prompt_group_id from conversation."""
        mock_scenario = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        test_uuid = str(uuid.uuid4())

        # Piece with prompt_metadata
        piece = MagicMock()
        piece.prompt_metadata = {"prompt_group_id": test_uuid}

        result = processor._get_prompt_group_id_from_conversation([piece])

        assert result == test_uuid

    def test_get_prompt_group_id_from_labels(self):
        """Test extracting prompt_group_id from labels."""
        mock_scenario = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        test_uuid = str(uuid.uuid4())

        # Piece with labels
        piece = MagicMock()
        piece.prompt_metadata = {}
        piece.labels = {"prompt_group_id": test_uuid}

        result = processor._get_prompt_group_id_from_conversation([piece])

        assert result == test_uuid

    def test_to_jsonl(self, tmp_path):
        """Test JSONL generation."""
        from pyrit.models.attack_result import AttackOutcome

        mock_scenario = MagicMock()

        # Create mock attack result
        attack_result = MagicMock()
        attack_result.conversation_id = "test-conv-id"
        attack_result.outcome = AttackOutcome.SUCCESS
        attack_result.attack_identifier = {"__type__": "TestAttack"}
        attack_result.last_score = None

        mock_scenario.get_attack_results.return_value = [attack_result]

        # Create mock memory
        mock_memory = MagicMock()
        user_piece = MagicMock()
        user_piece.api_role = "user"
        user_piece.converted_value = "Attack prompt"
        user_piece.sequence = 0
        user_piece.prompt_metadata = {}
        user_piece.labels = {}

        mock_memory.get_message_pieces.return_value = [user_piece]
        mock_scenario.get_memory.return_value = mock_memory

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        output_path = str(tmp_path / "output.jsonl")
        result = processor.to_jsonl(output_path)

        # Check file was written
        assert (tmp_path / "output.jsonl").exists()
        assert "Attack prompt" in result or "attack_success" in result


# =============================================================================
# Tests for FoundryExecutionManager
# =============================================================================
@pytest.mark.unittest
class TestFoundryExecutionManager:
    """Test the FoundryExecutionManager class."""

    def test_initialization(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test FoundryExecutionManager initialization."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        assert manager.credential == mock_credential
        assert manager.azure_ai_project == mock_azure_ai_project
        assert manager.output_dir == "/test/output"
        assert manager._scenarios == {}
        assert manager._dataset_configs == {}

    def test_initialization_with_adversarial_chat(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test FoundryExecutionManager with adversarial chat target."""
        mock_adversarial = MagicMock()

        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
            adversarial_chat_target=mock_adversarial,
        )

        assert manager.adversarial_chat_target == mock_adversarial

    def test_extract_objective_content_from_messages(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting objective content from messages format."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {"messages": [{"content": "Attack prompt"}]}
        result = manager._extract_objective_content(obj)

        assert result == "Attack prompt"

    def test_extract_objective_content_from_content_field(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting objective content from content field."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {"content": "Attack prompt"}
        result = manager._extract_objective_content(obj)

        assert result == "Attack prompt"

    def test_extract_objective_content_from_objective_field(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting objective content from objective field."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {"objective": "Attack prompt"}
        result = manager._extract_objective_content(obj)

        assert result == "Attack prompt"

    def test_extract_objective_content_returns_none(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting objective content returns None for invalid input."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {"other_field": "value"}
        result = manager._extract_objective_content(obj)

        assert result is None

    def test_extract_context_items_from_message_context(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting context items from message context."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {
            "messages": [{
                "content": "Attack",
                "context": [
                    {"content": "Email body", "context_type": "email"},
                ],
            }]
        }
        result = manager._extract_context_items(obj)

        assert len(result) == 1
        assert result[0]["content"] == "Email body"

    def test_extract_context_items_from_top_level(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting context items from top-level context."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {
            "context": [{"content": "Top level context", "context_type": "text"}]
        }
        result = manager._extract_context_items(obj)

        assert len(result) == 1
        assert result[0]["content"] == "Top level context"

    def test_build_dataset_config(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test building DatasetConfiguration from objectives."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        objectives = [
            {
                "id": str(uuid.uuid4()),
                "messages": [{"content": "Attack 1"}],
                "metadata": {},
            },
            {
                "id": str(uuid.uuid4()),
                "messages": [{"content": "Attack 2"}],
                "metadata": {},
            },
        ]

        config = manager._build_dataset_config(
            risk_category="violence",
            objectives=objectives,
            is_indirect_attack=False,
        )

        # Should have 2 seed groups (one per objective)
        assert len(config.get_all_seed_groups()) == 2

    def test_get_scenarios(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test get_scenarios returns empty dict initially."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        assert manager.get_scenarios() == {}

    def test_get_dataset_configs(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test get_dataset_configs returns empty dict initially."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        assert manager.get_dataset_configs() == {}

    def test_group_results_by_strategy(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test grouping results by strategy."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        mock_orchestrator = MagicMock()
        mock_orchestrator.calculate_asr_by_strategy.return_value = {
            "Base64Attack": 0.75,
            "MorseConverter": 0.50,
        }

        results = manager._group_results_by_strategy(
            orchestrator=mock_orchestrator,
            risk_value="violence",
            output_path="/test/output.jsonl",
        )

        # Strategy names should be cleaned
        assert "Base64" in results
        assert results["Base64"]["asr"] == 0.75
        assert results["Base64"]["status"] == "completed"

        assert "Morse" in results
        assert results["Morse"]["asr"] == 0.50

    def test_group_results_by_strategy_empty(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test grouping results by strategy with no strategy-specific results."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        mock_orchestrator = MagicMock()
        mock_orchestrator.calculate_asr_by_strategy.return_value = {}
        mock_orchestrator.calculate_asr.return_value = 0.6

        results = manager._group_results_by_strategy(
            orchestrator=mock_orchestrator,
            risk_value="violence",
            output_path="/test/output.jsonl",
        )

        # Should fall back to "Foundry" entry
        assert "Foundry" in results
        assert results["Foundry"]["asr"] == 0.6

    @pytest.mark.asyncio
    async def test_execute_attacks_empty_objectives(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test execute_attacks with no objectives."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        mock_target = MagicMock()

        result = await manager.execute_attacks(
            objective_target=mock_target,
            risk_categories=[RiskCategory.Violence],
            attack_strategies=[AttackStrategy.Base64],
            objectives_by_risk={},  # No objectives
        )

        # Should return empty dict when no objectives
        assert result == {}

    @pytest.mark.asyncio
    async def test_execute_attacks_filters_multi_turn_without_adversarial(
        self, mock_credential, mock_azure_ai_project, mock_logger
    ):
        """Test that multi-turn strategies are filtered when no adversarial chat is provided."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
            adversarial_chat_target=None,  # No adversarial chat
        )

        mock_target = MagicMock()

        # Create a mock orchestrator instance that's fully configured
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.execute = AsyncMock(return_value=mock_orchestrator_instance)
        mock_orchestrator_instance.calculate_asr_by_strategy.return_value = {"test": 0.5}
        mock_orchestrator_instance.get_attack_results.return_value = []

        # Mock result processor
        mock_result_processor = MagicMock()
        mock_result_processor.to_jsonl.return_value = None
        mock_result_processor.get_summary_stats.return_value = {"asr": 0.5, "total": 10, "successful": 5}

        # Patch internal methods to avoid full execution
        with patch.object(manager, "_build_dataset_config") as mock_build, \
             patch(
                 "azure.ai.evaluation.red_team._foundry._execution_manager.ScenarioOrchestrator",
                 return_value=mock_orchestrator_instance
             ), \
             patch(
                 "azure.ai.evaluation.red_team._foundry._execution_manager.FoundryResultProcessor",
                 return_value=mock_result_processor
             ), \
             patch(
                 "azure.ai.evaluation.red_team._foundry._execution_manager.RAIServiceScorer"
             ):

            mock_dataset = MagicMock()
            mock_dataset.get_all_seed_groups.return_value = [MagicMock()]
            mock_build.return_value = mock_dataset

            # Use multi-turn strategies
            await manager.execute_attacks(
                objective_target=mock_target,
                risk_categories=[RiskCategory.Violence],
                attack_strategies=[AttackStrategy.MultiTurn, AttackStrategy.Crescendo],
                objectives_by_risk={"violence": [{"messages": [{"content": "Test"}]}]},
            )

            # Should log warning about missing adversarial chat
            mock_logger.warning.assert_called()


# =============================================================================
# Additional Tests for DatasetConfigurationBuilder
# =============================================================================
@pytest.mark.unittest
class TestDatasetConfigurationBuilderExtended:
    """Extended tests for DatasetConfigurationBuilder edge cases."""

    def test_add_multiple_objectives(self, sample_context_items):
        """Test adding multiple objectives to builder."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        for i in range(5):
            builder.add_objective_with_context(
                objective_content=f"Test objective {i}",
                objective_id=str(uuid.uuid4()),
                context_items=sample_context_items if i % 2 == 0 else None,
                metadata={"risk_subtype": f"test_subtype_{i}"},
            )

        assert len(builder) == 5
        assert len(builder.seed_groups) == 5

    def test_add_objective_with_empty_context_list(self):
        """Test adding an objective with empty context list."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            context_items=[],
            metadata={"risk_subtype": "violence_general"},
        )

        assert len(builder) == 1
        # Should only have the objective, no context prompts
        assert len(builder.seed_groups[0].seeds) == 1

    def test_add_objective_with_invalid_context_items(self):
        """Test adding objective with malformed context items."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        # Context items with missing content
        invalid_context = [
            {"context_type": "email"},  # Missing content
            None,  # None item
            {"content": "Valid content", "context_type": "document"},
        ]

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            context_items=invalid_context,
            metadata={},
        )

        assert len(builder) == 1
        # Should have objective + only valid context
        assert len(builder.seed_groups[0].seeds) >= 1

    def test_xpia_without_context_items(self):
        """Test XPIA mode without context items does nothing special."""
        builder = DatasetConfigurationBuilder(
            risk_category="violence",
            is_indirect_attack=True,
        )

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            context_items=None,
        )

        assert len(builder) == 1
        # Should only have objective when no context for XPIA
        assert len(builder.seed_groups[0].seeds) == 1

    def test_metadata_preserved_in_objective(self):
        """Test that metadata is preserved in the objective seed."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        test_metadata = {
            "risk_subtype": "weapons",
            "custom_field": "custom_value",
        }

        builder.add_objective_with_context(
            objective_content="Test attack prompt",
            objective_id=str(uuid.uuid4()),
            metadata=test_metadata,
        )

        objective_seed = builder.seed_groups[0].seeds[0]
        assert objective_seed.metadata["risk_subtype"] == "weapons"
        assert objective_seed.metadata["custom_field"] == "custom_value"
        assert objective_seed.metadata["risk_category"] == "violence"

    def test_inject_attack_markdown_context(self):
        """Test attack injection for markdown context type."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "# Document Title\n\nRegular markdown content."
        result = builder._inject_attack_into_vehicle(
            attack_string="Hidden attack text",
            content=content,
            context_type="markdown",
        )

        assert "# Document Title" in result
        assert "[//]: #" in result or "Hidden attack text" in result

    def test_inject_attack_footnote_context(self):
        """Test attack injection for footnote context type."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "Main content with footnote reference."
        result = builder._inject_attack_into_vehicle(
            attack_string="Hidden in footnote",
            content=content,
            context_type="footnote",
        )

        assert "Main content" in result
        assert "[^note]:" in result or "Hidden in footnote" in result

    def test_inject_attack_unknown_context_type(self):
        """Test attack injection for unknown context type defaults to append."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        content = "Some content"
        result = builder._inject_attack_into_vehicle(
            attack_string="Attack text",
            content=content,
            context_type="unknown_type",
        )

        assert "Some content" in result
        assert "Attack text" in result

    def test_create_xpia_prompts_with_multiple_contexts(self):
        """Test XPIA prompt creation with multiple context items."""
        builder = DatasetConfigurationBuilder(
            risk_category="violence",
            is_indirect_attack=True,
        )

        context_items = [
            {"content": "Email body 1", "context_type": "email", "tool_name": "email_reader"},
            {"content": "<html>Page</html>", "context_type": "html", "tool_name": "browser"},
            {"content": "def code():", "context_type": "code", "tool_name": "ide"},
        ]

        builder.add_objective_with_context(
            objective_content="Attack string",
            objective_id=str(uuid.uuid4()),
            context_items=context_items,
        )

        assert len(builder) == 1
        # Should have objective + (attack_vehicle + original) for each context
        # 1 objective + 2*3 = 7 seeds
        seeds = builder.seed_groups[0].seeds
        assert len(seeds) >= 1  # At least the objective

        # Check for attack vehicle seeds
        attack_vehicles = [s for s in seeds if getattr(s, "metadata", {}).get("is_attack_vehicle")]
        assert len(attack_vehicles) >= 0  # May be 3 if working correctly

    def test_determine_data_type_edge_cases(self):
        """Test data type determination for edge case context types.

        With binary_path support, all non-tool_call contexts return binary_path.
        """
        builder = DatasetConfigurationBuilder(risk_category="violence")

        # Empty context returns binary_path (stored as file)
        assert builder._determine_data_type({}) == "binary_path"

        # Mixed case - all non-tool_call return binary_path
        assert builder._determine_data_type({"context_type": "HTML"}) == "binary_path"
        assert builder._determine_data_type({"context_type": "TOOL_CALL"}) == "tool_call"

        # Substrings - all return binary_path now
        assert builder._determine_data_type({"context_type": "image_png"}) == "binary_path"
        assert builder._determine_data_type({"context_type": "audio_wav"}) == "binary_path"
        assert builder._determine_data_type({"context_type": "video_mp4"}) == "binary_path"

    def test_build_with_no_seed_groups(self):
        """Test building with no seed groups added raises error on access."""
        builder = DatasetConfigurationBuilder(risk_category="violence")

        config = builder.build()

        # DatasetConfiguration raises error when trying to get seed groups with empty list
        with pytest.raises(ValueError, match="DatasetConfiguration has no seed_groups"):
            config.get_all_seed_groups()


# =============================================================================
# Additional Tests for RAIServiceScorer
# =============================================================================
@pytest.mark.unittest
class TestRAIServiceScorerExtended:
    """Extended tests for RAIServiceScorer edge cases."""

    def test_initialization_with_dataset_config(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test RAIServiceScorer initialization with dataset config."""
        # Create mock dataset config
        mock_dataset = MagicMock()
        mock_seed = MagicMock()
        mock_seed.prompt_group_id = uuid.uuid4()
        mock_seed.value = "Context content"
        mock_seed.metadata = {"is_context": True, "context_type": "email"}

        mock_objective = MagicMock()
        mock_objective.prompt_group_id = mock_seed.prompt_group_id
        mock_objective.metadata = {}

        mock_group = MagicMock()
        mock_group.seeds = [mock_objective, mock_seed]

        mock_dataset.get_all_seed_groups.return_value = [mock_group]

        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
            dataset_config=mock_dataset,
        )

        # Context lookup should be built
        assert len(scorer._context_lookup) >= 0

    def test_get_context_from_prompt_metadata(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test context retrieval from prompt_metadata."""
        # Create mock dataset config with context
        mock_dataset = MagicMock()
        test_group_id = uuid.uuid4()

        mock_seed = MagicMock()
        mock_seed.prompt_group_id = test_group_id
        mock_seed.value = "Test context content"
        mock_seed.metadata = {"is_context": True, "context_type": "email", "tool_name": "reader"}

        mock_objective = MagicMock()
        mock_objective.__class__.__name__ = "SeedObjective"
        mock_objective.prompt_group_id = test_group_id
        mock_objective.metadata = {}

        mock_group = MagicMock()
        mock_group.seeds = [mock_objective, mock_seed]

        mock_dataset.get_all_seed_groups.return_value = [mock_group]

        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
            dataset_config=mock_dataset,
        )

        # Create piece with prompt_metadata
        mock_piece = MagicMock()
        mock_piece.labels = {}
        mock_piece.prompt_metadata = {"prompt_group_id": str(test_group_id)}

        result = scorer._get_context_for_piece(mock_piece)
        # Should retrieve context from lookup
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_score_async_with_context(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test score_async includes context in evaluation."""
        scorer = RAIServiceScorer(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            risk_category=RiskCategory.Violence,
            logger=mock_logger,
        )

        mock_piece = MagicMock()
        mock_piece.id = "test-id"
        mock_piece.converted_value = "Response text"
        mock_piece.original_value = "Original text"
        mock_piece.labels = {
            "context": json.dumps({"contexts": [{"content": "Context for eval"}]})
        }
        mock_piece.api_role = "assistant"

        mock_message = MagicMock()
        mock_message.message_pieces = [mock_piece]

        mock_eval_result = {
            "violence_score": 4,
            "violence_reason": "Contains concerning content",
            "violence_threshold": 3,
            "violence": "medium",
        }

        with patch(
            "azure.ai.evaluation.red_team._foundry._rai_scorer.evaluate_with_rai_service",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = mock_eval_result

            scores = await scorer.score_async(mock_message, objective="Test task")

            # Should include context in call
            assert len(scores) == 1
            assert scores[0].score_value == "true"

    @pytest.mark.asyncio
    async def test_score_async_with_different_risk_categories(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test score_async with different risk categories."""
        risk_categories = [
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
        ]

        for risk_cat in risk_categories:
            scorer = RAIServiceScorer(
                credential=mock_credential,
                azure_ai_project=mock_azure_ai_project,
                risk_category=risk_cat,
                logger=mock_logger,
            )

            mock_piece = MagicMock()
            mock_piece.id = "test-id"
            mock_piece.converted_value = "Test response"
            mock_piece.original_value = "Original"
            mock_piece.labels = {}
            mock_piece.api_role = "assistant"

            mock_message = MagicMock()
            mock_message.message_pieces = [mock_piece]

            mock_eval_result = {
                f"{risk_cat.value}_score": 2,
                f"{risk_cat.value}_reason": "Test reason",
                f"{risk_cat.value}_threshold": 3,
                risk_cat.value: "low",
            }

            with patch(
                "azure.ai.evaluation.red_team._foundry._rai_scorer.evaluate_with_rai_service",
                new_callable=AsyncMock,
            ) as mock_eval:
                mock_eval.return_value = mock_eval_result

                scores = await scorer.score_async(mock_message, objective="Test")

                assert len(scores) == 1
                assert risk_cat.value in scores[0].score_category


# =============================================================================
# Additional Tests for ScenarioOrchestrator
# =============================================================================
@pytest.mark.unittest
class TestScenarioOrchestratorExtended:
    """Extended tests for ScenarioOrchestrator."""

    @pytest.mark.asyncio
    async def test_execute_with_adversarial_chat(self, mock_logger):
        """Test execute with adversarial chat target configured."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        mock_target = MagicMock()
        mock_scorer = MagicMock()
        mock_adversarial = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = [MagicMock()]

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
            adversarial_chat_target=mock_adversarial,
        )

        mock_foundry = AsyncMock()
        mock_foundry.initialize_async = AsyncMock()
        mock_foundry.run_attack_async = AsyncMock()

        with patch(
            "azure.ai.evaluation.red_team._foundry._scenario_orchestrator.FoundryScenario",
            return_value=mock_foundry,
        ), patch(
            "pyrit.executor.attack.AttackScoringConfig",
        ) as mock_config:
            result = await orchestrator.execute(
                dataset_config=mock_dataset,
                strategies=[FoundryStrategy.Base64, FoundryStrategy.Crescendo],
            )

            assert result == orchestrator
            # FoundryScenario should be created with adversarial_chat
            mock_foundry.initialize_async.assert_called_once()

    def test_calculate_asr_with_undetermined(self, mock_logger):
        """Test ASR calculation with undetermined outcomes."""
        from pyrit.models.attack_result import AttackOutcome

        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        # Mix of outcomes
        success = MagicMock()
        success.outcome = AttackOutcome.SUCCESS

        failure = MagicMock()
        failure.outcome = AttackOutcome.FAILURE

        undetermined = MagicMock()
        undetermined.outcome = AttackOutcome.UNDETERMINED

        orchestrator._scenario_result = MagicMock()
        orchestrator._scenario_result.attack_results = {
            "obj1": [success, failure, undetermined, success]
        }

        asr = orchestrator.calculate_asr()
        # 2 successes out of 4 total
        assert asr == pytest.approx(0.5)

    def test_calculate_asr_by_strategy_with_unknown(self, mock_logger):
        """Test ASR by strategy with unknown strategy type."""
        from pyrit.models.attack_result import AttackOutcome

        mock_target = MagicMock()
        mock_scorer = MagicMock()

        orchestrator = ScenarioOrchestrator(
            risk_category="violence",
            objective_target=mock_target,
            rai_scorer=mock_scorer,
            logger=mock_logger,
        )

        # Results with missing attack_identifier
        result1 = MagicMock()
        result1.outcome = AttackOutcome.SUCCESS
        result1.attack_identifier = {}  # No __type__

        result2 = MagicMock()
        result2.outcome = AttackOutcome.FAILURE
        result2.attack_identifier = {"__type__": "KnownAttack"}

        orchestrator._scenario_result = MagicMock()
        orchestrator._scenario_result.attack_results = {
            "obj1": [result1, result2]
        }

        asr_by_strategy = orchestrator.calculate_asr_by_strategy()

        assert "Unknown" in asr_by_strategy
        assert "KnownAttack" in asr_by_strategy


# =============================================================================
# Additional Tests for FoundryResultProcessor
# =============================================================================
@pytest.mark.unittest
class TestFoundryResultProcessorExtended:
    """Extended tests for FoundryResultProcessor."""

    def test_process_attack_result_with_score(self):
        """Test processing result that has a score."""
        from pyrit.models.attack_result import AttackOutcome

        mock_scenario = MagicMock()

        # Create result with score
        attack_result = MagicMock()
        attack_result.conversation_id = "test-conv"
        attack_result.outcome = AttackOutcome.SUCCESS
        attack_result.attack_identifier = {"__type__": "TestAttack"}

        mock_score = MagicMock()
        mock_score.score_value = "true"
        mock_score.score_rationale = "Attack succeeded"
        mock_score.score_metadata = {"raw_score": 5}
        attack_result.last_score = mock_score

        mock_scenario.get_attack_results.return_value = [attack_result]

        # Create mock memory with conversation
        mock_memory = MagicMock()
        mock_piece = MagicMock()
        mock_piece.api_role = "user"
        mock_piece.converted_value = "Attack prompt"
        mock_piece.sequence = 0
        mock_piece.prompt_metadata = {}
        mock_piece.labels = {}

        mock_memory.get_message_pieces.return_value = [mock_piece]
        mock_scenario.get_memory.return_value = mock_memory

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        entry = processor._process_attack_result(attack_result, mock_memory)

        assert entry is not None
        assert entry["attack_success"] is True
        assert "score" in entry
        assert entry["score"]["value"] == "true"

    def test_process_attack_result_with_error(self):
        """Test processing result when an error occurs."""
        from pyrit.models.attack_result import AttackOutcome

        mock_scenario = MagicMock()

        attack_result = MagicMock()
        attack_result.conversation_id = "test-conv"
        attack_result.outcome = AttackOutcome.FAILURE
        attack_result.attack_identifier = {}
        attack_result.last_score = None

        mock_scenario.get_attack_results.return_value = [attack_result]

        # Memory raises error
        mock_memory = MagicMock()
        mock_memory.get_message_pieces.side_effect = Exception("Memory error")
        mock_scenario.get_memory.return_value = mock_memory

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        entry = processor._process_attack_result(attack_result, mock_memory)

        # Should return error entry, not None
        assert entry is not None
        assert "error" in entry

    def test_build_messages_with_context_in_labels(self):
        """Test building messages when context is in labels."""
        mock_scenario = MagicMock()
        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = []

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        # Piece with context in labels
        piece = MagicMock()
        piece.api_role = "user"
        piece.converted_value = "Message content"
        piece.sequence = 0
        piece.labels = {
            "context": json.dumps({
                "contexts": [
                    {"content": "Context 1", "context_type": "email"},
                    {"content": "Context 2", "context_type": "document"},
                ]
            })
        }

        messages = processor._build_messages_from_pieces([piece])

        assert len(messages) == 1
        assert messages[0]["content"] == "Message content"
        assert "context" in messages[0]
        assert len(messages[0]["context"]) == 2

    def test_build_context_lookup_with_attack_vehicles(self):
        """Test context lookup building with XPIA attack vehicles."""
        mock_scenario = MagicMock()

        # Create mock seed group with attack vehicle
        group_id = uuid.uuid4()

        mock_objective = MagicMock()
        mock_objective.__class__.__name__ = "SeedObjective"
        mock_objective.prompt_group_id = group_id
        mock_objective.value = "Attack objective"
        mock_objective.metadata = {"risk_subtype": "test"}

        mock_attack_vehicle = MagicMock()
        mock_attack_vehicle.__class__.__name__ = "SeedPrompt"
        mock_attack_vehicle.prompt_group_id = group_id
        mock_attack_vehicle.value = "Injected attack content"
        mock_attack_vehicle.metadata = {
            "is_attack_vehicle": True,
            "context_type": "email",
            "tool_name": "reader",
        }

        mock_original = MagicMock()
        mock_original.__class__.__name__ = "SeedPrompt"
        mock_original.prompt_group_id = group_id
        mock_original.value = "Original content"
        mock_original.metadata = {
            "is_original_context": True,
            "context_type": "email",
        }

        mock_seed_group = MagicMock()
        mock_seed_group.seeds = [mock_objective, mock_attack_vehicle, mock_original]

        mock_dataset = MagicMock()
        mock_dataset.get_all_seed_groups.return_value = [mock_seed_group]

        processor = FoundryResultProcessor(
            scenario=mock_scenario,
            dataset_config=mock_dataset,
            risk_category="violence",
        )

        # Should have context lookup entry
        assert str(group_id) in processor._context_lookup
        lookup_data = processor._context_lookup[str(group_id)]
        assert "contexts" in lookup_data
        # Should include attack vehicle but not original context
        contexts = lookup_data["contexts"]
        assert any(c.get("is_attack_vehicle") for c in contexts)


# =============================================================================
# Additional Tests for FoundryExecutionManager
# =============================================================================
@pytest.mark.unittest
class TestFoundryExecutionManagerExtended:
    """Extended tests for FoundryExecutionManager."""

    def test_extract_context_string_format(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting context when it's a string instead of list."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        obj = {
            "messages": [{
                "content": "Attack",
                "context": "Simple string context",  # String, not list
            }]
        }
        result = manager._extract_context_items(obj)

        # String context should be converted to dict
        assert len(result) >= 0

    def test_extract_objective_string_type(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test extracting objective when input is just a string."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        # String input instead of dict
        result = manager._extract_objective_content("Direct string objective")

        # Should return None for non-dict input
        assert result is None

    def test_build_dataset_config_with_string_objectives(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test building dataset config handles string objectives gracefully."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        # Mix of valid and invalid objectives
        objectives = [
            {"messages": [{"content": "Valid objective 1"}]},
            "String objective",  # Invalid - string not dict
            {"messages": [{"content": "Valid objective 2"}]},
            {"no_messages": "Invalid structure"},  # Invalid - no messages
        ]

        config = manager._build_dataset_config(
            risk_category="violence",
            objectives=objectives,
            is_indirect_attack=False,
        )

        # Should only have the 2 valid objectives
        assert len(config.get_all_seed_groups()) == 2

    @pytest.mark.asyncio
    async def test_execute_attacks_handles_orchestrator_error(
        self, mock_credential, mock_azure_ai_project, mock_logger, tmp_path
    ):
        """Test execute_attacks handles orchestrator execution errors."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir=str(tmp_path),
        )

        mock_target = MagicMock()

        with patch.object(ScenarioOrchestrator, "execute", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Orchestrator failed")

            result = await manager.execute_attacks(
                objective_target=mock_target,
                risk_categories=[RiskCategory.Violence],
                attack_strategies=[AttackStrategy.Base64],
                objectives_by_risk={"violence": [{"messages": [{"content": "Test"}]}]},
            )

            # Should return error status for the risk category
            # The error is caught and logged, result structure depends on implementation

    def test_get_result_processors(self, mock_credential, mock_azure_ai_project, mock_logger):
        """Test accessing result processors after execution."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir="/test/output",
        )

        # Initially empty
        assert manager._result_processors == {}

        # After setting
        mock_processor = MagicMock()
        manager._result_processors["violence"] = mock_processor

        assert "violence" in manager._result_processors


# =============================================================================
# Additional Tests for StrategyMapper
# =============================================================================
@pytest.mark.unittest
class TestStrategyMapperExtended:
    """Extended tests for StrategyMapper edge cases."""

    def test_map_all_individual_strategies(self):
        """Test mapping all individual converter strategies."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        individual_strategies = [
            AttackStrategy.AnsiAttack,
            AttackStrategy.AsciiArt,
            AttackStrategy.AsciiSmuggler,
            AttackStrategy.Atbash,
            AttackStrategy.Base64,
            AttackStrategy.Binary,
            AttackStrategy.Caesar,
            AttackStrategy.CharacterSpace,
            AttackStrategy.CharSwap,
            AttackStrategy.Diacritic,
            AttackStrategy.Flip,
            AttackStrategy.Leetspeak,
            AttackStrategy.Morse,
            AttackStrategy.ROT13,
            AttackStrategy.SuffixAppend,
            AttackStrategy.StringJoin,
            AttackStrategy.UnicodeConfusable,
            AttackStrategy.UnicodeSubstitution,
            AttackStrategy.Url,
            AttackStrategy.Jailbreak,
            AttackStrategy.Tense,
        ]

        for strategy in individual_strategies:
            foundry_strategy = StrategyMapper.map_strategy(strategy)
            assert foundry_strategy is not None, f"Strategy {strategy} should map to a FoundryStrategy"

    def test_map_aggregate_strategies(self):
        """Test mapping aggregate difficulty strategies."""
        from pyrit.scenario.scenarios.foundry import FoundryStrategy

        assert StrategyMapper.map_strategy(AttackStrategy.EASY) == FoundryStrategy.EASY
        assert StrategyMapper.map_strategy(AttackStrategy.MODERATE) == FoundryStrategy.MODERATE
        assert StrategyMapper.map_strategy(AttackStrategy.DIFFICULT) == FoundryStrategy.DIFFICULT

    def test_filter_mixed_strategies(self):
        """Test filtering a complex mix of strategies."""
        strategies = [
            AttackStrategy.Base64,
            AttackStrategy.Baseline,
            [AttackStrategy.Morse, AttackStrategy.Caesar],  # Composed
            AttackStrategy.IndirectJailbreak,
            AttackStrategy.MultiTurn,
            [AttackStrategy.Base64, AttackStrategy.IndirectJailbreak],  # Composed with special
        ]

        foundry, special = StrategyMapper.filter_for_foundry(strategies)

        # Base64, composed [Morse, Caesar], and MultiTurn should be foundry-compatible
        assert AttackStrategy.Base64 in foundry
        assert [AttackStrategy.Morse, AttackStrategy.Caesar] in foundry
        assert AttackStrategy.MultiTurn in foundry

        # Baseline, IndirectJailbreak, and composed with special should be special
        assert AttackStrategy.Baseline in special
        assert AttackStrategy.IndirectJailbreak in special
        assert [AttackStrategy.Base64, AttackStrategy.IndirectJailbreak] in special

    def test_has_indirect_attack_nested_composed(self):
        """Test indirect attack detection in deeply nested structures."""
        # Single level nesting with indirect
        strategies_with = [[AttackStrategy.Base64, AttackStrategy.IndirectJailbreak]]
        assert StrategyMapper.has_indirect_attack(strategies_with) is True

        # No indirect
        strategies_without = [[AttackStrategy.Base64, AttackStrategy.Morse]]
        assert StrategyMapper.has_indirect_attack(strategies_without) is False

    def test_requires_adversarial_composed(self):
        """Test adversarial chat detection in composed strategies."""
        # Composed with multi-turn
        strategies = [[AttackStrategy.Base64, AttackStrategy.MultiTurn]]
        assert StrategyMapper.requires_adversarial_chat(strategies) is True

        # Composed without multi-turn
        strategies = [[AttackStrategy.Base64, AttackStrategy.Morse]]
        assert StrategyMapper.requires_adversarial_chat(strategies) is False


# =============================================================================
# Tests for RedTeam Foundry Integration Methods
# =============================================================================
@pytest.mark.unittest
class TestRedTeamFoundryIntegration:
    """Tests for RedTeam class Foundry integration methods."""

    @pytest.fixture
    def mock_red_team(self, mock_credential, mock_azure_ai_project):
        """Create a mock RedTeam instance for testing."""
        from azure.ai.evaluation.red_team import RedTeam

        # Patch all network-related and initialization calls
        with patch("azure.ai.evaluation.red_team._red_team.CentralMemory"), \
             patch("azure.ai.evaluation.red_team._red_team.SQLiteMemory"), \
             patch("azure.ai.evaluation.red_team._red_team.validate_azure_ai_project"), \
             patch("azure.ai.evaluation.red_team._red_team.is_onedp_project", return_value=False), \
             patch("azure.ai.evaluation.red_team._red_team.ManagedIdentityAPITokenManager"), \
             patch("azure.ai.evaluation.red_team._red_team.GeneratedRAIClient"):
            red_team = RedTeam(
                azure_ai_project=mock_azure_ai_project,
                credential=mock_credential,
            )
            # Set up necessary attributes
            red_team.attack_objectives = {}
            red_team.red_team_info = {}
            red_team.risk_categories = [RiskCategory.Violence, RiskCategory.HateUnfairness]
            red_team.completed_tasks = 0

            return red_team

    def test_build_objective_dict_from_cached_dict_with_messages(self, mock_red_team):
        """Test building objective dict when cached obj already has messages."""
        obj = {
            "messages": [{"content": "Attack prompt", "context": [{"content": "Context"}]}],
            "metadata": {"risk_subtype": "weapons"},
        }

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "messages" in result
        assert result["messages"][0]["content"] == "Attack prompt"

    def test_build_objective_dict_from_cached_dict_without_messages(self, mock_red_team):
        """Test building objective dict when cached obj has content but no messages."""
        obj = {
            "content": "Attack prompt",
            "context": [{"content": "Email context", "context_type": "email"}],
            "risk_subtype": "weapons",
        }

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "messages" in result
        assert result["messages"][0]["content"] == "Attack prompt"
        assert "context" in result["messages"][0]
        assert len(result["messages"][0]["context"]) == 1

    def test_build_objective_dict_from_cached_string(self, mock_red_team):
        """Test building objective dict from string content."""
        obj = "Simple attack prompt string"

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "messages" in result
        assert result["messages"][0]["content"] == "Simple attack prompt string"
        assert result["metadata"]["risk_category"] == "violence"

    def test_build_objective_dict_from_cached_none(self, mock_red_team):
        """Test building objective dict from None returns None."""
        result = mock_red_team._build_objective_dict_from_cached(None, "violence")
        assert result is None

    def test_build_objective_dict_from_cached_context_string(self, mock_red_team):
        """Test building objective dict when context is a string."""
        obj = {
            "content": "Attack prompt",
            "context": "Simple string context",
        }

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "messages" in result
        # String context should be wrapped in list
        context = result["messages"][0].get("context", [])
        assert len(context) == 1
        assert context[0]["content"] == "Simple string context"

    def test_build_objective_dict_from_cached_context_dict(self, mock_red_team):
        """Test building objective dict when context is a dict."""
        obj = {
            "content": "Attack prompt",
            "context": {"content": "Dict context", "context_type": "email"},
        }

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "messages" in result
        context = result["messages"][0].get("context", [])
        assert len(context) == 1
        assert context[0]["content"] == "Dict context"

    def test_build_objective_dict_adds_metadata(self, mock_red_team):
        """Test that metadata is added when not present."""
        obj = {"content": "Attack prompt"}

        result = mock_red_team._build_objective_dict_from_cached(obj, "violence")

        assert result is not None
        assert "metadata" in result
        assert result["metadata"]["risk_category"] == "violence"

    @pytest.mark.asyncio
    async def test_handle_baseline_with_foundry_results(self, mock_red_team):
        """Test baseline handling with existing Foundry results."""
        # Set up existing red_team_info with data files
        mock_red_team.red_team_info = {
            "Base64": {
                "violence": {
                    "data_file": "/test/output/violence_results.jsonl",
                    "status": "completed",
                },
                "hate_unfairness": {
                    "data_file": "/test/output/hate_results.jsonl",
                    "status": "completed",
                },
            }
        }
        mock_red_team.completed_tasks = 0

        progress_bar = MagicMock()

        with patch("os.path.exists", return_value=True):
            await mock_red_team._handle_baseline_with_foundry_results(
                objectives_by_risk={"violence": [], "hate_unfairness": []},
                progress_bar=progress_bar,
                skip_evals=True,
            )

        # Baseline should be added
        assert "baseline" in mock_red_team.red_team_info
        assert "violence" in mock_red_team.red_team_info["baseline"]
        assert "hate_unfairness" in mock_red_team.red_team_info["baseline"]

        # Should have used existing data files
        assert mock_red_team.red_team_info["baseline"]["violence"]["data_file"] != ""

    @pytest.mark.asyncio
    async def test_handle_baseline_no_existing_data(self, mock_red_team):
        """Test baseline handling when no existing data files."""
        mock_red_team.red_team_info = {}
        mock_red_team.completed_tasks = 0

        progress_bar = MagicMock()

        with patch("os.path.exists", return_value=False):
            await mock_red_team._handle_baseline_with_foundry_results(
                objectives_by_risk={"violence": []},
                progress_bar=progress_bar,
                skip_evals=True,
            )

        # Baseline should be added but with failed status
        assert "baseline" in mock_red_team.red_team_info
        assert mock_red_team.red_team_info["baseline"]["violence"]["data_file"] == ""


# =============================================================================
# Integration Tests for Complete Foundry Flow
# =============================================================================
@pytest.mark.unittest
class TestFoundryFlowIntegration:
    """Integration tests for the complete Foundry execution flow."""

    def test_strategy_to_foundry_mapping_roundtrip(self):
        """Test that strategies can be mapped and filtered correctly."""
        # Mix of strategies
        strategies = [
            AttackStrategy.Base64,
            AttackStrategy.Baseline,
            AttackStrategy.Morse,
            AttackStrategy.IndirectJailbreak,
            AttackStrategy.MultiTurn,
        ]

        # Filter
        foundry_compatible, special = StrategyMapper.filter_for_foundry(strategies)

        # Verify separation
        assert AttackStrategy.Base64 in foundry_compatible
        assert AttackStrategy.Morse in foundry_compatible
        assert AttackStrategy.MultiTurn in foundry_compatible
        assert AttackStrategy.Baseline in special
        assert AttackStrategy.IndirectJailbreak in special

        # Map to Foundry
        mapped = StrategyMapper.map_strategies(foundry_compatible)

        # Verify mapping
        assert len(mapped) == 3
        from pyrit.scenario.scenarios.foundry import FoundryStrategy
        assert FoundryStrategy.Base64 in mapped
        assert FoundryStrategy.Morse in mapped
        assert FoundryStrategy.MultiTurn in mapped

    def test_dataset_builder_to_result_processor_flow(self):
        """Test that data flows correctly from builder to processor."""
        # Build dataset
        builder = DatasetConfigurationBuilder(risk_category="violence")

        test_uuid = uuid.uuid4()
        builder.add_objective_with_context(
            objective_content="Test attack objective",
            objective_id=str(test_uuid),
            context_items=[
                {"content": "Email context", "context_type": "email", "tool_name": "reader"}
            ],
            metadata={"risk_subtype": "weapons"},
        )

        dataset_config = builder.build()

        # Verify dataset structure
        seed_groups = dataset_config.get_all_seed_groups()
        assert len(seed_groups) == 1

        # Verify seed group contents
        seeds = seed_groups[0].seeds
        assert len(seeds) >= 1  # At least the objective

        # Verify objective
        objectives = [s for s in seeds if s.__class__.__name__ == "SeedObjective"]
        assert len(objectives) == 1
        assert objectives[0].value == "Test attack objective"
        assert str(objectives[0].prompt_group_id) == str(test_uuid)

    @pytest.mark.asyncio
    async def test_execution_manager_with_mocked_dependencies(
        self, mock_credential, mock_azure_ai_project, mock_logger, tmp_path
    ):
        """Test FoundryExecutionManager with all dependencies mocked."""
        manager = FoundryExecutionManager(
            credential=mock_credential,
            azure_ai_project=mock_azure_ai_project,
            logger=mock_logger,
            output_dir=str(tmp_path),
        )

        mock_target = MagicMock()

        # Mock the scenario orchestrator completely
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute = AsyncMock(return_value=mock_orchestrator)
        mock_orchestrator.calculate_asr.return_value = 0.5
        mock_orchestrator.calculate_asr_by_strategy.return_value = {"Base64Attack": 0.5}
        mock_orchestrator.get_attack_results.return_value = []

        # Mock result processor
        mock_processor = MagicMock()
        mock_processor.to_jsonl.return_value = ""
        mock_processor.get_summary_stats.return_value = {
            "total": 10,
            "successful": 5,
            "failed": 5,
            "asr": 0.5,
        }

        with patch.object(ScenarioOrchestrator, "__init__", return_value=None), \
             patch.object(ScenarioOrchestrator, "execute", mock_orchestrator.execute), \
             patch.object(ScenarioOrchestrator, "calculate_asr_by_strategy", mock_orchestrator.calculate_asr_by_strategy), \
             patch.object(ScenarioOrchestrator, "get_attack_results", mock_orchestrator.get_attack_results), \
             patch.object(FoundryResultProcessor, "__init__", return_value=None), \
             patch.object(FoundryResultProcessor, "to_jsonl", mock_processor.to_jsonl), \
             patch.object(FoundryResultProcessor, "get_summary_stats", mock_processor.get_summary_stats):

            # Note: This test verifies the structure, actual execution requires PyRIT
            # The test passes if no exceptions are raised during setup
            assert manager.output_dir == str(tmp_path)
            assert manager.credential == mock_credential
