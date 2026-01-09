#!/usr/bin/env python
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Standalone test runner for deployment template operations tests.
This bypasses conftest.py import issues for quick validation.
"""

import sys
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add the package to the path
sdk_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(sdk_path))

from azure.ai.ml.operations._deployment_template_operations import DeploymentTemplateOperations
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate
from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings, OnlineRequestSettings
from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig
from azure.core.exceptions import ResourceNotFoundError


class TestDeploymentTemplateEntity(unittest.TestCase):
    """Test DeploymentTemplate entity properties."""

    def test_deployment_template_probe_settings(self):
        """Test probe settings functionality."""
        liveness_probe = ProbeSettings(initial_delay=10, period=30, timeout=5)
        readiness_probe = ProbeSettings(initial_delay=5, period=15, timeout=3)

        template = DeploymentTemplate(
            name="test-template", version="1.0", liveness_probe=liveness_probe, readiness_probe=readiness_probe
        )

        self.assertIsNotNone(template.liveness_probe)
        self.assertIsNotNone(template.readiness_probe)

        # Test convenience properties (without _seconds suffix)
        self.assertEqual(template.liveness_probe_initial_delay, 10)
        self.assertEqual(template.liveness_probe_period, 30)
        self.assertEqual(template.liveness_probe_timeout, 5)

        self.assertEqual(template.readiness_probe_initial_delay, 5)
        self.assertEqual(template.readiness_probe_period, 15)
        self.assertEqual(template.readiness_probe_timeout, 3)
        print("✓ test_deployment_template_probe_settings passed")

    def test_deployment_template_request_settings(self):
        """Test request settings functionality."""
        request_settings = OnlineRequestSettings(request_timeout_ms=30000)
        template = DeploymentTemplate(name="test-template", version="1.0", request_settings=request_settings)

        self.assertIsNotNone(template.request_settings)
        self.assertEqual(template.request_timeout, 30)
        print("✓ test_deployment_template_request_settings passed")

    def test_deployment_template_probe_property_setters(self):
        """Test probe property setters."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test liveness probe setters
        template.liveness_probe_initial_delay = 15
        template.liveness_probe_period = 45
        template.liveness_probe_timeout = 10

        self.assertIsNotNone(template.liveness_probe)
        self.assertEqual(template.liveness_probe_initial_delay, 15)
        self.assertEqual(template.liveness_probe_period, 45)
        self.assertEqual(template.liveness_probe_timeout, 10)

        # Test readiness probe setters
        template.readiness_probe_initial_delay = 8
        template.readiness_probe_period = 20
        template.readiness_probe_timeout = 6

        self.assertIsNotNone(template.readiness_probe)
        self.assertEqual(template.readiness_probe_initial_delay, 8)
        self.assertEqual(template.readiness_probe_period, 20)
        self.assertEqual(template.readiness_probe_timeout, 6)
        print("✓ test_deployment_template_probe_property_setters passed")

    def test_deployment_template_request_timeout_setter(self):
        """Test request timeout setter."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test request timeout setter
        template.request_timeout = 60

        self.assertIsNotNone(template.request_settings)
        self.assertEqual(template.request_timeout, 60)
        print("✓ test_deployment_template_request_timeout_setter passed")


class TestArchiveRestore(unittest.TestCase):
    """Test archive and restore operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_service_client = Mock()
        self.mock_service_client.deployment_templates = Mock()

        mock_operation_scope = Mock(spec=OperationScope)
        mock_operation_config = Mock(spec=OperationConfig)

        self.ops = DeploymentTemplateOperations(
            operation_scope=mock_operation_scope,
            operation_config=mock_operation_config,
            service_client_04_2024_dataplanepreview=self.mock_service_client,
        )

        self.sample_template = DeploymentTemplate(
            name="test-template",
            version="1.0",
            description="Test deployment template",
        )

    def test_archive_deployment_template(self):
        """Test archive operation."""
        # Mock get to return a template
        self.ops.get = Mock(return_value=self.sample_template)

        # Mock create_or_update
        archived_template = DeploymentTemplate(
            name=self.sample_template.name, version=self.sample_template.version, stage="Archived"
        )
        self.ops.create_or_update = Mock(return_value=archived_template)

        result = self.ops.archive("test-template", "1.0")

        # Verify
        self.ops.get.assert_called_once_with(name="test-template", version="1.0")
        self.ops.create_or_update.assert_called_once()
        call_args = self.ops.create_or_update.call_args[0][0]
        self.assertEqual(call_args.stage, "Archived")
        self.assertEqual(result.stage, "Archived")
        print("✓ test_archive_deployment_template passed")

    def test_restore_deployment_template(self):
        """Test restore operation."""
        # Create an archived template
        archived_template = DeploymentTemplate(
            name=self.sample_template.name, version=self.sample_template.version, stage="Archived"
        )

        # Mock get to return the archived template
        self.ops.get = Mock(return_value=archived_template)

        # Mock create_or_update
        restored_template = DeploymentTemplate(
            name=self.sample_template.name, version=self.sample_template.version, stage="Development"
        )
        self.ops.create_or_update = Mock(return_value=restored_template)

        result = self.ops.restore("test-template", "1.0")

        # Verify
        self.ops.get.assert_called_once_with(name="test-template", version="1.0")
        self.ops.create_or_update.assert_called_once()
        call_args = self.ops.create_or_update.call_args[0][0]
        self.assertEqual(call_args.stage, "Development")
        self.assertEqual(result.stage, "Development")
        print("✓ test_restore_deployment_template passed")


class TestConvertDictToDeploymentTemplate(unittest.TestCase):
    """Test _convert_dict_to_deployment_template method."""

    def setUp(self):
        """Set up test fixtures."""
        mock_service_client = Mock()
        mock_operation_scope = Mock(spec=OperationScope)
        mock_operation_config = Mock(spec=OperationConfig)

        self.ops = DeploymentTemplateOperations(
            operation_scope=mock_operation_scope,
            operation_config=mock_operation_config,
            service_client_04_2024_dataplanepreview=mock_service_client,
        )

    def test_basic_conversion(self):
        """Test basic dictionary to DeploymentTemplate conversion."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "description": "Test description",
            "environment": "azureml:test-env:1",
            "tags": {"key": "value"},
        }

        result = self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIsInstance(result, DeploymentTemplate)
        self.assertEqual(result.name, "test-template")
        self.assertEqual(result.version, "1.0")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.environment, "azureml:test-env:1")
        print("✓ test_basic_conversion passed")

    def test_missing_name(self):
        """Test conversion with missing name."""
        dict_data = {
            "version": "1.0",
            "environment": "azureml:test-env:1",
        }

        with self.assertRaises(ValueError) as context:
            self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIn("name is required", str(context.exception))
        print("✓ test_missing_name passed")

    def test_missing_version(self):
        """Test conversion with missing version."""
        dict_data = {
            "name": "test-template",
            "environment": "azureml:test-env:1",
        }

        with self.assertRaises(ValueError) as context:
            self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIn("version is required", str(context.exception))
        print("✓ test_missing_version passed")

    def test_missing_environment(self):
        """Test conversion with missing environment."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
        }

        with self.assertRaises(ValueError) as context:
            self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIn("environment is required", str(context.exception))
        print("✓ test_missing_environment passed")

    def test_camel_case_fields(self):
        """Test conversion with camelCase field names."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environmentId": "azureml:test-env:1",
            "allowedInstanceTypes": ["Standard_DS2_v2", "Standard_DS3_v2"],
            "defaultInstanceType": "Standard_DS2_v2",
            "deploymentTemplateType": "model_deployment",
            "instanceCount": "5",
        }

        result = self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertEqual(result.environment, "azureml:test-env:1")
        self.assertEqual(result.allowed_instance_types, ["Standard_DS2_v2", "Standard_DS3_v2"])
        self.assertEqual(result.default_instance_type, "Standard_DS2_v2")
        self.assertEqual(result.deployment_template_type, "model_deployment")
        self.assertEqual(result.instance_count, 5)
        print("✓ test_camel_case_fields passed")

    def test_request_settings(self):
        """Test conversion with request settings."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "request_settings": {
                "request_timeout_ms": 60000,
                "max_concurrent_requests_per_instance": 10,
            },
        }

        result = self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIsNotNone(result.request_settings)
        self.assertEqual(result.request_settings.request_timeout_ms, 60000)
        self.assertEqual(result.request_settings.max_concurrent_requests_per_instance, 10)
        print("✓ test_request_settings passed")

    def test_probe_settings(self):
        """Test conversion with probe settings."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "liveness_probe": {
                "initial_delay": 30,
                "period": 10,
                "timeout": 5,
                "failure_threshold": 3,
                "path": "/health",
            },
        }

        result = self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertIsNotNone(result.liveness_probe)
        self.assertEqual(result.liveness_probe.initial_delay, 30)
        self.assertEqual(result.liveness_probe.period, 10)
        self.assertEqual(result.liveness_probe.path, "/health")
        print("✓ test_probe_settings passed")

    def test_string_to_int_conversion(self):
        """Test conversion of string values to integers."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "instance_count": "3",
            "scoring_port": "8080",
        }

        result = self.ops._convert_dict_to_deployment_template(dict_data)

        self.assertEqual(result.instance_count, 3)
        self.assertEqual(result.scoring_port, 8080)
        print("✓ test_string_to_int_conversion passed")


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Running Deployment Template Tests")
    print("=" * 70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDeploymentTemplateEntity))
    suite.addTests(loader.loadTestsFromTestCase(TestArchiveRestore))
    suite.addTests(loader.loadTestsFromTestCase(TestConvertDictToDeploymentTemplate))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
