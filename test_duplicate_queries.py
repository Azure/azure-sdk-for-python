#!/usr/bin/env python3
"""
Test script to reproduce the duplicate queries issue in DirectAttackSimulator.
"""
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation.simulator import DirectAttackSimulator, AdversarialScenario
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.core.credentials import TokenCredential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def mock_target(query: str) -> str:
    """Mock target function for testing."""
    return f"Response to: {query}"

async def test_duplicate_queries():
    """Test to reproduce the duplicate queries issue."""
    
    # Mock credential and project
    mock_credential = MagicMock(spec=TokenCredential)
    mock_project = {
        "subscription_id": "mock-sub",
        "resource_group_name": "mock-rg", 
        "project_name": "mock-proj"
    }
    
    # Create mock template data that would cause duplicates
    mock_template_params = [
        {"conversation_starter": f"Test query {i}"} for i in range(10)
    ]
    
    mock_template = MagicMock()
    mock_template.template_parameters = mock_template_params
    
    # Mock jailbreak dataset 
    mock_jailbreak_data = ["jailbreak1", "jailbreak2", "jailbreak3"]
    
    with patch('azure.ai.evaluation.simulator._adversarial_simulator.AdversarialSimulator.__init__', return_value=None), \
         patch('azure.ai.evaluation.simulator._adversarial_simulator.AdversarialSimulator.__call__', new_callable=AsyncMock) as mock_sim_call, \
         patch('azure.ai.evaluation.simulator._direct_attack_simulator.DirectAttackSimulator._ensure_service_dependencies'), \
         patch('azure.ai.evaluation.simulator._direct_attack_simulator.DirectAttackSimulator.adversarial_template_handler'):
        
        # Setup mock responses
        mock_regular_results = JsonLineList([
            {"messages": [{"content": f"regular_query_{i}", "role": "user"}]} for i in range(5)
        ])
        mock_jailbreak_results = JsonLineList([
            {"messages": [{"content": f"jailbreak_query_{i}", "role": "user"}]} for i in range(5)
        ])
        
        # Configure mock to return different results for each call
        mock_sim_call.side_effect = [mock_regular_results, mock_jailbreak_results]
        
        # Create DirectAttackSimulator
        simulator = DirectAttackSimulator(azure_ai_project=mock_project, credential=mock_credential)
        
        # Run simulation with a fixed seed
        result = await simulator(
            scenario=AdversarialScenario.ADVERSARIAL_QA,
            target=mock_target,
            max_simulation_results=5,
            randomization_seed=42  # Fixed seed that should cause duplicates
        )
        
        logger.info("Simulation completed successfully")
        logger.info(f"Regular results: {len(result['regular'])}")
        logger.info(f"Jailbreak results: {len(result['jailbreak'])}")
        
        # Check if both simulators were called with the same seed
        calls = mock_sim_call.call_args_list
        if len(calls) >= 2:
            regular_call_kwargs = calls[0][1] if calls[0][1] else {}
            jailbreak_call_kwargs = calls[1][1] if calls[1][1] else {}
            
            regular_seed = regular_call_kwargs.get('randomization_seed')
            jailbreak_seed = jailbreak_call_kwargs.get('randomization_seed')
            
            logger.info(f"Regular simulation seed: {regular_seed}")
            logger.info(f"Jailbreak simulation seed: {jailbreak_seed}")
            
            if regular_seed == jailbreak_seed:
                logger.error("ISSUE CONFIRMED: Both simulations use the same randomization seed!")
                logger.error("This will cause identical template shuffling and duplicate queries.")
                return True
            else:
                logger.info("Seeds are different - issue may have been fixed")
                return False
        else:
            logger.warning("Expected 2 simulator calls but got different number")
            return False

if __name__ == "__main__":
    asyncio.run(test_duplicate_queries())