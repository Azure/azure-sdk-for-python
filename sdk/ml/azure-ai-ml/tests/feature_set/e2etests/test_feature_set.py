from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient
from azure.ai.ml.entities._load_functions import _load_feature_set, _load_feature_store_entity

from azure.ai.ml.entities._assets._artifacts.feature_set import _FeatureSet
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller

from azure.ai.ml.entities import (
    _FeatureSet,
)

@pytest.mark.e2etest
@pytest.mark.data_experiences_test
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestFeatureSet(AzureRecordedTestCase):
    def test_create_and_get(self, feature_store_client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        fset_name = f"e2etest_{randstr('fset_name')}"
        fset_description = "Feature set description"
        fs_entity_name = f"e2etest_{randstr('fs_entity_name')}"
        fs_entity_description = "Feature store entity description"

        version = "1"

        params_override = [
            {"name": fs_entity_name},
            {"version": version},
            {"description": fs_entity_description},
        ]

        def feature_store_entitiy_validation(fs_entity):
            fs_entity_poller = feature_store_client._feature_store_entities.begin_create_or_update(
                feature_store_entity=fs_entity
            )
            assert isinstance(fs_entity_poller, LROPoller)
            fs_entity = fs_entity_poller.result()

        featureStoreEntity = verify_entity_load_and_dump(
            _load_feature_store_entity,
            feature_store_entitiy_validation,
            "./tests/test_configs/feature_store_entity/feature_store_entity_full.yaml",
            params_override=params_override,
        )[0]

        params_override = [
            {"name": fset_name},
            {"version": version},
            {"description": fset_description},
        ]

        def feature_set_validation(fset):
            fset.entities = [f"azureml:{fs_entity_name}:{version}"]
            fset_poller = feature_store_client._feature_sets.begin_create_or_update(
                featureset=fset
            )
            assert isinstance(fset_poller, LROPoller)
            fset = fset_poller.result()
            assert isinstance(fset, _FeatureSet)
            assert fset.name == fset_name
            assert fset.description == fset_description

        fset = verify_entity_load_and_dump(
            _load_feature_set,
            feature_set_validation,
            "./tests/test_configs/feature_set/feature_set_full.yaml",
            params_override=params_override,
        )[0]

        fset_list = feature_store_client._feature_sets.list(name=fset_name)
        assert isinstance(fset_list, ItemPaged)

        fset = feature_store_client._feature_sets.get(name=fset_name, version=version)
        assert isinstance(fset, _FeatureSet)
        assert fset.name == fset_name
