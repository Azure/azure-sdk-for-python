# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
import os
from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate
from azure.ai.ml.operations._deployment_template_operations import DeploymentTemplateOperations
from azure.core.exceptions import HttpResponseError


class TestDeploymentTemplateIntegration:
    """Integration tests for complete deployment template workflows."""
    
    @pytest.fixture
    def mock_service_client(self):
        """Create a mock service client for integration tests."""
        mock_client = Mock()
        mock_deployment_templates = Mock()
        mock_client.deployment_templates = mock_deployment_templates
        return mock_client

    @pytest.fixture
    def deployment_template_ops(self, mock_service_client):
        """Create DeploymentTemplateOperations instance for integration tests."""
        from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig
        
        mock_operation_scope = Mock(spec=OperationScope)
        mock_operation_config = Mock(spec=OperationConfig)
        
        return DeploymentTemplateOperations(
            operation_scope=mock_operation_scope,
            operation_config=mock_operation_config,
            service_client_04_2024_dataplanepreview=mock_service_client
        )

    def test_complete_crud_workflow(self, deployment_template_ops):
        """Test complete CRUD workflow for deployment templates."""
        # Step 1: Create a deployment template
        template = DeploymentTemplate(
            name="integration-test-template",
            version="1.0",
            description="Integration test deployment template",
            tags={"test": "integration", "env": "test"},
            properties={"model_type": "classification", "version": "1.0"},
            environment_variables={"MODEL_PATH": "/models/test", "LOG_LEVEL": "DEBUG"},
            type="deployment_template",
            deployment_template_type="model_deployment"
        )
        
        # Mock create response
        create_rest_response = Mock()
        create_rest_response.name = "integration-test-template"
        create_rest_response.template = "model_deployment"
        create_rest_response.deployment_template_type = "model_deployment"
        create_rest_response.description = "Integration test deployment template"
        create_rest_response.tags = {"test": "integration", "env": "test"}
        create_rest_response.properties = {"model_type": "classification", "version": "1.0"}
        create_rest_response.environment_id = "azureml:integration-env:1"
        create_rest_response.environment_variables = {"MODEL_PATH": "/models/test", "LOG_LEVEL": "DEBUG"}
        create_rest_response.id = "integration-template-id"
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = create_rest_response
        
        # Create the template
        created_template = deployment_template_ops.create_or_update(template)
        
        # Verify creation
        assert isinstance(created_template, DeploymentTemplate)
        assert created_template.name == "integration-test-template"
        assert created_template.id == "integration-template-id"
        assert created_template.deployment_template_type == "model_deployment"
        
        # Step 2: Get the created template
        deployment_template_ops._service_client.deployment_templates.get.return_value = create_rest_response
        
        retrieved_template = deployment_template_ops.get("integration-test-template")
        
        # Verify retrieval
        assert isinstance(retrieved_template, DeploymentTemplate)
        assert retrieved_template.name == "integration-test-template"
        assert retrieved_template.template == "model_deployment"
        assert retrieved_template.description == "Integration test deployment template"
        assert retrieved_template.tags == {"test": "integration", "env": "test"}
        assert retrieved_template.environment_id == "azureml:integration-env:1"
        
        # Step 3: Update the template
        updated_template = DeploymentTemplate(
            name="integration-test-template",
            version="2.0",
            description="Updated integration test deployment template",
            tags={"test": "integration", "env": "production"},
            properties={"model_type": "classification", "version": "2.0"},
            environment_variables={"MODEL_PATH": "/models/production", "LOG_LEVEL": "INFO"},
            type="deployment_template",
            deployment_template_type="model_deployment"
        )
        
        # Mock update response
        update_rest_response = Mock()
        update_rest_response.name = "integration-test-template"
        update_rest_response.template = "model_deployment"
        update_rest_response.deployment_template_type = "model_deployment"
        update_rest_response.description = "Updated integration test deployment template"
        update_rest_response.tags = {"test": "integration", "env": "production"}
        update_rest_response.properties = {"model_type": "classification", "version": "2.0"}
        update_rest_response.environment_id = "azureml:integration-env:2"
        update_rest_response.environment_variables = {"MODEL_PATH": "/models/production", "LOG_LEVEL": "INFO"}
        update_rest_response.id = "integration-template-id"
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = update_rest_response
        
        # Update the template
        updated_result = deployment_template_ops.create_or_update(updated_template)
        
        # Verify update
        assert updated_result.description == "Updated integration test deployment template"
        assert updated_result.tags["env"] == "production"
        assert updated_result.properties["version"] == "2.0"
        assert updated_result.environment_id == "azureml:integration-env:2"
        assert updated_result.environment_variables["LOG_LEVEL"] == "INFO"
        
        # Step 4: List templates
        mock_pager = [update_rest_response]  # Use a list instead of Mock for iteration
        deployment_template_ops._service_client.deployment_templates.list_deployment_templates.return_value = mock_pager
        
        template_list = list(deployment_template_ops.list())
        
        # Verify list
        assert len(template_list) == 1
        assert template_list[0].name == "integration-test-template"
        assert template_list[0].description == "Updated integration test deployment template"
        
        # Step 5: Delete the template
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template.return_value = None
        
        deployment_template_ops.delete_deployment_template("integration-test-template")
        
        # Verify delete was called
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template.assert_called_with(
            name="integration-test-template"
        )

    @patch('azure.ai.ml.entities._load_functions.load_deployment_template')
    def test_yaml_to_rest_api_workflow(self, mock_load, deployment_template_ops):
        """Test complete workflow from YAML file to REST API."""
        # Step 1: Create template from YAML data
        yaml_template = DeploymentTemplate(
            name="yaml-workflow-template",
            version="1.0",
            description="Template loaded from YAML",
            tags={"source": "yaml", "batch": "true"},
            properties={"batch_config": {"batch_size": 64, "timeout": 300}},
            environment_variables={
                "BATCH_SIZE": "64",
                "TIMEOUT": "300",
                "COMPUTE_TARGET": "cpu-cluster"
            },
            deployment_template_type="batch_deployment"
        )
        
        mock_load.return_value = yaml_template
        
        # Step 2: Mock REST API response
        rest_response = Mock()
        rest_response.name = "yaml-workflow-template"
        rest_response.template = "batch_deployment"
        rest_response.deployment_template_type = "batch_deployment"
        rest_response.description = "Template loaded from YAML"
        rest_response.tags = {"source": "yaml", "workflow": "test"}
        rest_response.properties = {
            "batch_config": {
                "batch_size": 64,
                "timeout": 300
            },
            "compute_target": "cpu-cluster"
        }
        rest_response.environment_id = "azureml:yaml-env:1"
        rest_response.environment_variables = {
            "BATCH_SIZE": "64",
            "TIMEOUT": "300",
            "COMPUTE_TARGET": "cpu-cluster"
        }
        rest_response.id = "yaml-template-id"
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = rest_response
        
        # Step 3: Execute workflow
        yaml_file_path = "deployment_template.yaml"
        result = deployment_template_ops.create_or_update(yaml_file_path)
        
        # Step 4: Verify workflow
        # Check that YAML was loaded
        mock_load.assert_called_once_with(source=yaml_file_path)
        
        # Check that REST API was called
        deployment_template_ops._service_client.deployment_templates.create.assert_called_once()
        
        # Verify the REST object was properly constructed
        call_args = deployment_template_ops._service_client.deployment_templates.create.call_args
        rest_obj = call_args[1]['body']
        assert rest_obj["name"] == "yaml-workflow-template"
        assert rest_obj["deploymentTemplateType"] == "batch_deployment"
        assert rest_obj["properties"]["batch_config"]["batch_size"] == 64
        
        # Verify the result
        assert isinstance(result, DeploymentTemplate)
        assert result.name == "yaml-workflow-template"
        assert result.template == "batch_deployment"
        assert result.id == "yaml-template-id"
        assert result.properties["compute_target"] == "cpu-cluster"

    def test_error_handling_workflow(self, deployment_template_ops):
        """Test error handling throughout the workflow."""
        template = DeploymentTemplate(
            name="error-test-template",
            version="1.0",
            description="Template for error testing",
            tags={"test": "error", "env": "test"},
            properties={"test_type": "error_handling"},
            deployment_template_type="model_deployment"
        )
        
        # Test create error
        deployment_template_ops._service_client.deployment_templates.create.side_effect = HttpResponseError(
            message="Bad request"
        )
        
        with pytest.raises(HttpResponseError):
            deployment_template_ops.create_or_update(template)
        
        # Test get error
        deployment_template_ops._service_client.deployment_templates.get.side_effect = HttpResponseError(
            message="Not found"
        )
        
        with pytest.raises(HttpResponseError):
            deployment_template_ops.get("nonexistent-template")
        
        # Test list error
        deployment_template_ops._service_client.deployment_templates.list_deployment_templates.side_effect = HttpResponseError(
            message="Service unavailable"
        )
        
        with pytest.raises(HttpResponseError):
            list(deployment_template_ops.list())
        
        # Test delete error
        deployment_template_ops._service_client.deployment_templates.delete_deployment_template.side_effect = HttpResponseError(
            message="Forbidden"
        )
        
        with pytest.raises(HttpResponseError):
            deployment_template_ops.delete_deployment_template("error-test-template")

    def test_field_mapping_consistency(self, deployment_template_ops):
        """Test consistency of field mapping throughout the workflow."""
        # Create template with all supported fields
        template = DeploymentTemplate(
            name="field-mapping-test",
            version="1.0",
            description="Testing field mapping consistency",
            tags={"test": "field_mapping", "env": "test"},
            properties={"mapping_type": "field_consistency"},
            environment_variables={"MAPPING": "test"},
            type="deployment_template",
            deployment_template_type="model_deployment"
        )
        
        # Mock REST response with all fields
        rest_response = Mock()
        rest_response.name = "field-mapping-test"
        rest_response.template = "model_deployment"
        rest_response.deployment_template_type = "model_deployment"
        rest_response.description = "Testing field mapping consistency"
        rest_response.tags = {"consistency": "test"}
        rest_response.properties = {"mapping": "test"}
        rest_response.environment_id = "azureml:mapping-env:1"
        rest_response.environment_variables = {"MAPPING": "test"}
        rest_response.code_id = "azureml:mapping-code:1"
        rest_response.id = "mapping-test-id"
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = rest_response
        deployment_template_ops._service_client.deployment_templates.get.return_value = rest_response
        
        # Test create workflow
        created = deployment_template_ops.create_or_update(template)
        
        # Verify create call arguments
        create_call = deployment_template_ops._service_client.deployment_templates.create.call_args
        create_rest_obj = create_call[1]['body']
        
        # Check expected field mapping in create (only check fields that would be in the request)
        assert 'deploymentTemplateType' in create_rest_obj
        assert create_rest_obj['deploymentTemplateType'] == "model_deployment"
        assert 'environmentVariables' in create_rest_obj
        assert create_rest_obj['environmentVariables'] == {"MAPPING": "test"}
        
        # Test get workflow
        retrieved = deployment_template_ops.get("field-mapping-test")
        
        # Verify all fields are properly mapped back
        assert retrieved.name == "field-mapping-test"
        assert retrieved.description == "Testing field mapping consistency"
        assert retrieved.tags == {"consistency": "test"}
        assert retrieved.properties == {"mapping": "test"}
        assert retrieved.environment_variables == {"MAPPING": "test"}
        assert retrieved.deployment_template_type == "model_deployment"
        assert retrieved.id == "mapping-test-id"

    def test_large_data_workflow(self, deployment_template_ops):
        """Test workflow with large data sets."""
        # Create template with large data
        large_tags = {f"tag_{i}": f"value_{i}" for i in range(100)}
        large_properties = {
            f"property_{i}": {
                "nested_key": f"nested_value_{i}",
                "list_data": [f"item_{j}" for j in range(10)]
            } for i in range(50)
        }
        large_env_vars = {f"ENV_VAR_{i}": f"value_{i}" for i in range(100)}
        
        template = DeploymentTemplate(
            name="large-data-template",
            version="1.0",
            description="A" * 1000,  # Large description
            tags=large_tags,
            properties=large_properties,
            environment_variables=large_env_vars,
            deployment_template_type="model_deployment"
        )
        
        # Mock REST response
        rest_response = Mock()
        rest_response.name = "large-data-template"
        rest_response.template = "model_deployment"
        rest_response.deployment_template_type = "model_deployment"
        rest_response.description = "A" * 1000
        rest_response.tags = large_tags
        rest_response.properties = large_properties
        rest_response.environment_variables = large_env_vars
        rest_response.id = "large-data-id"
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = rest_response
        
        # Execute workflow
        result = deployment_template_ops.create_or_update(template)
        
        # Verify large data handling
        assert len(result.tags) == 100
        assert len(result.properties) == 50
        assert len(result.environment_variables) == 100
        assert len(result.description) == 1000
        assert result.properties["property_0"]["list_data"] == [f"item_{j}" for j in range(10)]

    @patch('azure.ai.ml.entities._load_functions.load_deployment_template')
    def test_pathlike_object_workflow(self, mock_load, deployment_template_ops):
        """Test workflow with PathLike objects."""
        template = DeploymentTemplate(
            name="pathlike-test",
            version="1.0",
            description="Template for PathLike object testing",
            tags={"test": "pathlike", "env": "test"},
            properties={"path_type": "pathlike_test"},
            deployment_template_type="model_deployment"
        )
        
        mock_load.return_value = template
        
        rest_response = Mock()
        rest_response.name = "pathlike-test"
        rest_response.template = "model_deployment"
        rest_response.deployment_template_type = "model_deployment"
        rest_response.id = "pathlike-id"
        rest_response.tags = {"test": "pathlike", "env": "test"}
        rest_response.properties = {"path_type": "pathlike_test"}
        
        deployment_template_ops._service_client.deployment_templates.create.return_value = rest_response
        
        # Test with Path object
        path_obj = Path("template.yaml")
        result = deployment_template_ops.create_or_update(path_obj)
        
        # Verify Path object was handled correctly
        mock_load.assert_called_with(source=path_obj)
        assert result.name == "pathlike-test"
        assert result.id == "pathlike-id"
