import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation.red_team_agent.red_team_agent import (
    RedTeamAgent, RiskCategory, AttackStrategy
)
from azure.ai.evaluation._exceptions import EvaluationException
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


@pytest.fixture
def red_team_agent(mock_azure_ai_project, mock_credential):
    return RedTeamAgent(
        azure_ai_project=mock_azure_ai_project, credential=mock_credential
    )


@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
def test_red_team_agent_initialization(mock_rai_client, red_team_agent):
    mock_rai_client.return_value = MagicMock()
    assert red_team_agent.azure_ai_project is not None
    assert red_team_agent.credential is not None
    assert red_team_agent.logger is not None
    assert red_team_agent.token_manager is not None
    assert red_team_agent.rai_client is not None
    assert red_team_agent.generated_rai_client is not None


@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
def test_start_redteam_mlflow_run_no_project(mock_rai_client, red_team_agent):
    mock_rai_client.return_value = MagicMock()
    with pytest.raises(EvaluationException) as exc_info:
        red_team_agent._start_redteam_mlflow_run(azure_ai_project=None)
    assert "No azure_ai_project provided" in str(exc_info.value)


@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
@patch(
    "azure.ai.evaluation.red_team_agent.red_team_agent._trace_destination_from_project_scope"
)
@patch("azure.ai.evaluation.red_team_agent.red_team_agent.LiteMLClient")
def test_start_redteam_mlflow_run(
    mock_lite_ml_client, mock_trace_destination, mock_rai_client,
    red_team_agent, mock_azure_ai_project
):
    mock_rai_client.return_value = MagicMock()
    mock_trace_destination.return_value = "mock-trace-destination"
    mock_lite_ml_client.return_value.workspace_get_info.return_value = (
        MagicMock(ml_flow_tracking_uri="mock-tracking-uri")
    )

    eval_run = red_team_agent._start_redteam_mlflow_run(
        azure_ai_project=mock_azure_ai_project, run_name="test-run"
    )
    assert eval_run is not None
    assert eval_run.run_name == "test-run"


@pytest.mark.asyncio
@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
async def test_get_attack_objectives_no_risk_category(
    mock_rai_client, red_team_agent
):
    mock_rai_client.return_value = MagicMock()
    mock_attack_objective_generator = MagicMock(
        risk_categories=[RiskCategory.Violence], num_objectives=5
    )

    with patch.object(
        red_team_agent.generated_rai_client, "get_attack_objectives",
        new_callable=AsyncMock
    ) as mock_get_attack_objectives:
        mock_get_attack_objectives.return_value = [
            {"messages": [{"content": "test-objective"}]}
        ]
        objectives = await red_team_agent._get_attack_objectives(
            mock_attack_objective_generator
        )
        assert len(objectives) == 1
        assert objectives[0] == "test-objective"


@pytest.mark.asyncio
@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
async def test_process_attack(mock_rai_client, red_team_agent):
    mock_rai_client.return_value = MagicMock()
    mock_orchestrator = AsyncMock(
        get_memory=AsyncMock(return_value=[]),
        dispose_db_engine=AsyncMock(return_value=None)
    )

    with patch.object(
        red_team_agent, "_prompt_sending_orchestrator",
        return_value=mock_orchestrator
    ), patch.object(
        red_team_agent, "_write_pyrit_outputs_to_file",
        return_value="mock-data-path"
    ), patch.object(
        red_team_agent, "_evaluate", new_callable=AsyncMock
    ) as mock_evaluate:
        await red_team_agent._process_attack(
            target=MagicMock(),
            call_orchestrator=red_team_agent._prompt_sending_orchestrator,
            strategy=AttackStrategy.Baseline,
            risk_category=RiskCategory.Violence,
            all_prompts=["test-prompt"],
            progress_bar=MagicMock(),
            progress_bar_lock=AsyncMock(),
        )
        mock_evaluate.assert_called_once()


@pytest.mark.asyncio
@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient", new_callable=AsyncMock)
@patch(
    "azure.ai.evaluation.red_team_agent.red_team_agent._trace_destination_from_project_scope"
)
async def test_scan_no_attack_objective_generator(
    mock_trace_destination, mock_rai_client
):
    red_team_agent = AsyncMock()  # Ensure red_team_agent is an AsyncMock
    mock_rai_client.return_value = AsyncMock()

    with pytest.raises(EvaluationException) as exc_info:
        await red_team_agent.scan(
            target=AsyncMock(),  # Use AsyncMock for async calls
            attack_objective_generator=None,
        )
    assert (
        "Attack objective generator is required for red team agent."
        in str(exc_info.value)
    )


@pytest.mark.asyncio
@patch("azure.ai.evaluation.red_team_agent.red_team_agent.RAIClient")
async def test_scan_with_attack_objective_generator(
    mock_rai_client, red_team_agent
):
    mock_rai_client.return_value = MagicMock()
    mock_attack_objective_generator = MagicMock(
        risk_categories=[RiskCategory.Violence], num_objectives=5
    )

    with patch.object(
        red_team_agent, "_start_redteam_mlflow_run",
        return_value=MagicMock()
    ), patch.object(
        red_team_agent, "_get_attack_objectives",
        new_callable=AsyncMock, return_value=["test-prompt"]
    ), patch.object(
        red_team_agent, "_process_attack", new_callable=AsyncMock
    ):
        await red_team_agent.scan(
            target=MagicMock(),
            attack_objective_generator=mock_attack_objective_generator,
            attack_strategies=[AttackStrategy.Baseline],
        )
