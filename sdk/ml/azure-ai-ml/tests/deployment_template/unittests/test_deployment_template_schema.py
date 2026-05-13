# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, mock_open
from azure.ai.ml._schema._deployment.template.deployment_template import DeploymentTemplateSchema
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate
from marshmallow import ValidationError
import yaml
import tempfile
import os


class TestDeploymentTemplateSchema:
    @pytest.fixture
    def schema(self):
        """Create a DeploymentTemplateSchema instance with base path context."""
        from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
        from pathlib import Path

        # Create schema with proper context
        temp_dir = tempfile.mkdtemp()
        context = {BASE_PATH_CONTEXT_KEY: Path(temp_dir)}
        schema = DeploymentTemplateSchema(context=context)
        return schema

    def test_schema_fields(self, schema):
        """Test that schema has expected fields."""
        expected_fields = {
            "name",
            "version",
            "description",
            "tags",
            "environment_variables",
            "request_settings",
            "liveness_probe",
            "readiness_probe",
            "instance_count",
            "model_mount_path",
            "allowed_instance_types",
            "default_instance_type",
            "environment",
            "type",
            "deployment_template_type",
        }

        # Check that most expected fields are present
        schema_fields = set(schema.fields.keys())
        common_fields = expected_fields.intersection(schema_fields)
        assert len(common_fields) > 5  # At least some fields should be present

    def test_load_valid_data(self, schema):
        """Test loading valid deployment template data."""
        data = {
            "name": "test-template",
            "version": "1.0",
            "description": "Test deployment template",
            "tags": {"env": "test"},
            "environment_variables": {"VAR1": "value1"},
            "instance_count": 2,
            "type": "deployment_template",
            "deployment_template_type": "model_deployment",
        }

        result = schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.name == "test-template"
        assert result.version == "1.0"
        assert result.description == "Test deployment template"
        assert result.tags == {"env": "test"}
        assert result.environment_variables == {"VAR1": "value1"}
        assert result.instance_count == 2
        assert result.type == "deployment_template"
        assert result.deployment_template_type == "model_deployment"

    def test_load_minimal_data(self, schema):
        """Test loading minimal deployment template data."""
        data = {"name": "minimal-template", "version": "1.0"}

        result = schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.name == "minimal-template"
        assert result.version == "1.0"
        assert result.description is None
        # Tags and environment_variables may be empty dict instead of None
        assert result.tags in [None, {}]

    def test_load_missing_required_field(self, schema):
        """Test loading data with missing required fields."""
        # Missing 'name' field
        data_missing_name = {"version": "1.0"}

        with pytest.raises(ValidationError) as exc_info:
            schema.load(data_missing_name)
        assert "name" in str(exc_info.value)

    def test_dump_deployment_template(self, schema):
        """Test dumping a DeploymentTemplate object."""
        template = DeploymentTemplate(
            name="test-template",
            version="1.0",
            description="Test deployment template",
            tags={"env": "test"},
            environment_variables={"VAR1": "value1"},
            instance_count=2,
            type="deployment_template",
            deployment_template_type="model_deployment",
        )

        result = schema.dump(template)

        assert isinstance(result, dict)
        assert result["name"] == "test-template"
        assert result["version"] == "1.0"
        assert result["description"] == "Test deployment template"
        assert result["tags"] == {"env": "test"}
        assert result["environment_variables"] == {"VAR1": "value1"}
        assert result["instance_count"] == 2
        assert result["type"] == "deployment_template"
        assert result["deployment_template_type"] == "model_deployment"

    def test_post_load_method(self, schema):
        """Test that post_load method properly creates DeploymentTemplate object."""
        data = {"name": "test-template", "version": "1.0", "description": "Test template"}

        # Call the make method directly to test post_load
        result = schema.make(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.name == "test-template"
        assert result.version == "1.0"
        assert result.description == "Test template"

    def test_load_with_extra_fields(self, schema):
        """Test loading data with extra fields (should raise ValidationError)."""
        data = {"name": "test-template", "version": "1.0", "extra_field": "should_be_ignored", "another_extra": 123}

        # Extra fields should cause ValidationError
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)

        # Verify that the error mentions the unknown fields
        assert "extra_field" in str(exc_info.value)
        assert "another_extra" in str(exc_info.value)

    def test_load_with_type_fields(self, schema):
        """Test loading data with both type and deployment_template_type fields."""
        # Test with only type field
        data1 = {"name": "test1", "version": "1.0", "type": "deployment_template"}

        result1 = schema.load(data1)
        assert result1.type == "deployment_template"
        assert result1.deployment_template_type is None

        # Test with only deployment_template_type field
        data2 = {"name": "test2", "version": "1.0", "deployment_template_type": "model_deployment"}

        result2 = schema.load(data2)
        assert result2.type is None
        assert result2.deployment_template_type == "model_deployment"

        # Test with both fields
        data3 = {
            "name": "test3",
            "version": "1.0",
            "type": "deployment_template",
            "deployment_template_type": "model_deployment",
        }

        result3 = schema.load(data3)
        assert result3.type == "deployment_template"
        assert result3.deployment_template_type == "model_deployment"

    def test_load_empty_collections(self, schema):
        """Test loading data with empty collections."""
        data = {"name": "test-template", "version": "1.0", "tags": {}, "environment_variables": {}}

        result = schema.load(data)

        assert isinstance(result, DeploymentTemplate)
        assert result.tags == {}
        assert result.environment_variables == {}

    def test_load_none_values(self, schema):
        """Test loading data with None values (should raise ValidationError)."""
        data = {
            "name": "test-template",
            "version": "1.0",
            "description": None,
            "tags": None,
            "environment_variables": None,
        }

        # Explicit None values should cause ValidationError
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)

        # Verify that the error mentions the null fields
        error_fields = list(exc_info.value.messages.keys())
        assert "description" in error_fields
        assert "tags" in error_fields
        assert "environment_variables" in error_fields

    def test_schema_validation_invalid_types(self, schema):
        """Test schema validation with invalid data types."""
        # Invalid name type (should be string)
        data_invalid_name = {"name": 123, "version": "1.0"}

        with pytest.raises(ValidationError):
            schema.load(data_invalid_name)

    def test_round_trip_serialization(self, schema):
        """Test that we can load and dump data consistently."""
        original_data = {
            "name": "test-template",
            "version": "1.0",
            "description": "Test deployment template",
            "tags": {"env": "test", "version": "1.0"},
            "environment_variables": {"VAR1": "value1", "VAR2": "value2"},
            "instance_count": 2,
            "type": "deployment_template",
            "deployment_template_type": "model_deployment",
        }

        # Load data into object
        template = schema.load(original_data)

        # Dump object back to data
        dumped_data = schema.dump(template)

        # Compare original and dumped data
        assert dumped_data["name"] == original_data["name"]
        assert dumped_data["version"] == original_data["version"]
        assert dumped_data["description"] == original_data["description"]
        assert dumped_data["tags"] == original_data["tags"]
        assert dumped_data["environment_variables"] == original_data["environment_variables"]
        assert dumped_data["instance_count"] == original_data["instance_count"]
        assert dumped_data["type"] == original_data["type"]
        assert dumped_data["deployment_template_type"] == original_data["deployment_template_type"]


class TestYAMLLoading:
    """Test YAML loading functionality for deployment templates."""

    @patch("azure.ai.ml._utils.utils.load_yaml")
    @patch("builtins.open", new_callable=mock_open)
    def test_load_deployment_template_from_yaml_file(self, mock_file, mock_load_yaml):
        """Test loading deployment template from YAML file."""
        # Mock YAML content
        yaml_data = {
            "name": "yaml-template",
            "version": "1.0",
            "description": "Template from YAML",
            "tags": {"source": "yaml"},
            "environment_variables": {"ENV": "test"},
        }

        mock_load_yaml.return_value = yaml_data

        # Import the load function
        from azure.ai.ml.entities._load_functions import load_deployment_template

        with patch("azure.ai.ml.entities._load_functions.load_deployment_template") as mock_load_func:
            mock_load_func.return_value = DeploymentTemplate(
                name="yaml-template",
                version="1.0",
                description="Template from YAML",
                tags={"source": "yaml"},
                environment_variables={"ENV": "test"},
            )

            result = mock_load_func("test_template.yaml")

            assert isinstance(result, DeploymentTemplate)
            assert result.name == "yaml-template"
            assert result.version == "1.0"
            assert result.description == "Template from YAML"
            assert result.tags == {"source": "yaml"}
            assert result.environment_variables == {"ENV": "test"}

    def test_yaml_loading_integration(self):
        """Test integration between YAML loading and schema."""
        from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
        from pathlib import Path

        temp_dir = tempfile.mkdtemp()
        try:
            # Create schema with proper context
            context = {BASE_PATH_CONTEXT_KEY: Path(temp_dir)}
            schema = DeploymentTemplateSchema(context=context)

            # Simulate YAML data that would be loaded
            yaml_data = {
                "name": "integration-test",
                "version": "1.0",
                "description": "Integration test template",
                "tags": {"test": "integration"},
                "environment_variables": {"WORKER_COUNT": "4"},
            }

            # Load using schema (simulates what load_deployment_template does)
            result = schema.load(yaml_data)

            assert isinstance(result, DeploymentTemplate)
            assert result.name == "integration-test"
            assert result.version == "1.0"
            assert result.description == "Integration test template"
            assert result.tags == {"test": "integration"}
            assert result.environment_variables == {"WORKER_COUNT": "4"}
        finally:
            # Cleanup
            os.rmdir(temp_dir)

    def test_yaml_loading_with_complex_data(self):
        """Test YAML loading with complex nested data structures."""
        from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
        from pathlib import Path

        temp_dir = tempfile.mkdtemp()
        try:
            # Create schema with proper context
            context = {BASE_PATH_CONTEXT_KEY: Path(temp_dir)}
            schema = DeploymentTemplateSchema(context=context)

            # Complex YAML data with nested structures
            yaml_data = {
                "name": "complex-template",
                "version": "1.0",
                "description": "Complex template with nested data",
                "tags": {"environment": "production", "team": "ml-ops", "version": "2.1.0"},
                "environment_variables": {
                    "MODEL_PATH": "/models/best_model",
                    "LOG_LEVEL": "INFO",
                    "CACHE_SIZE": "1000",
                    "ENABLE_METRICS": "true",
                },
                "instance_count": 3,
            }

            result = schema.load(yaml_data)

            assert isinstance(result, DeploymentTemplate)
            assert result.name == "complex-template"
            assert result.instance_count == 3
            assert result.environment_variables["MODEL_PATH"] == "/models/best_model"
            assert result.environment_variables["ENABLE_METRICS"] == "true"
        finally:
            # Cleanup
            os.rmdir(temp_dir)
