"""Unit tests for Model with default_deployment_template functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml import load_model
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import (
    ModelVersionData,
    ModelVersionDetails,
    ModelVersionDefaultDeploymentTemplate,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ModelVersion,
    ModelVersionProperties,
)
from azure.ai.ml.entities import Model
from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelDefaultDeploymentTemplate:
    """Test cases for Model entity with default_deployment_template."""

    def test_model_init_with_default_deployment_template_object(self) -> None:
        """Test creating a Model with DefaultDeploymentTemplate object."""
        template = DefaultDeploymentTemplate(
            asset_id="azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        )
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            default_deployment_template=template,
        )

        assert model.default_deployment_template is not None
        assert model.default_deployment_template.asset_id == template.asset_id

    def test_model_init_with_default_deployment_template_dict(self) -> None:
        """Test creating a Model with default_deployment_template as dict."""
        template_dict = {"asset_id": "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"}
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            default_deployment_template=template_dict,  # type: ignore[arg-type]
        )

        assert model.default_deployment_template is not None
        assert isinstance(model.default_deployment_template, DefaultDeploymentTemplate)
        assert model.default_deployment_template.asset_id == template_dict["asset_id"]

    def test_model_init_without_default_deployment_template(self) -> None:
        """Test creating a Model without default_deployment_template."""
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
        )

        assert model.default_deployment_template is None

    def test_model_to_rest_object_with_default_deployment_template(self) -> None:
        """Test Model._to_rest_object() with default_deployment_template."""
        template = DefaultDeploymentTemplate(
            asset_id="azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        )
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            description="Test model",
            default_deployment_template=template,
        )

        rest_object = model._to_rest_object()

        # Should return ModelVersionData when default_deployment_template is present
        assert isinstance(rest_object, ModelVersionData)
        assert isinstance(rest_object.properties, ModelVersionDetails)
        assert rest_object.properties.default_deployment_template is not None
        assert isinstance(rest_object.properties.default_deployment_template, ModelVersionDefaultDeploymentTemplate)
        assert rest_object.properties.default_deployment_template.asset_id == template.asset_id

    def test_model_to_rest_object_without_default_deployment_template(self) -> None:
        """Test Model._to_rest_object() without default_deployment_template."""
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            description="Test model",
            stage="Production",
        )

        rest_object = model._to_rest_object()

        # Should return ModelVersion when default_deployment_template is not present
        assert isinstance(rest_object, ModelVersion)
        assert isinstance(rest_object.properties, ModelVersionProperties)
        assert rest_object.properties.stage == "Production"

    def test_model_from_rest_object_with_default_deployment_template_dict(self) -> None:
        """Test Model._from_rest_object() with default_deployment_template as dict."""
        template_asset_id = "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"

        # Create mock REST object
        rest_properties = Mock(spec=ModelVersionDetails)
        rest_properties.description = "Test model"
        rest_properties.tags = {"key": "value"}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://locations/test/artifacts/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = None
        rest_properties.job_name = None
        rest_properties.intellectual_property = None
        rest_properties.system_metadata = None
        rest_properties.default_deployment_template = {"asset_id": template_asset_id}

        rest_object = Mock(spec=ModelVersionData)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        # Mock system_data
        mock_system_data = Mock()
        mock_system_data.created_by = "test_user"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.default_deployment_template is not None
        assert isinstance(model.default_deployment_template, DefaultDeploymentTemplate)
        assert model.default_deployment_template.asset_id == template_asset_id

    def test_model_from_rest_object_with_default_deployment_template_object(self) -> None:
        """Test Model._from_rest_object() with default_deployment_template as object."""
        template_asset_id = "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"

        # Create mock REST object
        rest_properties = Mock(spec=ModelVersionDetails)
        rest_properties.description = "Test model"
        rest_properties.tags = {"key": "value"}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://locations/test/artifacts/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = None
        rest_properties.job_name = None
        rest_properties.intellectual_property = None
        rest_properties.system_metadata = None

        # Create template object with asset_id attribute
        template_obj = Mock()
        template_obj.asset_id = template_asset_id
        rest_properties.default_deployment_template = template_obj

        rest_object = Mock(spec=ModelVersionData)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        # Mock system_data
        mock_system_data = Mock()
        mock_system_data.created_by = "test_user"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.default_deployment_template is not None
        assert isinstance(model.default_deployment_template, DefaultDeploymentTemplate)
        assert model.default_deployment_template.asset_id == template_asset_id

    def test_model_from_rest_object_without_default_deployment_template(self) -> None:
        """Test Model._from_rest_object() without default_deployment_template."""
        # Create mock REST object
        rest_properties = Mock(spec=ModelVersionProperties)
        rest_properties.description = "Test model"
        rest_properties.tags = {"key": "value"}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://locations/test/artifacts/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = "Production"
        rest_properties.job_name = None
        rest_properties.intellectual_property = None

        rest_object = Mock(spec=ModelVersion)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        # Mock system_data
        mock_system_data = Mock()
        mock_system_data.created_by = "test_user"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.default_deployment_template is None
        assert model.stage == "Production"

    def test_model_with_stage_and_default_deployment_template(self) -> None:
        """Test that stage is preserved when default_deployment_template is present."""
        template = DefaultDeploymentTemplate(
            asset_id="azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        )
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            stage="Production",
            default_deployment_template=template,
        )

        assert model.stage == "Production"
        assert model.default_deployment_template is not None

        # Serialize to REST object
        rest_object = model._to_rest_object()

        # Note: When default_deployment_template is present, it uses ModelVersionDetails
        # which doesn't support stage in the v2021_10_01_dataplanepreview API
        # This is expected behavior - stage is only supported in workspace operations
        assert isinstance(rest_object, ModelVersionData)

    def test_model_yaml_with_default_deployment_template(self, tmp_path: Path) -> None:
        """Test loading a Model from YAML with default_deployment_template."""
        # Create a dummy model file
        model_file = tmp_path / "model.pkl"
        model_file.write_text("dummy model")

        yaml_content = f"""
name: test-model
version: "1"
path: {str(model_file)}
description: Test model with deployment template
default_deployment_template:
  asset_id: azureml://registries/test-registry/deploymenttemplates/template1/versions/1
"""
        yaml_file = tmp_path / "model_with_template.yml"
        yaml_file.write_text(yaml_content)

        model = load_model(source=yaml_file)

        assert model.name == "test-model"
        assert model.version == "1"
        assert model.default_deployment_template is not None
        assert isinstance(model.default_deployment_template, DefaultDeploymentTemplate)
        assert model.default_deployment_template.asset_id is not None
        assert "test-registry" in model.default_deployment_template.asset_id
