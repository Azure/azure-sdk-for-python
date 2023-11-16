from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_model
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import ModelVersionData, EnvironmentVersionData
from azure.ai.ml._schema import ModelSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.entities._assets import Model, Environment
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._load_functions import load_model, load_model_package, load_online_deployment


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelPackageSchema:
    def test_model_package(self) -> None:
        file = Path("tests/test_configs/model_package/model_package_simple.yml")
        model_pack = load_model_package(source=file)
        assert model_pack.name == "diabetes-online-mlflow"
        assert model_pack.inferencing_server.type == "azureml_online"
        assert model_pack.model_configuration.mode == "download"

    def test_model_package_with_online_deployment(self) -> None:
        file = Path("tests/test_configs/model_package/online_deployment_registry_package.yml")
        deployment = load_online_deployment(source=file)
        assert deployment.environment == "azureml://registries/bani-euap/environments/testv1/versions/20"
        assert deployment.model == "azureml://registries/bani-euap/models/demo_ml/versions/1"

    def test_model_package_schema(self) -> None:
        file = Path("tests/test_configs/model_package/model_package_config_copy.yml")
        deployment = load_model_package(source=file)
        assert deployment.model_configuration.mode == "copy"
