# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base class for evaluator unit tests to reduce code duplication."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import MagicMock

import pytest


class BaseEvaluatorInputTests(ABC):
    """
    Base class for evaluator input scenario tests.

    This class provides reusable test methods for common input parameter validation patterns
    across different evaluators. Each evaluator test class can inherit from this and configure
    it with evaluator-specific behavior.

    Subclasses must:
    1. Implement get_evaluator_class() to return the evaluator class
    2. Implement get_flow_side_effect() to return the mock flow function
    3. Configure PARAMETER_CONFIG for their specific parameters
    4. Override any test methods that have evaluator-specific behavior
    """

    # ========================================================================
    # CONFIGURATION - Must be set by subclass
    # ========================================================================

    @property
    @abstractmethod
    def PARAMETER_CONFIG(self) -> Dict[str, Dict[str, Any]]:
        """
        Configuration for each parameter's test scenarios.

        Structure:
        {
            "parameter_name": {
                "test_data": {
                    "valid": {...},  # Valid test data
                    "empty": {...},  # Empty/null test data
                    "string": {...},  # String format test data
                    "json_single": {...},  # JSON single item test data
                    "json_object": {...},  # JSON object test data
                    "unexpected": {...},  # Unexpected format test data
                },
                "expected_results": {
                    "not_passed": "not applicable" | "pass" | "fail",
                    "string": "not applicable" | "pass" | "fail" | "exception",
                    "json_object": "not applicable" | "pass" | "fail",
                    "unexpected": "not applicable" | "pass" | "fail",
                    "extracted_success": "pass" | "fail",
                    "not_present": "not applicable" | "pass" | "fail",
                    "not_as_expected": "fail",
                },
                "exception_type": Optional[Exception],  # For string scenario
                "result_assertions": Callable,  # Additional assertions for results
            }
        }
        """
        pass

    @abstractmethod
    def get_evaluator_class(self):
        """Return the evaluator class to test."""
        pass

    @abstractmethod
    def get_flow_side_effect(self) -> Callable:
        """Return the async flow side effect function for mocking."""
        pass

    def get_result_key(self):
        """Get the result key from the evaluator class."""
        return self.get_evaluator_class()._RESULT_KEY

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def create_evaluator(self, mock_model_config):
        """Create an evaluator instance with mocked flow."""
        evaluator = self.get_evaluator_class()(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=self.get_flow_side_effect())
        return evaluator

    def get_default_test_data(
        self, param_name: str, exclude_param: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get default test data for all parameters except the one being tested.

        Args:
            param_name: The parameter currently being tested (will use test-specific data)
            exclude_param: Optional parameter to completely exclude from the call

        Returns:
            Dict of parameter names to test values
        """
        data = {}
        for pname, pconfig in self.PARAMETER_CONFIG.items():
            if pname == exclude_param:
                continue
            if pname == param_name:
                # Use valid data for the parameter being tested
                data[pname] = pconfig["test_data"]["valid"]
            else:
                # Use valid data for all other parameters
                data[pname] = pconfig["test_data"]["valid"]
        return data

    def assert_result_structure(self, result: Dict[str, Any], key: str):
        """Assert basic result structure is present."""
        assert result is not None
        assert key in result

    def assert_not_applicable(
        self, result: Dict[str, Any], key: str, expected_reason: Optional[str] = None
    ):
        """Assert result is 'not applicable' with proper structure."""
        self.assert_result_structure(result, key)
        assert result[key] == "not applicable"
        assert result[f"{key}_result"] == "pass"
        if expected_reason:
            assert expected_reason in result[f"{key}_reason"]

    def assert_pass_result(self, result: Dict[str, Any], key: str):
        """Assert result is a pass."""
        self.assert_result_structure(result, key)
        assert result[f"{key}_result"] == "pass"

    def assert_fail_result(self, result: Dict[str, Any], key: str):
        """Assert result is a fail."""
        self.assert_result_structure(result, key)
        assert result[f"{key}_result"] == "fail"

    # ========================================================================
    # TEMPLATE TEST METHODS - Can be overridden by subclass
    # ========================================================================

    def run_test_not_passed_empty_or_null(
        self,
        mock_model_config,
        param_name: str,
        expected_result: str,
        expected_message: Optional[str] = None,
    ):
        """
        Test parameter: Not Passed, Empty, or Null.

        Args:
            mock_model_config: The mock model configuration fixture
            param_name: Name of the parameter being tested
            expected_result: Expected result ("not applicable", "pass", or "fail")
            expected_message: Optional message to check in reason
        """
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        # Test 1: Parameter not passed
        test_data = self.get_default_test_data(param_name, exclude_param=param_name)
        result = evaluator(**test_data)

        if expected_result == "not applicable":
            self.assert_not_applicable(result, key, expected_message)
        elif expected_result == "pass":
            self.assert_pass_result(result, key)
        else:
            self.assert_fail_result(result, key)

        # Test 2: Parameter is None
        test_data = self.get_default_test_data(param_name)
        test_data[param_name] = None
        result = evaluator(**test_data)

        if expected_result == "not applicable":
            self.assert_not_applicable(result, key, expected_message)
        elif expected_result == "pass":
            self.assert_pass_result(result, key)

        # Test 3: Parameter is empty (if applicable)
        if config["test_data"].get("empty") is not None:
            test_data[param_name] = config["test_data"]["empty"]
            result = evaluator(**test_data)

            if expected_result == "not applicable":
                self.assert_not_applicable(result, key, expected_message)

    def run_test_string_or_json_single_string(
        self,
        mock_model_config,
        param_name: str,
        expected_result: str,
        exception_type: Optional[type] = None,
        expected_message: Optional[str] = None,
    ):
        """Test parameter: String or JSON with single item string."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        # Test 1: Simple string
        if exception_type:
            test_data = self.get_default_test_data(param_name)
            test_data[param_name] = config["test_data"]["string"]
            with pytest.raises(exception_type):
                evaluator(**test_data)
        else:
            test_data = self.get_default_test_data(param_name)
            test_data[param_name] = config["test_data"]["string"]
            result = evaluator(**test_data)

            if expected_result == "not applicable":
                self.assert_not_applicable(result, key, expected_message)
            elif expected_result == "pass":
                self.assert_pass_result(result, key)

        # Test 2: JSON with single string item (if different from simple string)
        if config["test_data"].get("json_single") and not exception_type:
            test_data = self.get_default_test_data(param_name)
            test_data[param_name] = config["test_data"]["json_single"]
            result = evaluator(**test_data)

            if expected_result == "not applicable":
                self.assert_not_applicable(result, key, expected_message)
            elif expected_result == "pass":
                self.assert_pass_result(result, key)

    def run_test_json_object(
        self, mock_model_config, param_name: str, expected_result: str
    ):
        """Test parameter: JSON Object (proper format)."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        test_data = self.get_default_test_data(param_name)
        test_data[param_name] = config["test_data"]["json_object"]
        result = evaluator(**test_data)

        if expected_result == "pass":
            self.assert_pass_result(result, key)
        elif expected_result == "fail":
            self.assert_fail_result(result, key)

        # Run any additional assertions from config
        if "result_assertions" in config:
            config["result_assertions"](result, key)

    def run_test_json_object_unexpected_format(
        self, mock_model_config, param_name: str, expected_result: str
    ):
        """Test parameter: JSON Object not in expected format."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        test_data = self.get_default_test_data(param_name)
        test_data[param_name] = config["test_data"]["unexpected"]
        result = evaluator(**test_data)

        if expected_result == "not applicable":
            self.assert_not_applicable(result, key)
        elif expected_result == "pass":
            self.assert_pass_result(result, key)
        elif expected_result == "fail":
            self.assert_fail_result(result, key)

    def run_test_extracted_parameter_successfully(
        self,
        mock_model_config,
        param_name: str,
        custom_assertions: Optional[Callable] = None,
    ):
        """Test parameter: Extracted parameter successfully."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        # Use the success test data
        test_data = config["test_data"].get("success", config["test_data"]["valid"])
        result = evaluator(**test_data)

        self.assert_pass_result(result, key)

        # Run custom assertions if provided
        if custom_assertions:
            custom_assertions(result, key)
        elif "result_assertions" in config:
            config["result_assertions"](result, key)

    def run_test_parameter_not_present(
        self,
        mock_model_config,
        param_name: str,
        expected_result: str,
        expected_message: Optional[str] = None,
    ):
        """Test parameter: Parameter not present."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        # Use the 'not_present' test data
        test_data = config["test_data"].get(
            "not_present", self.get_default_test_data(param_name)
        )
        if "not_present" in config["test_data"]:
            test_data.update(config["test_data"]["not_present"])

        result = evaluator(**test_data)

        if expected_result == "not applicable":
            self.assert_not_applicable(result, key, expected_message)
        elif expected_result == "pass":
            self.assert_pass_result(result, key)
        elif expected_result == "fail":
            self.assert_fail_result(result, key)

    def run_test_parameter_not_as_expected(
        self,
        mock_model_config,
        param_name: str,
        custom_assertions: Optional[Callable] = None,
    ):
        """Test parameter: Parameter not as expected."""
        evaluator = self.create_evaluator(mock_model_config)
        config = self.PARAMETER_CONFIG[param_name]
        key = self.get_result_key()

        # Use the 'not_as_expected' test data
        test_data = config["test_data"]["not_as_expected"]
        result = evaluator(**test_data)

        self.assert_fail_result(result, key)

        # Run custom assertions if provided
        if custom_assertions:
            custom_assertions(result, key)
        elif "result_assertions" in config:
            config["result_assertions"](result, key)
