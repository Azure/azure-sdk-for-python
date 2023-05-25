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

    def test_deserialize_with_stage(self) -> None:
        path = Path("./tests/test_configs/model/model_with_stage.yml")
        model = load_model(path)
        assert model.stage == "Production"

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
