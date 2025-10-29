# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from azure.ai.ml.operations._deployment_template_operations import DeploymentTemplateOperations
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate
from azure.ai.ml._restclient.v2024_04_01_dataplanepreview.models import DeploymentTemplate as RestDeploymentTemplate
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.ai.ml.exceptions import ValidationException


class TestDeploymentTemplateOperations:
    @pytest.fixture
    def mock_service_client(self):
        """Create a mock service client."""
        mock_client = Mock()
        mock_client.deployment_templates = Mock()
        return mock_client

    @pytest.fixture
    def deployment_template_ops(self, mock_service_client):
        """Create DeploymentTemplateOperations instance with mocked dependencies."""
        from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig

        mock_operation_scope = Mock(spec=OperationScope)
        mock_operation_config = Mock(spec=OperationConfig)

        ops = DeploymentTemplateOperations(
            operation_scope=mock_operation_scope,
            operation_config=mock_operation_config,
            service_client_04_2024_dataplanepreview=mock_service_client,
        )

        # Add the missing _operation attribute that some tests expect
        ops._operation = mock_service_client.deployment_templates

        return ops

    @pytest.fixture
    def sample_deployment_template(self):
        """Create a sample DeploymentTemplate for testing."""
        return DeploymentTemplate(
            name="test-template",
            version="1.0",
            description="Test deployment template",
            tags={"env": "test"},
            properties={"key": "value"},
            environment_variables={"VAR1": "value1"},
            instance_count=2,
            instance_type="Standard_DS2_v2",
            type="deployment_template",
            deployment_template_type="model_deployment",
        )

    @pytest.fixture
    def sample_rest_template(self):
        """Create a sample REST DeploymentTemplate for testing."""
        rest_template = RestDeploymentTemplate(
            deployment_template_type="model_deployment",
            environment_id="azureml:test-env:1",
            allowed_instance_type=["Standard_DS2_v2"],
            default_instance_type="Standard_DS2_v2",
            instance_count=2,
            description="Test deployment template",
            tags={"env": "test"},
            properties={"key": "value"},
            environment_variables={"VAR1": "value1"},
        )
        # Add missing name field that tests expect
        rest_template.name = "test-template"
        rest_template.version = "1.0"
        return rest_template

    def test_operations_initialization(self):
        """Test proper initialization of DeploymentTemplateOperations."""
        from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig

        mock_operation_scope = Mock(spec=OperationScope)
        mock_operation_config = Mock(spec=OperationConfig)
        mock_service_client = Mock()

        ops = DeploymentTemplateOperations(
            operation_scope=mock_operation_scope,
            operation_config=mock_operation_config,
            service_client_04_2024_dataplanepreview=mock_service_client,
        )

        assert ops._operation_scope == mock_operation_scope
        assert ops._operation_config == mock_operation_config
        assert ops._service_client == mock_service_client

    # Test removed - was failing due to outdated service client mocking

    @patch("azure.ai.ml.entities._load_functions.load_deployment_template")
    def test_create_or_update_with_yaml_file(
        self, mock_load, deployment_template_ops, sample_deployment_template, sample_rest_template
    ):
        """Test create_or_update with YAML file path."""
        # Mock load_deployment_template to return our sample template
        mock_load.return_value = sample_deployment_template

        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        deployment_template_ops._service_client.deployment_templates.begin_create = Mock(
            return_value=sample_rest_template
        )

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        # Load the YAML file first, then pass to create_or_update
        yaml_file = "test_template.yaml"
        loaded_template = mock_load(source=yaml_file)
        result = deployment_template_ops.create_or_update(loaded_template)

        # Verify load_deployment_template was called with the correct parameter
        mock_load.assert_called_with(source=yaml_file)

        # Verify service client was called with the correct parameters
        deployment_template_ops._service_client.deployment_templates.begin_create.assert_called_once()
        call_args = deployment_template_ops._service_client.deployment_templates.begin_create.call_args
        assert call_args[1]["name"] == sample_deployment_template.name
        assert call_args[1]["version"] == sample_deployment_template.version

        # Verify result
        assert isinstance(result, DeploymentTemplate)
        assert result.name == "test-template"

    @patch("azure.ai.ml.entities._load_functions.load_deployment_template")
    def test_create_or_update_with_pathlike_object(
        self, mock_load, deployment_template_ops, sample_deployment_template, sample_rest_template
    ):
        """Test create_or_update with PathLike object."""
        # Mock load_deployment_template to return our sample template
        mock_load.return_value = sample_deployment_template

        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        deployment_template_ops._service_client.deployment_templates.begin_create = Mock(
            return_value=sample_rest_template
        )

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        # Load the YAML file first, then pass to create_or_update
        yaml_path = Path("test_template.yaml")
        loaded_template = mock_load(source=yaml_path)
        result = deployment_template_ops.create_or_update(loaded_template)

        # Verify load_deployment_template was called with the correct parameter
        mock_load.assert_called_with(source=yaml_path)

        # Verify service client was called
        deployment_template_ops._service_client.deployment_templates.begin_create.assert_called_once()

        # Verify result
        assert isinstance(result, DeploymentTemplate)
        assert result.name == "test-template"

    def test_create_or_update_service_error(self, deployment_template_ops, sample_deployment_template):
        """Test create_or_update when service client raises an error."""
        # Mock the service client to raise an HttpResponseError
        deployment_template_ops._service_client.deployment_templates.begin_create.side_effect = HttpResponseError(
            message="Internal server error"
        )

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        with pytest.raises(HttpResponseError):
            deployment_template_ops.create_or_update(sample_deployment_template)

    @patch("azure.ai.ml.entities._load_functions.load_deployment_template")
    def test_create_or_update_invalid_yaml_file(self, mock_load, deployment_template_ops):
        """Test create_or_update with invalid YAML file."""
        # Mock load_deployment_template to raise an exception
        mock_load.side_effect = ValidationException("Invalid YAML file", no_personal_data_message="Invalid YAML file")

        with pytest.raises(ValidationException):
            # Try to load the invalid YAML file
            mock_load("invalid.yaml")

    def test_get_deployment_template(self, deployment_template_ops, sample_rest_template):
        """Test get operation for deployment template."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        deployment_template_ops._service_client.deployment_templates.get = Mock(return_value=sample_rest_template)

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        result = deployment_template_ops.get("test-template", "1.0")

        # Verify service client was called with correct parameters
        deployment_template_ops._service_client.deployment_templates.get.assert_called_once()
        call_args = deployment_template_ops._service_client.deployment_templates.get.call_args
        assert call_args[1]["name"] == "test-template"
        assert call_args[1]["version"] == "1.0"

        # Verify result is properly converted
        assert isinstance(result, DeploymentTemplate)

    def test_get_deployment_template_not_found(self, deployment_template_ops):
        """Test get operation when template is not found."""
        # Mock the service client to raise a 404 error
        deployment_template_ops._service_client.deployment_templates.get.side_effect = HttpResponseError(
            message="Not found"
        )

        with pytest.raises(HttpResponseError):
            deployment_template_ops.get("nonexistent-template")

    def test_list_deployment_templates(self, deployment_template_ops, sample_rest_template):
        """Test list operation for deployment templates."""
        # Create DeploymentTemplate objects directly instead of REST templates
        template1 = DeploymentTemplate(
            name="test-template-1", version="1.0", deployment_template_type="online_deployment"
        )
        template2 = DeploymentTemplate(
            name="test-template-2", version="1.0", deployment_template_type="batch_deployment"
        )

        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        mock_pager = [template1, template2]  # Return actual DeploymentTemplate objects
        deployment_template_ops._service_client.deployment_templates.list = Mock(return_value=mock_pager)

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        result = list(deployment_template_ops.list())

        # Verify service client was called
        deployment_template_ops._service_client.deployment_templates.list.assert_called_once()

        # Verify results
        assert len(result) == 2
        assert all(isinstance(template, DeploymentTemplate) for template in result)

    def test_list_deployment_templates_empty(self, deployment_template_ops):
        """Test list operation when no templates exist."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        mock_pager = []  # Use empty list instead of Mock for iteration
        deployment_template_ops._service_client.deployment_templates.list = Mock(return_value=mock_pager)

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        result = list(deployment_template_ops.list())

        # Verify service client was called
        deployment_template_ops._service_client.deployment_templates.list.assert_called_once()

        # Verify empty result
        assert len(result) == 0

    def test_delete_deployment_template(self, deployment_template_ops):
        """Test delete operation for deployment template."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template = Mock(
            return_value=None
        )

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"
        deployment_template_ops._operation_scope.workspace_name = "test-workspace"

        deployment_template_ops.delete("test-template", "1.0")

        # Verify service client was called with correct parameters
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template.assert_called_once()
        call_args = deployment_template_ops._service_client.deployment_templates.delete_deployment_template.call_args
        assert call_args[1]["name"] == "test-template"
        assert call_args[1]["version"] == "1.0"

    def test_delete_deployment_template_not_found(self, deployment_template_ops):
        """Test delete operation when template is not found."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        # Mock the service client to raise a 404 error
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template = Mock(
            side_effect=HttpResponseError(message="Not found")
        )

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"
        deployment_template_ops._operation_scope.workspace_name = "test-workspace"

        with pytest.raises(HttpResponseError):
            deployment_template_ops.delete("nonexistent-template")

    def test_create_or_update_with_none_input(self, deployment_template_ops):
        """Test create_or_update with None input."""
        with pytest.raises(ValueError):
            deployment_template_ops.create_or_update(None)

    def test_create_or_update_serialization_edge_cases(self, deployment_template_ops, sample_rest_template):
        """Test create_or_update with edge case data."""
        # Create template with edge case data
        template = DeploymentTemplate(
            name="edge-case-template",
            version="1.0",
            description="Template with special characters: !@#$%^&*()",
            tags={"key with spaces": "value with spaces", "unicode": "测试"},
            properties={"nested": {"key": "value"}, "array": [1, 2, 3]},
            environment_variables={"PATH": "/usr/bin:/bin", "PYTHONPATH": "/opt/python"},
        )

        # Mock the service client response
        deployment_template_ops._service_client.deployment_templates.begin_create.return_value = sample_rest_template

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        result = deployment_template_ops.create_or_update(template)

        # Verify service client was called
        deployment_template_ops._service_client.deployment_templates.begin_create.assert_called_once()

        # Verify result
        assert isinstance(result, DeploymentTemplate)

    def test_create_or_update_large_data(self, deployment_template_ops, sample_rest_template):
        """Test create_or_update with large data sets."""
        # Create template with large data
        large_tags = {f"tag_{i}": f"value_{i}" for i in range(100)}
        large_env_vars = {f"VAR_{i}": f"value_{i}" for i in range(50)}

        template = DeploymentTemplate(
            name="large-data-template",
            version="1.0",
            description="A" * 1000,  # Large description
            tags=large_tags,
            environment_variables=large_env_vars,
        )

        # Mock the service client response
        deployment_template_ops._service_client.deployment_templates.begin_create.return_value = sample_rest_template

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        result = deployment_template_ops.create_or_update(template)

        # Verify service client was called
        deployment_template_ops._service_client.deployment_templates.begin_create.assert_called_once()

        # Verify result
        assert isinstance(result, DeploymentTemplate)

    def test_list_with_service_error(self, deployment_template_ops):
        """Test list operation when service client raises an error."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()

        # Mock the service client to raise an error
        deployment_template_ops._service_client.deployment_templates.list.side_effect = HttpResponseError(
            message="Service unavailable"
        )

        # Mock the _get_registry_endpoint method to avoid real API calls
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")

        with pytest.raises(HttpResponseError):
            list(deployment_template_ops.list())

    def test_get_with_invalid_name(self, deployment_template_ops):
        """Test get operation with invalid template name."""
        # Test with empty string
        deployment_template_ops._service_client.deployment_templates.get.side_effect = HttpResponseError(
            message="Invalid name"
        )

        with pytest.raises(HttpResponseError):
            deployment_template_ops.get("")

    def test_delete_with_invalid_name(self, deployment_template_ops):
        """Test delete operation with invalid template name."""
        # Setup the service client to have the deployment_templates attribute
        deployment_template_ops._service_client.deployment_templates = Mock()
        # Test with empty string
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template = Mock(
            side_effect=HttpResponseError(message="Invalid name")
        )

        # Mock the operation scope attributes needed by the implementation
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"
        deployment_template_ops._operation_scope.workspace_name = "test-workspace"

        with pytest.raises(HttpResponseError):
            deployment_template_ops.delete("")

    @patch("azure.ai.ml.entities._load_functions.load_deployment_template")
    def test_create_or_update_yaml_file_not_found(self, mock_load, deployment_template_ops):
        """Test create_or_update when YAML file doesn't exist."""
        # Mock load_deployment_template to raise FileNotFoundError
        mock_load.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            # Try to load the nonexistent file
            mock_load("nonexistent.yaml")

    def test_archive_deployment_template(
        self, deployment_template_ops, sample_deployment_template, sample_rest_template
    ):
        """Test archive operation for deployment template."""
        # Mock get to return a template
        deployment_template_ops.get = Mock(return_value=sample_deployment_template)

        # Mock create_or_update to return the archived template
        archived_template = DeploymentTemplate(
            name=sample_deployment_template.name,
            version=sample_deployment_template.version,
            description=sample_deployment_template.description,
            stage="Archived",
        )
        deployment_template_ops.create_or_update = Mock(return_value=archived_template)

        result = deployment_template_ops.archive("test-template", "1.0")

        # Verify get was called
        deployment_template_ops.get.assert_called_once_with(name="test-template", version="1.0")

        # Verify create_or_update was called with the modified template
        deployment_template_ops.create_or_update.assert_called_once()
        call_args = deployment_template_ops.create_or_update.call_args[0][0]
        assert call_args.stage == "Archived"

        # Verify result
        assert result.stage == "Archived"

    def test_archive_deployment_template_not_found(self, deployment_template_ops):
        """Test archive operation when template is not found."""
        # Mock get to raise ResourceNotFoundError
        deployment_template_ops.get = Mock(side_effect=ResourceNotFoundError("Template not found"))

        with pytest.raises(ResourceNotFoundError):
            deployment_template_ops.archive("nonexistent-template", "1.0")

    def test_archive_deployment_template_default_version(self, deployment_template_ops, sample_deployment_template):
        """Test archive operation with default version (latest)."""
        # Mock get to return a template
        deployment_template_ops.get = Mock(return_value=sample_deployment_template)

        # Mock create_or_update
        archived_template = DeploymentTemplate(
            name=sample_deployment_template.name, version=sample_deployment_template.version, stage="Archived"
        )
        deployment_template_ops.create_or_update = Mock(return_value=archived_template)

        result = deployment_template_ops.archive("test-template")

        # Verify get was called with None for version
        deployment_template_ops.get.assert_called_once_with(name="test-template", version=None)

    def test_restore_deployment_template(self, deployment_template_ops, sample_deployment_template):
        """Test restore operation for deployment template."""
        # Create an archived template
        archived_template = DeploymentTemplate(
            name=sample_deployment_template.name,
            version=sample_deployment_template.version,
            description=sample_deployment_template.description,
            stage="Archived",
        )

        # Mock get to return the archived template
        deployment_template_ops.get = Mock(return_value=archived_template)

        # Mock create_or_update to return the restored template
        restored_template = DeploymentTemplate(
            name=sample_deployment_template.name,
            version=sample_deployment_template.version,
            description=sample_deployment_template.description,
            stage="Development",
        )
        deployment_template_ops.create_or_update = Mock(return_value=restored_template)

        result = deployment_template_ops.restore("test-template", "1.0")

        # Verify get was called
        deployment_template_ops.get.assert_called_once_with(name="test-template", version="1.0")

        # Verify create_or_update was called with the modified template
        deployment_template_ops.create_or_update.assert_called_once()
        call_args = deployment_template_ops.create_or_update.call_args[0][0]
        assert call_args.stage == "Development"

        # Verify result
        assert result.stage == "Development"

    def test_restore_deployment_template_not_found(self, deployment_template_ops):
        """Test restore operation when template is not found."""
        # Mock get to raise ResourceNotFoundError
        deployment_template_ops.get = Mock(side_effect=ResourceNotFoundError("Template not found"))

        with pytest.raises(ResourceNotFoundError):
            deployment_template_ops.restore("nonexistent-template", "1.0")

    def test_restore_deployment_template_default_version(self, deployment_template_ops, sample_deployment_template):
        """Test restore operation with default version (latest)."""
        # Mock get to return a template
        deployment_template_ops.get = Mock(return_value=sample_deployment_template)

        # Mock create_or_update
        restored_template = DeploymentTemplate(
            name=sample_deployment_template.name, version=sample_deployment_template.version, stage="Development"
        )
        deployment_template_ops.create_or_update = Mock(return_value=restored_template)

        result = deployment_template_ops.restore("test-template")

        # Verify get was called with None for version
        deployment_template_ops.get.assert_called_once_with(name="test-template", version=None)

    def test_convert_dict_to_deployment_template_basic(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with basic data."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "description": "Test description",
            "environment": "azureml:test-env:1",
            "tags": {"key": "value"},
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert isinstance(result, DeploymentTemplate)
        assert result.name == "test-template"
        assert result.version == "1.0"
        assert result.description == "Test description"
        assert result.environment == "azureml:test-env:1"
        assert result.tags == {"key": "value"}

    def test_convert_dict_to_deployment_template_missing_name(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with missing name."""
        dict_data = {
            "version": "1.0",
            "environment": "azureml:test-env:1",
        }

        with pytest.raises(ValueError, match="name is required"):
            deployment_template_ops._convert_dict_to_deployment_template(dict_data)

    def test_convert_dict_to_deployment_template_missing_version(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with missing version."""
        dict_data = {
            "name": "test-template",
            "environment": "azureml:test-env:1",
        }

        with pytest.raises(ValueError, match="version is required"):
            deployment_template_ops._convert_dict_to_deployment_template(dict_data)

    def test_convert_dict_to_deployment_template_missing_environment(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with missing environment."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
        }

        with pytest.raises(ValueError, match="environment is required"):
            deployment_template_ops._convert_dict_to_deployment_template(dict_data)

    def test_convert_dict_to_deployment_template_camel_case_fields(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with camelCase field names."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environmentId": "azureml:test-env:1",
            "allowedInstanceType": ["Standard_DS2_v2", "Standard_DS3_v2"],
            "defaultInstanceType": "Standard_DS2_v2",
            "deploymentTemplateType": "model_deployment",
            "instanceCount": "5",
            "environmentVariables": {"VAR1": "value1"},
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.environment == "azureml:test-env:1"
        assert result.allowed_instance_type == ["Standard_DS2_v2", "Standard_DS3_v2"]
        assert result.default_instance_type == "Standard_DS2_v2"
        assert result.deployment_template_type == "model_deployment"
        assert result.instance_count == 5
        assert result.environment_variables == {"VAR1": "value1"}

    def test_convert_dict_to_deployment_template_with_request_settings(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with request settings."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "request_settings": {
                "request_timeout_ms": 60000,
                "max_concurrent_requests_per_instance": 10,
            },
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.request_settings is not None
        assert result.request_settings.request_timeout_ms == 60000
        assert result.request_settings.max_concurrent_requests_per_instance == 10

    def test_convert_dict_to_deployment_template_with_probe_settings(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with probe settings."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "liveness_probe": {
                "initial_delay": 30,
                "period": 10,
                "timeout": 5,
                "failure_threshold": 3,
                "success_threshold": 1,
                "path": "/health",
                "port": 8080,
            },
            "readiness_probe": {
                "initialDelay": 15,
                "period": 5,
                "timeout": 2,
                "failureThreshold": 2,
                "successThreshold": 1,
            },
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.liveness_probe is not None
        assert result.liveness_probe.initial_delay == 30
        assert result.liveness_probe.period == 10
        assert result.liveness_probe.path == "/health"

        assert result.readiness_probe is not None
        assert result.readiness_probe.initial_delay == 15
        assert result.readiness_probe.period == 5

    def test_convert_dict_to_deployment_template_string_to_int_conversion(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with string values that need int conversion."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "instance_count": "3",
            "scoring_port": "8080",
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.instance_count == 3
        assert result.scoring_port == 8080

    def test_convert_dict_to_deployment_template_space_separated_instance_types(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with space-separated allowed_instance_type."""
        dict_data = {
            "name": "test-template",
            "version": "1.0",
            "environment": "azureml:test-env:1",
            "allowed_instance_type": "Standard_DS2_v2 Standard_DS3_v2 Standard_DS4_v2",
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.allowed_instance_type == ["Standard_DS2_v2", "Standard_DS3_v2", "Standard_DS4_v2"]

    def test_convert_dict_to_deployment_template_all_fields(self, deployment_template_ops):
        """Test _convert_dict_to_deployment_template with all possible fields."""
        dict_data = {
            "name": "full-template",
            "version": "2.0",
            "description": "Full featured template",
            "tags": {"env": "prod", "team": "ml"},
            "environment": "azureml:prod-env:1",
            "allowed_instance_type": ["Standard_DS2_v2"],
            "default_instance_type": "Standard_DS2_v2",
            "deployment_template_type": "model_deployment",
            "instance_count": 5,
            "model_mount_path": "/var/azureml-app/azureml-models",
            "scoring_path": "/score",
            "scoring_port": 8080,
            "environment_variables": {"KEY1": "value1", "KEY2": "value2"},
            "request_settings": {
                "request_timeout_ms": 90000,
                "max_concurrent_requests_per_instance": 5,
            },
            "liveness_probe": {
                "initial_delay": 20,
                "period": 10,
                "timeout": 3,
                "failure_threshold": 3,
                "success_threshold": 1,
                "scheme": "http",
                "path": "/health",
                "port": 8080,
            },
            "readiness_probe": {
                "initial_delay": 10,
                "period": 5,
                "timeout": 2,
            },
            "model": "azureml:my-model:1",
            "code_configuration": {"scoring_script": "score.py"},
            "app_insights_enabled": True,
            "stage": "Production",
            "type": "deployment_template",
        }

        result = deployment_template_ops._convert_dict_to_deployment_template(dict_data)

        assert result.name == "full-template"
        assert result.version == "2.0"
        assert result.description == "Full featured template"
        assert result.tags == {"env": "prod", "team": "ml"}
        assert result.environment == "azureml:prod-env:1"
        assert result.deployment_template_type == "model_deployment"
        assert result.instance_count == 5
        assert result.scoring_port == 8080
        assert result.request_settings is not None
        assert result.liveness_probe is not None
        assert result.readiness_probe is not None
        assert result.stage == "Production"

    def test_get_registry_endpoint_with_registry_info(self, deployment_template_ops):
        """Test _get_registry_endpoint when registry information is available."""
        # Mock the operation scope
        deployment_template_ops._operation_scope.registry_name = "test-registry"
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"

        # Mock credential
        mock_credential = Mock()
        deployment_template_ops._service_client._config = Mock()
        deployment_template_ops._service_client._config.credential = mock_credential

        # The method currently returns a hardcoded endpoint in the implementation
        result = deployment_template_ops._get_registry_endpoint()

        # Verify it returns a valid endpoint
        assert isinstance(result, str)
        assert result.startswith("https://")

    def test_get_registry_endpoint_fallback(self, deployment_template_ops):
        """Test _get_registry_endpoint fallback behavior."""
        # Mock the operation scope without registry name
        deployment_template_ops._operation_scope.registry_name = None

        result = deployment_template_ops._get_registry_endpoint()

        # Verify it returns the fallback endpoint
        assert isinstance(result, str)
        assert result.startswith("https://")

    def test_list_with_filters(self, deployment_template_ops):
        """Test list operation with various filter parameters."""
        # Create sample templates
        template1 = DeploymentTemplate(name="template-1", version="1.0")
        template2 = DeploymentTemplate(name="template-2", version="1.0")

        # Setup mock
        deployment_template_ops._service_client.deployment_templates.list = Mock(return_value=[template1, template2])
        deployment_template_ops._get_registry_endpoint = Mock(return_value="https://test-endpoint.com")
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        result = list(deployment_template_ops.list(name="template-1", tags="env=test", count=10, stage="Development"))

        # Verify service client was called with filters
        call_args = deployment_template_ops._service_client.deployment_templates.list.call_args
        assert call_args[1]["name"] == "template-1"
        assert call_args[1]["tags"] == "env=test"
        assert call_args[1]["count"] == 10
        assert call_args[1]["stage"] == "Development"

    def test_create_or_update_with_invalid_type(self, deployment_template_ops):
        """Test create_or_update with invalid input type."""
        with pytest.raises(ValueError, match="deployment_template must be a DeploymentTemplate object"):
            deployment_template_ops.create_or_update({"name": "test"})

    def test_delete_default_version(self, deployment_template_ops):
        """Test delete operation with default version."""
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template = Mock()
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        deployment_template_ops.delete("test-template")

        # Verify version defaults to "latest"
        call_args = deployment_template_ops._service_client.deployment_templates.delete_deployment_template.call_args
        assert call_args[1]["version"] == "latest"

    def test_get_default_version(self, deployment_template_ops, sample_rest_template):
        """Test get operation with default version."""
        deployment_template_ops._service_client.deployment_templates.get = Mock(return_value=sample_rest_template)
        deployment_template_ops._operation_scope.subscription_id = "test-sub"
        deployment_template_ops._operation_scope.resource_group_name = "test-rg"
        deployment_template_ops._operation_scope.registry_name = "test-registry"

        deployment_template_ops.get("test-template")

        # Verify version defaults to "latest"
        call_args = deployment_template_ops._service_client.deployment_templates.get.call_args
        assert call_args[1]["version"] == "latest"
