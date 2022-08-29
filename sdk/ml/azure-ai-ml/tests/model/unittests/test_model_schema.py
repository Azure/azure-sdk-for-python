from pathlib import Path
import pytest
import yaml

from azure.ai.ml._schema import ModelSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AssetTypes
from marshmallow.exceptions import ValidationError
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._assets import Model
from azure.ai.ml import load_model


@pytest.mark.unittest
class TestModelSchema:
    def test_deserialize(self) -> None:
        path = Path("./tests/test_configs/model/model_full.yml")
        model = load_model(path)
        assert str(model.path).endswith("lightgbm_mlflow_model")
        assert model.type == AssetTypes.MLFLOW_MODEL

    def test_deserialize_no_version(self) -> None:
        path = Path("./tests/test_configs/model/model_no_version.yml")
        model = load_model(path)
        assert model.version is None
        assert model._auto_increment_version
        assert model.type == AssetTypes.CUSTOM_MODEL  # assert the default model type
