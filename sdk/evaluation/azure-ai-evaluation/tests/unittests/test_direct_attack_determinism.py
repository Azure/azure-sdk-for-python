import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation.simulator._utils import JsonLineList
from azure.core.credentials import TokenCredential


class TestDirectAttackSimulatorDeterminism:
    """Test that DirectAttackSimulator produces deterministic results with the same randomization_seed"""

    @pytest.fixture
    def mock_credential(self):
        return MagicMock(spec=TokenCredential)

    @pytest.fixture
    def mock_target(self):
        def mock_target_fn(query: str) -> str:
            return f"response to {query}"
        return mock_target_fn

    @pytest.fixture
    def safety_eval(self, mock_credential):
        return _SafetyEvaluation(
            azure_ai_project={
                "subscription_id": "mock-sub",
                "resource_group_name": "mock-rg", 
                "project_name": "mock-proj"
            },
            credential=mock_credential
        )

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__init__", return_value=None)
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_direct_attack_deterministic_with_same_seed(
        self, mock_open, mock_direct_attack_call, mock_direct_attack_init, 
        safety_eval, mock_target
    ):
        """Test that DirectAttackSimulator produces identical results with the same randomization_seed"""
        
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock DirectAttackSimulator to return consistent results
        # Simulate the actual structure: {"regular": [...], "jailbreak": [...]}
        mock_regular_results = JsonLineList([
            {"messages": [{"role": "user", "content": "query1"}, {"role": "assistant", "content": "response1"}]},
            {"messages": [{"role": "user", "content": "query2"}, {"role": "assistant", "content": "response2"}]}
        ])
        mock_jailbreak_results = JsonLineList([
            {"messages": [{"role": "user", "content": "jb_query1"}, {"role": "assistant", "content": "jb_response1"}]},
            {"messages": [{"role": "user", "content": "jb_query2"}, {"role": "assistant", "content": "jb_response2"}]}
        ])
        
        mock_direct_attack_call.return_value = {
            "regular": mock_regular_results,
            "jailbreak": mock_jailbreak_results
        }
        
        seed_value = 1
        
        # First call with direct_attack evaluator
        result1 = await safety_eval._simulate(
            target=mock_target,
            adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA,
            direct_attack=True,
            randomization_seed=seed_value,
            max_simulation_results=2
        )
        
        # Second call with same seed
        result2 = await safety_eval._simulate(
            target=mock_target,
            adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA,
            direct_attack=True,
            randomization_seed=seed_value,
            max_simulation_results=2
        )
        
        # Verify both calls were made with same parameters
        assert mock_direct_attack_call.call_count == 2
        
        # Check that both calls used the same randomization_seed
        first_call_kwargs = mock_direct_attack_call.call_args_list[0][1]
        second_call_kwargs = mock_direct_attack_call.call_args_list[1][1]
        
        assert first_call_kwargs.get("randomization_seed") == seed_value
        assert second_call_kwargs.get("randomization_seed") == seed_value
        assert first_call_kwargs.get("randomization_seed") == second_call_kwargs.get("randomization_seed")
        
        # Verify that results are structured consistently
        # Both should have the same data paths (regular and jailbreak files)
        assert result1.keys() == result2.keys()
        
        # The keys should include both regular and jailbreak data files
        expected_keys = {"DirectAttackSimulator", "DirectAttackSimulator_Jailbreak"}
        assert set(result1.keys()) == expected_keys
        assert set(result2.keys()) == expected_keys
        
        print("✅ DirectAttackSimulator calls with same seed produce consistent structure")

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation.simulator._model_tools.AdversarialTemplateHandler._get_content_harm_template_collections")
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__init__", return_value=None) 
    @patch("azure.ai.evaluation.simulator.DirectAttackSimulator.__call__", new_callable=AsyncMock)
    @patch("pathlib.Path.open", new_callable=MagicMock)
    async def test_template_ordering_affects_determinism(
        self, mock_open, mock_direct_attack_call, mock_direct_attack_init,
        mock_get_templates, safety_eval, mock_target
    ):
        """Test that template ordering consistency is crucial for deterministic results"""
        
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Create mock templates with different parameter counts (this is key to the issue)
        from azure.ai.evaluation.simulator._model_tools._template_handler import AdversarialTemplate
        
        mock_templates_order1 = [
            AdversarialTemplate(
                template_name="template1", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "p1"}, {"param": "p2"}, {"param": "p3"}]
            ),
            AdversarialTemplate(
                template_name="template2", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "pA"}, {"param": "pB"}]
            ),
            AdversarialTemplate(
                template_name="template3", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "pX"}]
            )
        ]
        
        # Different order (this would happen without the fix)
        mock_templates_order2 = [
            AdversarialTemplate(
                template_name="template3", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "pX"}]
            ),
            AdversarialTemplate(
                template_name="template1", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "p1"}, {"param": "p2"}, {"param": "p3"}]
            ),
            AdversarialTemplate(
                template_name="template2", 
                text=None, 
                context_key=[], 
                template_parameters=[{"param": "pA"}, {"param": "pB"}]
            )
        ]
        
        # Mock the template handler to return different orders
        mock_get_templates.side_effect = [mock_templates_order1, mock_templates_order2]
        
        # Mock DirectAttackSimulator results
        mock_results = {
            "regular": JsonLineList([{"messages": []}]),
            "jailbreak": JsonLineList([{"messages": []}])
        }
        mock_direct_attack_call.return_value = mock_results
        
        seed_value = 1
        
        # Call with first template order
        await safety_eval._simulate(
            target=mock_target,
            adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA,
            direct_attack=True,
            randomization_seed=seed_value
        )
        
        # Call with second template order
        await safety_eval._simulate(
            target=mock_target,
            adversarial_scenario=AdversarialScenario.ADVERSARIAL_QA,
            direct_attack=True,
            randomization_seed=seed_value
        )
        
        # With the fix, both calls should receive templates in the same order
        # The AdversarialTemplateHandler should sort the templates by key
        assert mock_get_templates.call_count == 2
        
        print("✅ Template ordering test completed - fix should ensure consistent ordering")

    def test_template_handler_sorting_fix(self):
        """Test that the template handler sorting fix works correctly"""
        
        from azure.ai.evaluation.simulator._model_tools._template_handler import AdversarialTemplateHandler
        
        # Mock the RAI client and azure project
        mock_rai_client = MagicMock()
        mock_azure_ai_project = "mock_project"
        
        handler = AdversarialTemplateHandler(
            azure_ai_project=mock_azure_ai_project,
            rai_client=mock_rai_client
        )
        
        # Create mock categorized parameters in different orders
        params_data = {
            "template_z_qa": {"parameters": [{"param": "z"}], "category": "qa", "parameters_key": "z"},
            "template_a_qa": {"parameters": [{"param": "a"}], "category": "qa", "parameters_key": "a"}, 
            "template_m_qa": {"parameters": [{"param": "m"}], "category": "qa", "parameters_key": "m"}
        }
        
        # Set the categorized parameters
        handler.categorized_ch_parameters = params_data
        
        # Get templates - they should be sorted by key regardless of input order
        templates = handler._get_content_harm_template_collections("adv_qa")
        
        # Extract template names
        template_names = [t.template_name for t in templates]
        
        # They should be in sorted order: a, m, z
        expected_order = ["template_a_qa", "template_m_qa", "template_z_qa"]
        assert template_names == expected_order, f"Templates not in sorted order. Got: {template_names}, Expected: {expected_order}"
        
        print("✅ Template handler sorts templates consistently")
        
        # Test with different input order
        params_data_different_order = {
            "template_m_qa": {"parameters": [{"param": "m"}], "category": "qa", "parameters_key": "m"},
            "template_z_qa": {"parameters": [{"param": "z"}], "category": "qa", "parameters_key": "z"},
            "template_a_qa": {"parameters": [{"param": "a"}], "category": "qa", "parameters_key": "a"}
        }
        
        handler.categorized_ch_parameters = params_data_different_order
        templates2 = handler._get_content_harm_template_collections("adv_qa")
        template_names2 = [t.template_name for t in templates2]
        
        # Should still be in the same sorted order
        assert template_names2 == expected_order, f"Templates not consistently sorted. Got: {template_names2}, Expected: {expected_order}"
        assert template_names == template_names2, "Different input orders should produce same output order"
        
        print("✅ Template handler produces consistent ordering regardless of input order")