from pathlib import Path

import pytest
import yaml
from marshmallow.exceptions import ValidationError
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_model
from azure.ai.ml._schema import ModelSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._util import load_from_dict


@pytest.mark.unittest
@pytest.mark.production_experiences_test
class TestModelSchema:
    def test_deserialize_and_serialize(self) -> None:
        path = Path("./tests/test_configs/model/model_full.yml")

        def simple_model_validation(model):
            assert str(model.path).endswith("lightgbm_mlflow_model")
            assert model.type == AssetTypes.MLFLOW_MODEL

        verify_entity_load_and_dump(load_model, simple_model_validation, path)

    def test_deserialize_no_version(self) -> None:
        path = Path("./tests/test_configs/model/model_no_version.yml")
        model = load_model(path)
        assert model.version is None
        assert model._auto_increment_version
        assert model.type == AssetTypes.CUSTOM_MODEL  # assert the default model type
