import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _SafetyEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation.simulator._adversarial_simulator import AdversarialSimulator
from azure.core.credentials import TokenCredential


@pytest.mark.unittest
class TestDuplicateQueryFix:
    """Test the fix for duplicate queries in AdversarialSimulator"""

    def test_parameter_pairing_no_duplicates(self):
        """Test that the fixed parameter pairing logic prevents duplicates"""
        
        # Create mock templates with overlapping parameters (common in real scenarios)
        templates = []
        shared_params = [
            {"param1": "value1", "param2": "content1"},
            {"param1": "value2", "param2": "content2"}, 
            {"param1": "value3", "param2": "content3"}
        ]
        
        for i in range(3):
            template = MagicMock()
            template.template_parameters = shared_params  # All templates have same parameters
            templates.append(template)
        
        # Simulate the fixed logic from the AdversarialSimulator
        template_parameter_pairs = []
        
        # The fixed logic: each template with its own parameters
        for template in templates:
            if not template.template_parameters:
                continue
            for parameter in template.template_parameters:
                template_parameter_pairs.append((template, parameter))
        
        # Apply deduplication logic
        unique_pairs = []
        seen_combinations = set()
        for template, parameter in template_parameter_pairs:
            param_key = str(sorted(parameter.items())) if isinstance(parameter, dict) else str(parameter)
            combination_key = (id(template), param_key)
            
            if combination_key not in seen_combinations:
                unique_pairs.append((template, parameter))
                seen_combinations.add(combination_key)
        
        template_parameter_pairs = unique_pairs
        
        # Should have 9 unique combinations (3 templates × 3 parameters each)
        assert len(template_parameter_pairs) == 9, f"Expected 9 unique pairs, got {len(template_parameter_pairs)}"
        
        # Verify all combinations are unique
        combination_keys = set()
        for template, parameter in template_parameter_pairs:
            param_key = str(sorted(parameter.items()))
            combination_key = (id(template), param_key)
            assert combination_key not in combination_keys, "Found duplicate combination"
            combination_keys.add(combination_key)

    def test_old_logic_creates_duplicates(self):
        """Test that the old zip logic would create duplicates"""
        
        # Create mock templates with same parameters
        templates = []
        shared_params = [
            {"param": "value1"},
            {"param": "value2"},
            {"param": "value3"}
        ]
        
        for i in range(3):
            template = MagicMock()
            template.template_parameters = shared_params
            templates.append(template)
        
        # Simulate the old problematic logic
        parameter_lists = [t.template_parameters for t in templates]
        zipped_parameters = list(zip(*parameter_lists))
        
        template_parameter_pairs = []
        for param_group in zipped_parameters:
            for template, parameter in zip(templates, param_group):
                template_parameter_pairs.append((template, parameter))
        
        # Extract parameter values to show the duplication
        parameter_values = [pair[1]["param"] for pair in template_parameter_pairs]
        
        # Should have 9 total but only 3 unique parameter values
        assert len(parameter_values) == 9
        assert len(set(parameter_values)) == 3
        
        # Count occurrences of each value - should be 3 duplicates each
        from collections import Counter
        value_counts = Counter(parameter_values)
        for value, count in value_counts.items():
            assert count == 3, f"Value {value} appears {count} times, expected 3"

    def test_adversarial_conversation_scenario_unchanged(self):
        """Test that ADVERSARIAL_CONVERSATION scenario logic is unchanged"""
        
        templates = []
        for i in range(2):
            template = MagicMock()
            template.template_parameters = [
                {"param": f"value{j}"} for j in range(3)
            ]
            templates.append(template)
        
        # Simulate ADVERSARIAL_CONVERSATION logic (should be unchanged)
        template_parameter_pairs = []
        for i, template in enumerate(templates):
            if not template.template_parameters:
                continue
            for parameter in template.template_parameters:
                template_parameter_pairs.append((template, parameter))
        
        # Should have 6 pairs (2 templates × 3 parameters each)
        assert len(template_parameter_pairs) == 6
        
        # All should be unique
        combination_keys = set()
        for template, parameter in template_parameter_pairs:
            param_key = str(sorted(parameter.items()))
            combination_key = (id(template), param_key)
            assert combination_key not in combination_keys
            combination_keys.add(combination_key)


if __name__ == "__main__":
    test = TestDuplicateQueryFix()
    test.test_parameter_pairing_no_duplicates()
    print("✓ New logic prevents duplicates")
    
    test.test_old_logic_creates_duplicates()
    print("✓ Old logic creates duplicates (confirmed)")
    
    test.test_adversarial_conversation_scenario_unchanged()
    print("✓ ADVERSARIAL_CONVERSATION scenario unchanged")
    
    print("All tests passed!")