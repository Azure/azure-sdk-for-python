# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation.simulator import DirectAttackSimulator, AdversarialScenario
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.core.credentials import TokenCredential


@pytest.fixture
def mock_credential():
    return MagicMock(spec=TokenCredential)


@pytest.fixture
def mock_azure_ai_project():
    return {
        "subscription_id": "mock-sub",
        "resource_group_name": "mock-rg",
        "project_name": "mock-proj"
    }


@pytest.fixture
def mock_target():
    async def mock_target_fn(query: str) -> str:
        return "mock response"
    return mock_target_fn


@pytest.mark.unittest
class TestDirectAttackSimulator:
    
    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._direct_attack_simulator.DirectAttackSimulator._ensure_service_dependencies")
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    async def test_different_randomization_seeds_fix(
        self, 
        mock_adv_call, 
        mock_adv_init, 
        mock_ensure_deps,
        mock_azure_ai_project, 
        mock_credential, 
        mock_target
    ):
        """Test that DirectAttackSimulator uses different seeds for regular and jailbreak simulations."""
        
        # Setup mock returns
        mock_result = JsonLineList([
            {"messages": [{"content": "test_query", "role": "user"}]}
        ])
        mock_adv_call.return_value = mock_result
        
        # Create DirectAttackSimulator
        simulator = DirectAttackSimulator(
            azure_ai_project=mock_azure_ai_project, 
            credential=mock_credential
        )
        
        # Call with fixed randomization seed
        result = await simulator(
            scenario=AdversarialScenario.ADVERSARIAL_QA,
            target=mock_target,
            max_simulation_results=3,
            randomization_seed=42
        )
        
        # Verify that AdversarialSimulator was called twice (regular and jailbreak)
        assert mock_adv_call.call_count == 2
        
        # Extract the randomization_seed from each call
        call_kwargs_list = [call[1] for call in mock_adv_call.call_args_list]
        regular_seed = call_kwargs_list[0].get("randomization_seed")
        jailbreak_seed = call_kwargs_list[1].get("randomization_seed")
        
        # The fix should ensure different seeds are used
        assert regular_seed != jailbreak_seed, "Regular and jailbreak simulations should use different seeds"
        assert regular_seed == 42, "Regular simulation should use the original seed"
        assert jailbreak_seed == 43, "Jailbreak simulation should use derived seed (original + 1)"
        
        # Verify the structure of the result
        assert "regular" in result
        assert "jailbreak" in result
        assert result["regular"] == mock_result
        assert result["jailbreak"] == mock_result

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._direct_attack_simulator.DirectAttackSimulator._ensure_service_dependencies")
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    async def test_edge_case_max_seed_value(
        self, 
        mock_adv_call, 
        mock_adv_init, 
        mock_ensure_deps,
        mock_azure_ai_project, 
        mock_credential, 
        mock_target
    ):
        """Test edge case when randomization_seed is at maximum value."""
        
        # Setup mock returns
        mock_result = JsonLineList([
            {"messages": [{"content": "test_query", "role": "user"}]}
        ])
        mock_adv_call.return_value = mock_result
        
        # Create DirectAttackSimulator
        simulator = DirectAttackSimulator(
            azure_ai_project=mock_azure_ai_project, 
            credential=mock_credential
        )
        
        # Call with max seed value
        max_seed = 999999
        result = await simulator(
            scenario=AdversarialScenario.ADVERSARIAL_QA,
            target=mock_target,
            max_simulation_results=3,
            randomization_seed=max_seed
        )
        
        # Verify that AdversarialSimulator was called twice
        assert mock_adv_call.call_count == 2
        
        # Extract the randomization_seed from each call
        call_kwargs_list = [call[1] for call in mock_adv_call.call_args_list]
        regular_seed = call_kwargs_list[0].get("randomization_seed")
        jailbreak_seed = call_kwargs_list[1].get("randomization_seed")
        
        # When at max value, jailbreak seed should be original - 1
        assert regular_seed != jailbreak_seed, "Seeds should still be different at max value"
        assert regular_seed == max_seed, "Regular simulation should use the original max seed"
        assert jailbreak_seed == max_seed - 1, "Jailbreak simulation should use max seed - 1"

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._direct_attack_simulator.DirectAttackSimulator._ensure_service_dependencies")
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.AdversarialSimulator.__call__", new_callable=AsyncMock)
    async def test_no_seed_provided_generates_different_seeds(
        self, 
        mock_adv_call, 
        mock_adv_init, 
        mock_ensure_deps,
        mock_azure_ai_project, 
        mock_credential, 
        mock_target
    ):
        """Test that when no seed is provided, different seeds are still generated."""
        
        # Setup mock returns
        mock_result = JsonLineList([
            {"messages": [{"content": "test_query", "role": "user"}]}
        ])
        mock_adv_call.return_value = mock_result
        
        # Create DirectAttackSimulator
        simulator = DirectAttackSimulator(
            azure_ai_project=mock_azure_ai_project, 
            credential=mock_credential
        )
        
        # Call without providing randomization_seed (it will be generated randomly)
        result = await simulator(
            scenario=AdversarialScenario.ADVERSARIAL_QA,
            target=mock_target,
            max_simulation_results=3
        )
        
        # Verify that AdversarialSimulator was called twice
        assert mock_adv_call.call_count == 2
        
        # Extract the randomization_seed from each call
        call_kwargs_list = [call[1] for call in mock_adv_call.call_args_list]
        regular_seed = call_kwargs_list[0].get("randomization_seed")
        jailbreak_seed = call_kwargs_list[1].get("randomization_seed")
        
        # Even with random generation, seeds should be different
        assert regular_seed != jailbreak_seed, "Generated seeds should be different"
        assert jailbreak_seed == regular_seed + 1 or jailbreak_seed == regular_seed - 1, "Jailbreak seed should be derived from regular seed"