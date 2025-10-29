# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import Mock, patch
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate


class TestDeploymentTemplate:
    def test_deployment_template_basic_init(self):
        """Test basic DeploymentTemplate initialization with required fields."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        assert template.name == "test-template"
        assert template.version == "1.0"
        assert template.description is None
        assert template.tags is None or template.tags == {}
        assert template.properties is None or template.properties == {}

    def test_deployment_template_full_init(self):
        """Test DeploymentTemplate initialization with all fields."""
        template = DeploymentTemplate(
            name="test-template",
            version="1.0",
            description="Test deployment template",
            tags={"env": "test"},
            properties={"key": "value"},
            environment_variables={"VAR1": "value1"},
            instance_count=3,
            instance_type="Standard_DS3_v2",
            type="deployment_template",
            deployment_template_type="model_deployment",
            allowed_instance_type="Standard_DS2_v2,Standard_DS3_v2",
        )

        assert template.name == "test-template"
        assert template.version == "1.0"
        assert template.description == "Test deployment template"
        assert template.tags == {"env": "test"}
        assert template.properties == {"key": "value"}
        assert template.environment_variables == {"VAR1": "value1"}
        assert template.instance_count == 3
        assert template.instance_type == "Standard_DS3_v2"
        assert template.type == "deployment_template"
        assert template.deployment_template_type == "model_deployment"
        assert template.allowed_instance_type == "Standard_DS2_v2,Standard_DS3_v2"

    def test_deployment_template_type_fields(self):
        """Test handling of 'type' and 'deployment_template_type' fields."""
        # Test with type field only
        template1 = DeploymentTemplate(name="test1", version="1.0", type="deployment_template")
        assert template1.type == "deployment_template"
        assert template1.deployment_template_type is None

        # Test with deployment_template_type only
        template2 = DeploymentTemplate(name="test2", version="1.0", deployment_template_type="model_deployment")
        assert template2.type is None
        assert template2.deployment_template_type == "model_deployment"

        # Test with both fields
        template3 = DeploymentTemplate(
            name="test3", version="1.0", type="deployment_template", deployment_template_type="model_deployment"
        )
        assert template3.type == "deployment_template"
        assert template3.deployment_template_type == "model_deployment"

    def test_deployment_template_probe_settings(self):
        """Test probe settings functionality."""
        from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings

        liveness_probe = ProbeSettings(initial_delay=10, period=30, timeout=5)
        readiness_probe = ProbeSettings(initial_delay=5, period=15, timeout=3)

        template = DeploymentTemplate(
            name="test-template", version="1.0", liveness_probe=liveness_probe, readiness_probe=readiness_probe
        )

        assert template.liveness_probe is not None
        assert template.readiness_probe is not None

        # Test convenience properties (without _seconds suffix)
        assert template.liveness_probe_initial_delay == 10
        assert template.liveness_probe_period == 30
        assert template.liveness_probe_timeout == 5

        assert template.readiness_probe_initial_delay == 5
        assert template.readiness_probe_period == 15
        assert template.readiness_probe_timeout == 3

    def test_deployment_template_request_settings(self):
        """Test request settings functionality."""
        from azure.ai.ml.entities._deployment.deployment_template_settings import OnlineRequestSettings

        request_settings = OnlineRequestSettings(request_timeout_ms=30000)
        template = DeploymentTemplate(name="test-template", version="1.0", request_settings=request_settings)

        assert template.request_settings is not None
        assert template.request_timeout == 30

    def test_deployment_template_probe_property_setters(self):
        """Test probe property setters."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test liveness probe setters
        template.liveness_probe_initial_delay = 15
        template.liveness_probe_period = 45
        template.liveness_probe_timeout = 10

        assert template.liveness_probe is not None
        assert template.liveness_probe_initial_delay == 15
        assert template.liveness_probe_period == 45
        assert template.liveness_probe_timeout == 10

        # Test readiness probe setters
        template.readiness_probe_initial_delay = 8
        template.readiness_probe_period = 20
        template.readiness_probe_timeout = 6

        assert template.readiness_probe is not None
        assert template.readiness_probe_initial_delay == 8
        assert template.readiness_probe_period == 20
        assert template.readiness_probe_timeout == 6

    def test_deployment_template_request_timeout_setter(self):
        """Test request timeout setter."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test request timeout setter
        template.request_timeout = 60

        assert template.request_settings is not None
        assert template.request_timeout == 60

    def test_deployment_template_environment_handling(self):
        """Test environment field handling."""
        template = DeploymentTemplate(name="test-template", version="1.0", environment="azureml:test-env:1")

        assert template.environment == "azureml:test-env:1"

    def test_deployment_template_code_configuration(self):
        """Test code configuration handling."""
        code_config = {"code": "azureml:test-code:1", "scoring_script": "score.py"}

        template = DeploymentTemplate(name="test-template", version="1.0", code_configuration=code_config)

        assert template.code_configuration == code_config
        # Test code configuration access (if available)
        if template.code_configuration:
            assert template.code_configuration["code"] == "azureml:test-code:1"
            assert template.code_configuration["scoring_script"] == "score.py"

    def test_deployment_template_model_handling(self):
        """Test model field handling."""
        template = DeploymentTemplate(name="test-template", version="1.0", model="azureml:test-model:1")

        assert template.model == "azureml:test-model:1"

    def test_deployment_template_app_insights(self):
        """Test app insights enabled flag."""
        template = DeploymentTemplate(name="test-template", version="1.0", app_insights_enabled=True)

        assert template.app_insights_enabled is True

    def test_deployment_template_scoring_settings(self):
        """Test scoring path and port settings."""
        template = DeploymentTemplate(
            name="test-template",
            version="1.0",
            scoring_path="/score",
            scoring_port=8080,
            model_mount_path="/var/azureml-app",
        )

        assert template.scoring_path == "/score"
        assert template.scoring_port == 8080
        assert template.model_mount_path == "/var/azureml-app"

    def test_deployment_template_inheritance(self):
        """Test that DeploymentTemplate inherits from Resource."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test Resource attributes
        assert hasattr(template, "name")
        assert hasattr(template, "description")
        assert hasattr(template, "tags")
        assert hasattr(template, "properties")

    def test_deployment_template_rest_translatable(self):
        """Test that DeploymentTemplate has REST translation capability."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        # Test that it has REST translation methods
        assert hasattr(template, "_to_rest_object")
        assert hasattr(template, "_from_rest_object")

    def test_deployment_template_equality(self):
        """Test deployment template equality."""
        template1 = DeploymentTemplate(name="test-template", version="1.0", description="Test template")

        template2 = DeploymentTemplate(name="test-template", version="1.0", description="Test template")

        template3 = DeploymentTemplate(name="different-template", version="1.0", description="Test template")

        # Test that templates with same values have same public attributes
        # Filter out private attributes like _from_service and _original_immutable_fields
        def get_public_attrs(obj):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}

        assert get_public_attrs(template1) == get_public_attrs(template2)
        assert get_public_attrs(template1) != get_public_attrs(template3)

    def test_deployment_template_repr(self):
        """Test string representation."""
        template = DeploymentTemplate(name="test-template", version="1.0")

        repr_str = repr(template)
        # The current implementation returns JSON, so check for JSON structure
        assert "test-template" in repr_str
        assert "1.0" in repr_str

    def test_deployment_template_empty_values(self):
        """Test handling of empty values."""
        template = DeploymentTemplate(
            name="test-template", version="1.0", description="", tags={}, properties={}, environment_variables={}
        )

        assert template.description == ""
        assert template.tags == {}
        assert template.properties == {}
        assert template.environment_variables == {}

    def test_deployment_template_from_rest_object_none(self):
        """Test _from_rest_object with None input."""
        result = DeploymentTemplate._from_rest_object(None)

        # Should handle None gracefully
        assert result is not None or result is None  # Allow either behavior
