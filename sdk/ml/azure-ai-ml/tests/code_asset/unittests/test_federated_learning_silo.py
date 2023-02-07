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
            assert silo["inputs"][0]["path"] == "path_1"
            assert silo["inputs"][0]["type"] == AssetTypes.MLTABLE
            assert silo["inputs"][1]["path"] == "path_2"
            assert silo["inputs"][1]["type"] == AssetTypes.URI_FOLDER

    def test_load_silo_from_yaml_singleton_data(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo_one_input.yaml")
        with open(path, "r") as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            silo = load_from_dict(FederatedLearningSiloSchema, target, context)
            assert silo
            assert silo["compute"] == "some_compute"
            assert silo["datastore"] == "some_datastore"
            assert silo["inputs"]["path"] == "path_1"
            assert silo["inputs"]["type"] == AssetTypes.MLTABLE


    def test_load_silo_entity_from_yaml(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo.yaml")
        silo_entity = FederatedLearningSilo._load(path)
        assert silo_entity.datastore == "some_datastore"
        assert silo_entity.compute == "some_compute"
        # TODO: Make path testing robust - inputs paths are messed around with upon being inputted 
        # into a data object
        #assert silo_entity.inputs[0].path == "path_1"
        assert silo_entity.inputs[0].type == AssetTypes.MLTABLE
        #assert silo_entity.inputs[1].path == "path_2"
        assert silo_entity.inputs[1].type == AssetTypes.URI_FOLDER

        
        path = Path("./tests/test_configs/federated_learning/example_silo_one_input.yaml")
        silo_entity = FederatedLearningSilo._load(path)
        assert silo_entity.datastore == "some_datastore"
        assert silo_entity.compute == "some_compute"
        assert silo_entity.inputs[0].type == AssetTypes.MLTABLE

    def test_load_silo_list(self) -> None:
        path = Path("./tests/test_configs/federated_learning/example_silo_list.yaml")
        silos = FederatedLearningSilo.load_list(yaml_path=path, list_arg="silos")
        assert silos[0].datastore == "some_datastore"
        assert silos[0].compute == "some_compute"
        assert silos[0].inputs[0].type == AssetTypes.MLTABLE
        assert silos[0].inputs[1].type == AssetTypes.URI_FOLDER

    
        assert silos[1].datastore == "some_datastore"
        assert silos[1].compute == "some_compute"
        assert silos[1].inputs[0].type == AssetTypes.MLTABLE
        
        

