#!/usr/bin/env python3
"""
Simple test runner for deployment template tests that bypasses conftest.py import issues.
"""

import sys
import os
import unittest

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sdk_dir = os.path.join(current_dir, "..", "..")
sys.path.insert(0, sdk_dir)
sys.path.insert(0, current_dir)


def run_deployment_template_tests():
    """Run deployment template tests without conftest.py dependencies."""

    print("🧪 Testing DeploymentTemplate Entity...")
    try:
        # Test basic entity functionality
        from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate

        # Test 1: Basic initialization
        template = DeploymentTemplate(name="test", version="1.0")
        assert template.name == "test"
        assert template.version == "1.0"
        print("✅ Basic initialization test passed")

        # Test 2: Full initialization
        template = DeploymentTemplate(
            name="full-test",
            version="2.0",
            description="Test template",
            tags={"env": "test"},
            environment_variables={"VAR": "value"},
            instance_count=3,
            type="deployment_template",
            deployment_template_type="model_deployment",
        )
        assert template.name == "full-test"
        assert template.version == "2.0"
        assert template.description == "Test template"
        assert template.tags == {"env": "test"}
        assert template.environment_variables == {"VAR": "value"}
        assert template.instance_count == 3
        assert template.type == "deployment_template"
        assert template.deployment_template_type == "model_deployment"
        print("✅ Full initialization test passed")

    except Exception as e:
        print(f"❌ Entity test failed: {e}")
        return False

    print("\n🧪 Testing DeploymentTemplateOperations...")
    try:
        from azure.ai.ml.operations._deployment_template_operations import DeploymentTemplateOperations
        from unittest.mock import Mock

        # Test operations initialization
        operation_scope = Mock()
        operation_config = Mock()
        service_client = Mock()

        ops = DeploymentTemplateOperations(
            operation_scope=operation_scope,
            operation_config=operation_config,
            service_client_04_2024_dataplanepreview=service_client,
        )

        assert ops._operation_scope == operation_scope
        assert ops._operation_config == operation_config
        print("✅ Operations initialization test passed")

    except Exception as e:
        print(f"❌ Operations test failed: {e}")
        return False

    print("\n🧪 Testing Load Function...")
    try:
        from azure.ai.ml.entities._load_functions import load_deployment_template

        print("✅ Load function import test passed")

    except Exception as e:
        print(f"❌ Load function test failed: {e}")
        return False

    print("\n🧪 Testing Schema...")
    try:
        from azure.ai.ml._schema._deployment.template.deployment_template import DeploymentTemplateSchema
        import tempfile

        # Test schema with base path
        temp_dir = tempfile.mkdtemp()
        schema = DeploymentTemplateSchema(base_path=temp_dir)

        # Test loading data
        data = {"name": "schema-test", "version": "1.0", "description": "Schema test template"}

        result = schema.load(data)
        assert isinstance(result, DeploymentTemplate)
        assert result.name == "schema-test"
        assert result.version == "1.0"
        print("✅ Schema test passed")

        # Cleanup
        os.rmdir(temp_dir)

    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

    print("\n🎉 All deployment template tests passed!")
    return True


if __name__ == "__main__":
    success = run_deployment_template_tests()
    sys.exit(0 if success else 1)
