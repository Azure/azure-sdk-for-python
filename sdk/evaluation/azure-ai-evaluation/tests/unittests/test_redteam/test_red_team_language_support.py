import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation.red_team._red_team import RedTeam, RiskCategory, SupportedLanguages
from azure.core.credentials import TokenCredential


@pytest.fixture
def mock_azure_ai_project():
    return {
        "subscription_id": "test-subscription",
        "resource_group_name": "test-resource-group",
        "project_name": "test-project",
    }


@pytest.fixture
def mock_credential():
    return MagicMock(spec=TokenCredential)


class TestRedTeamLanguageSupport:
    """Test language support functionality in RedTeam class."""

    def test_red_team_init_default_language(self, mock_azure_ai_project, mock_credential):
        """Test that RedTeam initializes with default English language."""
        with patch("azure.ai.evaluation.red_team._red_team.GeneratedRAIClient"), patch(
            "azure.ai.evaluation.red_team._red_team.setup_logger"
        ) as mock_setup_logger, patch("azure.ai.evaluation.red_team._red_team.initialize_pyrit"), patch(
            "azure.ai.evaluation.red_team._red_team._AttackObjectiveGenerator"
        ):

            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger

            agent = RedTeam(
                azure_ai_project=mock_azure_ai_project,
                credential=mock_credential,
                risk_categories=[RiskCategory.Violence],
                num_objectives=5,
            )

            # Verify default language is English
            assert agent.language == SupportedLanguages.English

    def test_red_team_init_custom_language(self, mock_azure_ai_project, mock_credential):
        """Test that RedTeam initializes with custom language."""
        with patch("azure.ai.evaluation.red_team._red_team.GeneratedRAIClient"), patch(
            "azure.ai.evaluation.red_team._red_team.setup_logger"
        ) as mock_setup_logger, patch("azure.ai.evaluation.red_team._red_team.initialize_pyrit"), patch(
            "azure.ai.evaluation.red_team._red_team._AttackObjectiveGenerator"
        ):

            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger

            # Test with Spanish language
            agent = RedTeam(
                azure_ai_project=mock_azure_ai_project,
                credential=mock_credential,
                risk_categories=[RiskCategory.Violence],
                num_objectives=5,
                language=SupportedLanguages.Spanish,
            )

            assert agent.language == SupportedLanguages.Spanish

    @pytest.mark.parametrize(
        "language",
        [
            SupportedLanguages.English,
            SupportedLanguages.Spanish,
            SupportedLanguages.French,
            SupportedLanguages.German,
            SupportedLanguages.Italian,
            SupportedLanguages.Portuguese,
            SupportedLanguages.Japanese,
            SupportedLanguages.Korean,
            SupportedLanguages.SimplifiedChinese,
        ],
    )
    def test_red_team_init_all_supported_languages(self, mock_azure_ai_project, mock_credential, language):
        """Test that RedTeam initializes correctly with all supported languages."""
        with patch("azure.ai.evaluation.red_team._red_team.GeneratedRAIClient"), patch(
            "azure.ai.evaluation.red_team._red_team.setup_logger"
        ) as mock_setup_logger, patch("azure.ai.evaluation.red_team._red_team.initialize_pyrit"), patch(
            "azure.ai.evaluation.red_team._red_team._AttackObjectiveGenerator"
        ):

            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger

            agent = RedTeam(
                azure_ai_project=mock_azure_ai_project,
                credential=mock_credential,
                risk_categories=[RiskCategory.Violence],
                num_objectives=5,
                language=language,
            )

            assert agent.language == language

    @pytest.mark.asyncio
    async def test_get_attack_objectives_passes_language(self, mock_azure_ai_project, mock_credential):
        """Test that _get_attack_objectives passes language parameter to generated RAI client."""
        with patch("azure.ai.evaluation.red_team._red_team.GeneratedRAIClient") as mock_rai_client_class, patch(
            "azure.ai.evaluation.red_team._red_team.setup_logger"
        ) as mock_setup_logger, patch("azure.ai.evaluation.red_team._red_team.initialize_pyrit"), patch(
            "azure.ai.evaluation.red_team._red_team._AttackObjectiveGenerator"
        ) as mock_attack_obj_generator_class:

            mock_logger = MagicMock()
            mock_setup_logger.return_value = mock_logger

            # Set up mock RAI client instance
            mock_rai_client = MagicMock()
            mock_rai_client.get_attack_objectives = AsyncMock(
                return_value=[
                    {
                        "id": "test-id",
                        "messages": [{"role": "user", "content": "test prompt"}],
                        "metadata": {"target_harms": [{"risk-type": "violence"}]},
                    }
                ]
            )
            mock_rai_client_class.return_value = mock_rai_client

            # Set up mock attack objective generator instance
            mock_attack_obj_generator = MagicMock()
            mock_attack_obj_generator.num_objectives = 5
            mock_attack_obj_generator.custom_attack_seed_prompts = None
            mock_attack_obj_generator.validated_prompts = False
            mock_attack_obj_generator_class.return_value = mock_attack_obj_generator

            # Create RedTeam instance with Spanish language
            agent = RedTeam(
                azure_ai_project=mock_azure_ai_project,
                credential=mock_credential,
                risk_categories=[RiskCategory.Violence],
                num_objectives=5,
                language=SupportedLanguages.Spanish,
            )

            agent.generated_rai_client = mock_rai_client
            agent.scan_session_id = "test-session"

            # Call _get_attack_objectives
            await agent._get_attack_objectives(
                risk_category=RiskCategory.Violence,
                application_scenario="test scenario",
                strategy="baseline",
            )

            # Verify that get_attack_objectives was called with Spanish language
            mock_rai_client.get_attack_objectives.assert_called_once()
            call_args = mock_rai_client.get_attack_objectives.call_args
            assert call_args.kwargs["language"] == SupportedLanguages.Spanish.value
