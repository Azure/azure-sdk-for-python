# TODO determine where this should live
from pathlib import Path
import pytest

from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
import pytest
import yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema.assets.federated_learning_silo import FederatedLearningSiloSchema


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestFederatedLearningSilo:
    def test_load_silo_from_yaml(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            silo = load_from_dict(FederatedLearningSiloSchema, target, context)
            assert silo
            assert silo["compute"] == "some_compute"
            assert silo["datastore"] == "some_datastore"
            assert (
                silo["inputs"]["test_dataset"]["path"]
                == "/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/data/fake-dataset/versions/2"
            )
            assert silo["inputs"]["test_dataset"]["type"] == AssetTypes.MLTABLE
            assert silo["inputs"]["test_string_literal"] == "literal string"
            assert silo["inputs"]["test_literal_valued_int"] == 42

    def test_load_silo_from_yaml_singleton_data(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo_one_input.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            silo = load_from_dict(FederatedLearningSiloSchema, target, context)
            assert silo
            assert silo["compute"] == "some_compute"
            assert silo["datastore"] == "some_datastore"
            assert silo["inputs"]["test_dataset"]["path"] == "some_path"
            assert silo["inputs"]["test_dataset"]["type"] == AssetTypes.URI_FOLDER

    def test_load_silo_entity_from_yaml(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo.yaml")
        silo_entity = FederatedLearningSilo._load(path)
        assert silo_entity.datastore == "some_datastore"
        assert silo_entity.compute == "some_compute"
        assert (
            silo_entity.inputs["test_dataset"]["path"]
            == "/subscriptions/d511f82f-71ba-49a4-8233-d7be8a3650f4/resourceGroups/RLTesting/providers/Microsoft.MachineLearningServices/workspaces/AnkitWS/data/fake-dataset/versions/2"
        )
        assert silo_entity.inputs["test_dataset"]["type"] == AssetTypes.MLTABLE
        assert silo_entity.inputs["test_string_literal"] == "literal string"
        assert silo_entity.inputs["test_literal_valued_int"]["value"] == 42

        path = Path("./tests/test_configs/federated_learning/example_silo_one_input.yaml")
        silo_entity = FederatedLearningSilo._load(path)
        assert silo_entity.datastore == "some_datastore"
        assert silo_entity.compute == "some_compute"
        assert silo_entity.inputs["test_dataset"]["path"] == "some_path"

    def test_load_silo_list(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo_list.yaml")
        silos = FederatedLearningSilo.load_list(yaml_path=path, list_arg="silos")
        assert silos[0].datastore == "some_datastore"
        assert silos[0].compute == "some_compute"
        assert silos[0].inputs == {}

        assert silos[1].datastore == "some_datastore2"
        assert silos[1].compute == "some_compute2"
        assert silos[1].inputs["test_uri"]["type"] == AssetTypes.URI_FOLDER
        assert silos[1].inputs["test_uri"]["path"] == "some_path"
