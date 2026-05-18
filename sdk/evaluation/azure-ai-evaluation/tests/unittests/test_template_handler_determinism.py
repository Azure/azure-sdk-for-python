import pytest
from unittest.mock import MagicMock
from azure.ai.evaluation.simulator._model_tools._template_handler import AdversarialTemplateHandler


class TestAdversarialTemplateHandlerDeterminism:
    """Test that AdversarialTemplateHandler produces deterministic results"""

    def test_template_ordering_consistency(self):
        """Test that templates are returned in consistent order regardless of service response order"""
        
        # Mock the RAI client
        mock_rai_client = MagicMock()
        
        # Mock azure_ai_project
        mock_azure_ai_project = "mock_project"
        
        # Create template handler
        handler = AdversarialTemplateHandler(
            azure_ai_project=mock_azure_ai_project,
            rai_client=mock_rai_client
        )
        
        # Create test parameters data in different orders to simulate
        # different service response orderings
        base_parameters = {
            "template_harmful_qa_1": [
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "harm1"},
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "harm2"}
            ],
            "template_bias_qa_2": [
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "bias1"}
            ],
            "template_toxic_qa_3": [
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "toxic1"},
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "toxic2"},
                {"ch_template_placeholder": "{{ch_template_placeholder}}", "param": "toxic3"}
            ]
        }
        
        # Simulate different service response orders by creating different
        # dictionary orderings (this would happen if service returns data differently)
        
        # Order 1: bias, harmful, toxic
        params_order1 = {
            "template_bias_qa_2": base_parameters["template_bias_qa_2"],
            "template_harmful_qa_1": base_parameters["template_harmful_qa_1"], 
            "template_toxic_qa_3": base_parameters["template_toxic_qa_3"]
        }
        
        # Order 2: toxic, bias, harmful  
        params_order2 = {
            "template_toxic_qa_3": base_parameters["template_toxic_qa_3"],
            "template_bias_qa_2": base_parameters["template_bias_qa_2"],
            "template_harmful_qa_1": base_parameters["template_harmful_qa_1"]
        }
        
        # Order 3: harmful, toxic, bias
        params_order3 = {
            "template_harmful_qa_1": base_parameters["template_harmful_qa_1"],
            "template_toxic_qa_3": base_parameters["template_toxic_qa_3"],
            "template_bias_qa_2": base_parameters["template_bias_qa_2"]
        }
        
        results = []
        
        # Test each ordering
        for order_name, params in [("Order1", params_order1), ("Order2", params_order2), ("Order3", params_order3)]:
            # Set up the categorized parameters to simulate what would happen after service call
            categorized_params = {}
            for key, value in params.items():
                template_key = key  # Simplified for test
                categorized_params[template_key] = {
                    "parameters": value,
                    "category": "qa",  # All are qa category for this test
                    "parameters_key": key
                }
            
            handler.categorized_ch_parameters = categorized_params
            
            # Get templates for "adv_qa" scenario
            templates = handler._get_content_harm_template_collections("adv_qa")
            
            # Extract template names in the order they were returned
            template_names = [t.template_name for t in templates]
            results.append(template_names)
        
        # Verify all orderings produce the same result (due to sorting fix)
        assert results[0] == results[1] == results[2], f"Template ordering is not consistent: {results}"
        
        # Verify the expected sorted order
        expected_order = ["template_bias_qa_2", "template_harmful_qa_1", "template_toxic_qa_3"]
        assert results[0] == expected_order, f"Templates not in expected sorted order. Got: {results[0]}, Expected: {expected_order}"

    def test_template_parameter_consistency_across_orderings(self):
        """Test that template parameters are consistent across different service response orderings"""
        
        # Mock the RAI client
        mock_rai_client = MagicMock()
        mock_azure_ai_project = "mock_project"
        
        handler = AdversarialTemplateHandler(
            azure_ai_project=mock_azure_ai_project,
            rai_client=mock_rai_client
        )
        
        # Create test data with templates having different parameter counts
        # This simulates the scenario that causes the user's randomization issue
        params_data = {
            "template_3param": [{"param": "p1"}, {"param": "p2"}, {"param": "p3"}],
            "template_2param": [{"param": "pA"}, {"param": "pB"}],
            "template_1param": [{"param": "pX"}]
        }
        
        # Test different dictionary orderings that might come from service
        orderings = [
            # Order 1
            {"template_3param": params_data["template_3param"], "template_2param": params_data["template_2param"], "template_1param": params_data["template_1param"]},
            # Order 2  
            {"template_1param": params_data["template_1param"], "template_3param": params_data["template_3param"], "template_2param": params_data["template_2param"]},
            # Order 3
            {"template_2param": params_data["template_2param"], "template_1param": params_data["template_1param"], "template_3param": params_data["template_3param"]}
        ]
        
        results = []
        
        for i, ordering in enumerate(orderings):
            categorized_params = {}
            for key, value in ordering.items():
                categorized_params[key] = {
                    "parameters": value,
                    "category": "qa",
                    "parameters_key": key
                }
            
            handler.categorized_ch_parameters = categorized_params
            templates = handler._get_content_harm_template_collections("adv_qa")
            
            # Extract the template-parameter structure that affects randomization
            template_structure = []
            for template in templates:
                template_structure.append((template.template_name, len(template.template_parameters), [p["param"] for p in template.template_parameters]))
            
            results.append(template_structure)
        
        # All orderings should produce the same template structure due to sorting
        assert all(result == results[0] for result in results), f"Template structures differ across service response orderings: {results}"
        
        # Verify the expected sorted structure
        expected_structure = [
            ("template_1param", 1, ["pX"]),
            ("template_2param", 2, ["pA", "pB"]), 
            ("template_3param", 3, ["p1", "p2", "p3"])
        ]
        assert results[0] == expected_structure, f"Template structure not in expected order. Got: {results[0]}"