from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_model
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import ModelVersionData
from azure.ai.ml._schema import ModelSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._util import load_from_dict

# Get the directory of this test file and construct absolute paths
TEST_DIR = Path(__file__).parent.parent.parent
TEST_CONFIGS_DIR = TEST_DIR / "test_configs" / "model"


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelSchema:
    def test_deserialize_and_serialize(self) -> None:
        path = TEST_CONFIGS_DIR / "model_full.yml"

        def simple_model_validation(model):
            assert str(model.path).endswith("lightgbm_mlflow_model")
            assert model.type == AssetTypes.MLFLOW_MODEL

        verify_entity_load_and_dump(load_model, simple_model_validation, path)

    def test_deserialize_no_version(self) -> None:
        path = TEST_CONFIGS_DIR / "model_no_version.yml"
        model = load_model(path)
        assert model.version is None
        assert model._auto_increment_version
        assert model.type == AssetTypes.CUSTOM_MODEL  # assert the default model type

    def test_deserialize_with_stage(self) -> None:
        path = TEST_CONFIGS_DIR / "model_with_stage.yml"
        model = load_model(path)
        assert model.stage == "Production"

    def test_deserialize_with_system_metadata(self) -> None:
        path = TEST_CONFIGS_DIR / "model_with_system_metadata.yml"
        model = load_model(path)
        assert model._system_metadata
        assert model._system_metadata["publisher"] == "Contoso"
        assert model._system_metadata["license"] == "MIT License"

        model_version_resource = model._to_rest_object()
        assert model_version_resource.properties.system_metadata
        assert model_version_resource.properties.system_metadata["publisher"] == "Contoso"
        assert model_version_resource.properties.system_metadata["license"] == "MIT License"

    def test_ipp_model(self) -> None:
        rest_ipp_model = {
            "id": "azureml://registries/fake_registry/models/fake_ipp_model/versions/611575",
            "name": "ada",
            "type": "models",
            "properties": {
                "description": "a description",
                "tags": {},
                "properties": {},
                "isArchived": False,
                "isAnonymous": False,
                "flavors": {},
                "modelType": "custom_model",
                "modelUri": "azureml://datastore/fake_datastore/paths/fake_model_uri",
                "originAssetId": "fake_origin_asset_id",
                "jobName": "fake_job_name",
                "intellectualProperty": {
                    "publisher": "Contoso",
                    "protectionLevel": "All",
                },
            },
            "systemData": {},
        }

        from_rest_ipp_model = Model._from_rest_object(ModelVersionData.deserialize(rest_ipp_model))

        assert from_rest_ipp_model._intellectual_property
        assert from_rest_ipp_model._intellectual_property.protection_level == "All"
        assert from_rest_ipp_model._intellectual_property.publisher == "Contoso"

        ipp_model_dict = from_rest_ipp_model._to_dict()
        assert ipp_model_dict["intellectual_property"]
        assert ipp_model_dict["intellectual_property"]["protection_level"] == "all"
        assert ipp_model_dict["intellectual_property"]["publisher"] == "Contoso"

    def test_model_with_default_deployment_template_from_yaml(self, tmp_path: Path) -> None:
        """Test loading a model with default_deployment_template from YAML."""
        # Create a dummy model file
        model_file = tmp_path / "model.pkl"
        model_file.write_text("dummy model")

        yaml_content = f"""
$schema: https://azuremlschemas.azureedge.net/latest/model.schema.json
name: model_with_default_template
version: "1"
type: custom_model
path: {str(model_file)}
description: "Model with default deployment template"
default_deployment_template:
  asset_id: azureml://registries/test-registry/deploymenttemplates/template1/versions/1
"""
        yaml_file = tmp_path / "model_with_template.yml"
        yaml_file.write_text(yaml_content)

        model = load_model(yaml_file)

        assert model.default_deployment_template is not None
        assert model.default_deployment_template.asset_id is not None
        assert "test-registry" in model.default_deployment_template.asset_id
        assert "deploymenttemplates" in model.default_deployment_template.asset_id

    def test_model_with_default_deployment_template_to_rest_object(self) -> None:
        """Test Model._to_rest_object() with default_deployment_template."""
        from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate
        from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import ModelVersionData

        template = DefaultDeploymentTemplate(
            asset_id="azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        )

        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            description="Test model with deployment template",
            default_deployment_template=template,
        )

        rest_object = model._to_rest_object()

        # Should return ModelVersionData when default_deployment_template is present
        assert isinstance(rest_object, ModelVersionData)
        assert rest_object.properties.default_deployment_template is not None
        assert rest_object.properties.default_deployment_template.asset_id == template.asset_id

    def test_model_with_default_deployment_template_from_rest_object(self) -> None:
        """Test Model._from_rest_object() with default_deployment_template."""
        rest_model_with_template = {
            "id": "azureml://registries/fake_registry/models/fake_model/versions/1",
            "name": "fake_model",
            "type": "models",
            "properties": {
                "description": "Model with deployment template",
                "tags": {},
                "properties": {},
                "isArchived": False,
                "isAnonymous": False,
                "flavors": {},
                "modelType": "custom_model",
                "modelUri": "azureml://datastore/fake_datastore/paths/fake_model_uri",
                "defaultDeploymentTemplate": {
                    "assetId": "azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
                },
            },
            "systemData": {},
        }

        from_rest_model = Model._from_rest_object(ModelVersionData.deserialize(rest_model_with_template))

        assert from_rest_model.default_deployment_template is not None
        assert from_rest_model.default_deployment_template.asset_id is not None
        assert "test-registry" in from_rest_model.default_deployment_template.asset_id
        assert "deploymenttemplates" in from_rest_model.default_deployment_template.asset_id

    def test_model_with_default_deployment_template_to_dict(self) -> None:
        """Test Model._to_dict() with default_deployment_template."""
        from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate

        template = DefaultDeploymentTemplate(
            asset_id="azureml://registries/test-registry/deploymenttemplates/template1/versions/1"
        )

        model = Model(
            name="test-model",
            version="1",
            path="./model.pkl",
            description="Test model with deployment template",
            default_deployment_template=template,
        )

        model_dict = model._to_dict()

        assert "default_deployment_template" in model_dict
        assert model_dict["default_deployment_template"] is not None
        assert "asset_id" in model_dict["default_deployment_template"]
        assert model_dict["default_deployment_template"]["asset_id"] == template.asset_id
