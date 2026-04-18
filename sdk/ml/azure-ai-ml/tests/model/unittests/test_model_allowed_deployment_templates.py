# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for Model with allowed_deployment_templates functionality."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import (
    ModelVersionData,
    ModelVersionDeploymentTemplateReference,
    ModelVersionDetails,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelVersion, ModelVersionProperties
from azure.ai.ml.entities import Model
from azure.ai.ml.entities._assets.default_deployment_template import DeploymentTemplateReference


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelAllowedDeploymentTemplates:
    """Test cases for Model entity with allowed_deployment_templates."""

    def test_model_init_with_allowed_deployment_templates(self) -> None:
        """Test creating a Model with allowed_deployment_templates."""
        templates = [
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1"),
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt2/versions/1"),
        ]
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            allowed_deployment_templates=templates,
        )

        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2
        assert model.allowed_deployment_templates[0].asset_id == templates[0].asset_id
        assert model.allowed_deployment_templates[1].asset_id == templates[1].asset_id

    def test_model_init_with_allowed_deployment_templates_as_dicts(self) -> None:
        """Test creating a Model with allowed_deployment_templates as list of dicts."""
        templates = [
            {"asset_id": "azureml://registries/reg1/deploymenttemplates/dt1/versions/1"},
            {"asset_id": "azureml://registries/reg1/deploymenttemplates/dt2/versions/1"},
        ]
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            allowed_deployment_templates=templates,  # type: ignore[arg-type]
        )

        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2
        assert all(isinstance(t, DeploymentTemplateReference) for t in model.allowed_deployment_templates)

    def test_model_init_without_allowed_deployment_templates(self) -> None:
        """Test creating a Model without allowed_deployment_templates."""
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
        )

        assert model.allowed_deployment_templates is None

    def test_model_init_with_both_default_and_allowed(self) -> None:
        """Test Model with both default and allowed deployment templates."""
        default = DeploymentTemplateReference(
            asset_id="azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"
        )
        allowed = [
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/labels/latest"),
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt2/labels/latest"),
        ]
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            default_deployment_template=default,
            allowed_deployment_templates=allowed,
        )

        assert model.default_deployment_template is not None
        assert model.default_deployment_template.asset_id == default.asset_id
        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2

    def test_model_to_rest_object_with_allowed_only(self) -> None:
        """Test _to_rest_object with only allowed_deployment_templates (no default)."""
        allowed = [
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1"),
        ]
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            allowed_deployment_templates=allowed,
        )

        rest_object = model._to_rest_object()

        # Should use ModelVersionData path
        assert isinstance(rest_object, ModelVersionData)
        assert isinstance(rest_object.properties, ModelVersionDetails)
        assert rest_object.properties.allowed_deployment_templates is not None
        assert len(rest_object.properties.allowed_deployment_templates) == 1
        assert rest_object.properties.allowed_deployment_templates[0].asset_id == allowed[0].asset_id

    def test_model_to_rest_object_with_both(self) -> None:
        """Test _to_rest_object with both default and allowed templates."""
        default = DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1")
        allowed = [
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1"),
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt2/versions/1"),
        ]
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            default_deployment_template=default,
            allowed_deployment_templates=allowed,
        )

        rest_object = model._to_rest_object()

        assert isinstance(rest_object, ModelVersionData)
        assert rest_object.properties.default_deployment_template is not None
        assert rest_object.properties.default_deployment_template.asset_id == default.asset_id
        assert rest_object.properties.allowed_deployment_templates is not None
        assert len(rest_object.properties.allowed_deployment_templates) == 2

    def test_model_to_rest_object_without_templates(self) -> None:
        """Test _to_rest_object without any deployment templates uses ModelVersion path."""
        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
        )

        rest_object = model._to_rest_object()

        # Should use standard ModelVersion path
        assert isinstance(rest_object, ModelVersion)
        assert isinstance(rest_object.properties, ModelVersionProperties)

    def test_model_from_rest_object_with_allowed_deployment_templates_dict(self) -> None:
        """Test _from_rest_object with allowed_deployment_templates as list of dicts."""
        rest_properties = Mock(spec=ModelVersionDetails)
        rest_properties.description = "Test model"
        rest_properties.tags = {}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://test/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = None
        rest_properties.job_name = None
        rest_properties.intellectual_property = None
        rest_properties.system_metadata = None
        rest_properties.default_deployment_template = None
        rest_properties.allowed_deployment_templates = [
            {"asset_id": "azureml://registries/reg1/deploymenttemplates/dt1/versions/1"},
            {"asset_id": "azureml://registries/reg1/deploymenttemplates/dt2/versions/1"},
        ]

        rest_object = Mock(spec=ModelVersionData)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        mock_system_data = Mock()
        mock_system_data.created_by = "test"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2
        assert all(isinstance(t, DeploymentTemplateReference) for t in model.allowed_deployment_templates)
        assert (
            model.allowed_deployment_templates[0].asset_id
            == "azureml://registries/reg1/deploymenttemplates/dt1/versions/1"
        )
        assert (
            model.allowed_deployment_templates[1].asset_id
            == "azureml://registries/reg1/deploymenttemplates/dt2/versions/1"
        )

    def test_model_from_rest_object_with_allowed_deployment_templates_objects(self) -> None:
        """Test _from_rest_object with allowed_deployment_templates as list of objects."""
        rest_properties = Mock(spec=ModelVersionDetails)
        rest_properties.description = "Test model"
        rest_properties.tags = {}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://test/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = None
        rest_properties.job_name = None
        rest_properties.intellectual_property = None
        rest_properties.system_metadata = None
        rest_properties.default_deployment_template = None

        template_obj1 = Mock()
        template_obj1.asset_id = "azureml://registries/reg1/deploymenttemplates/dt1/versions/1"
        template_obj2 = Mock()
        template_obj2.asset_id = "azureml://registries/reg1/deploymenttemplates/dt2/versions/1"
        rest_properties.allowed_deployment_templates = [template_obj1, template_obj2]

        rest_object = Mock(spec=ModelVersionData)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        mock_system_data = Mock()
        mock_system_data.created_by = "test"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2
        assert model.allowed_deployment_templates[0].asset_id == template_obj1.asset_id
        assert model.allowed_deployment_templates[1].asset_id == template_obj2.asset_id

    def test_model_from_rest_object_without_allowed_deployment_templates(self) -> None:
        """Test _from_rest_object without allowed_deployment_templates."""
        rest_properties = Mock(spec=ModelVersionProperties)
        rest_properties.description = "Test model"
        rest_properties.tags = {}
        rest_properties.properties = {}
        rest_properties.flavors = {}
        rest_properties.model_uri = "azureml://test/model"
        rest_properties.model_type = "custom_model"
        rest_properties.stage = None
        rest_properties.job_name = None
        rest_properties.intellectual_property = None

        rest_object = Mock(spec=ModelVersion)
        rest_object.id = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/ws/models/test-model/versions/1"
        rest_object.properties = rest_properties

        mock_system_data = Mock()
        mock_system_data.created_by = "test"
        mock_system_data.created_at = None
        mock_system_data.last_modified_by = None
        mock_system_data.last_modified_at = None
        rest_object.system_data = mock_system_data

        model = Model._from_rest_object(rest_object)

        assert model.allowed_deployment_templates is None

    def test_model_yaml_with_allowed_deployment_templates(self, tmp_path: Path) -> None:
        """Test loading a Model from YAML with allowed_deployment_templates."""
        from azure.ai.ml import load_model

        model_file = tmp_path / "model.pkl"
        model_file.write_text("dummy model")

        yaml_content = f"""
name: test-model
version: "1"
path: {str(model_file)}
description: Test model with allowed deployment templates
default_deployment_template:
  asset_id: azureml://registries/reg1/deploymenttemplates/dt1/labels/latest
allowed_deployment_templates:
  - asset_id: azureml://registries/reg1/deploymenttemplates/dt1/labels/latest
  - asset_id: azureml://registries/reg1/deploymenttemplates/dt2/labels/latest
"""
        yaml_file = tmp_path / "model.yml"
        yaml_file.write_text(yaml_content)

        model = load_model(source=yaml_file)

        assert model.name == "test-model"
        assert model.default_deployment_template is not None
        assert model.default_deployment_template.asset_id is not None
        assert "dt1" in model.default_deployment_template.asset_id
        assert model.allowed_deployment_templates is not None
        assert len(model.allowed_deployment_templates) == 2
        assert all(isinstance(t, DeploymentTemplateReference) for t in model.allowed_deployment_templates)
        assert "dt1" in model.allowed_deployment_templates[0].asset_id
        assert "dt2" in model.allowed_deployment_templates[1].asset_id

    def test_model_round_trip_rest_with_both_templates(self) -> None:
        """Test round-trip: entity -> REST -> entity with both template types."""
        default = DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1")
        allowed = [
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt1/versions/1"),
            DeploymentTemplateReference(asset_id="azureml://registries/reg1/deploymenttemplates/dt2/versions/1"),
        ]
        original = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            description="Test model",
            default_deployment_template=default,
            allowed_deployment_templates=allowed,
        )

        rest_object = original._to_rest_object()

        # Verify REST object shape
        assert isinstance(rest_object, ModelVersionData)
        assert rest_object.properties.default_deployment_template.asset_id == default.asset_id
        assert len(rest_object.properties.allowed_deployment_templates) == 2

        # Now simulate deserialization from the REST object
        # We can't do a full round-trip via _from_rest_object because it expects ARM IDs,
        # but we can verify the REST serialization is correct
        assert rest_object.properties.allowed_deployment_templates[0].asset_id == allowed[0].asset_id
        assert rest_object.properties.allowed_deployment_templates[1].asset_id == allowed[1].asset_id
