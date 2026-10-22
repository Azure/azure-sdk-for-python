# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Test configuration and runner for deployment template tests.

This module provides configuration and utilities for running comprehensive
unit tests for the deployment template functionality.

To run all deployment template tests:
    pytest tests/deployment_template/unittests/

To run specific test files:
    pytest tests/deployment_template/unittests/test_deployment_template.py
    pytest tests/deployment_template/unittests/test_deployment_template_operations.py
    pytest tests/deployment_template/unittests/test_deployment_template_schema.py
    pytest tests/deployment_template/unittests/test_deployment_template_integration.py

To run with coverage:
    pytest tests/deployment_template/unittests/ --cov=azure.ai.ml.entities._deployment.deployment_template --cov=azure.ai.ml.operations._deployment_template_operations --cov=azure.ai.ml._schema._deployment.template.deployment_template --cov-report=html

Test Coverage Areas:
- DeploymentTemplate entity: All methods, properties, serialization/deserialization
- DeploymentTemplateOperations: CRUD operations, YAML loading, error handling
- DeploymentTemplateSchema: YAML parsing, validation, object creation
- Integration: Complete workflows, field mapping consistency, large data handling
"""

import pytest
import sys
from pathlib import Path


def run_all_tests():
    """Run all deployment template tests with coverage reporting."""
    test_dir = Path(__file__).parent

    # Coverage targets
    coverage_targets = [
        "azure.ai.ml.entities._deployment.deployment_template",
        "azure.ai.ml.operations._deployment_template_operations",
        "azure.ai.ml._schema._deployment.template.deployment_template",
    ]

    # Build pytest command
    pytest_args = [
        str(test_dir),
        "--verbose",
        "--tb=short",
        f"--cov={':'.join(coverage_targets)}",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=95",  # Require 95% coverage
    ]

    # Run tests
    exit_code = pytest.main(pytest_args)
    return exit_code


def run_entity_tests():
    """Run only DeploymentTemplate entity tests."""
    test_file = Path(__file__).parent / "test_deployment_template.py"
    return pytest.main([str(test_file), "--verbose"])


def run_operations_tests():
    """Run only DeploymentTemplateOperations tests."""
    test_file = Path(__file__).parent / "test_deployment_template_operations.py"
    return pytest.main([str(test_file), "--verbose"])


def run_schema_tests():
    """Run only DeploymentTemplateSchema tests."""
    test_file = Path(__file__).parent / "test_deployment_template_schema.py"
    return pytest.main([str(test_file), "--verbose"])


def run_integration_tests():
    """Run only integration tests."""
    test_file = Path(__file__).parent / "test_deployment_template_integration.py"
    return pytest.main([str(test_file), "--verbose"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "entity":
            exit_code = run_entity_tests()
        elif test_type == "operations":
            exit_code = run_operations_tests()
        elif test_type == "schema":
            exit_code = run_schema_tests()
        elif test_type == "integration":
            exit_code = run_integration_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: entity, operations, schema, integration")
            exit_code = 1
    else:
        exit_code = run_all_tests()

    sys.exit(exit_code)
