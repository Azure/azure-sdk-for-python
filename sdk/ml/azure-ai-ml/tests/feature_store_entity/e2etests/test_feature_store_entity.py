# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient
from azure.ai.ml.entities._load_functions import load_feature_store_entity

from azure.ai.ml.entities._feature_store_entity.feature_store_entity import FeatureStoreEntity
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.data_experiences_test
@pytest.mark.usefixtures("recorded_test", "mock_code_hash")
class TestFeatureStoreEntity(AzureRecordedTestCase):
    def test_create_and_get(self, feature_store_client: MLClient, tmp_path: Path, randstr: Callable[[], str]) -> None:
        fs_entity_name = f"e2etest_{randstr('fs_entity_name')}"
        fs_entity_description = "Feature store entity description"
        version = "1"

        params_override = [
            {"name": fs_entity_name},
            {"version": version},
            {"description": fs_entity_description},
        ]

        def feature_store_entitiy_validation(fs_entity):
            fs_entity_poller = feature_store_client.feature_store_entities.begin_create_or_update(
                feature_store_entity=fs_entity
            )
            assert isinstance(fs_entity_poller, LROPoller)
            fs_entity = fs_entity_poller.result()
            assert isinstance(fs_entity, FeatureStoreEntity)
            assert fs_entity.name == fs_entity_name
            assert fs_entity.description == fs_entity_description

        featureStoreEntity = verify_entity_load_and_dump(
            load_feature_store_entity,
            feature_store_entitiy_validation,
            "./tests/test_configs/feature_store_entity/feature_store_entity_full.yaml",
            params_override=params_override,
        )[0]

        entity_list = feature_store_client.feature_store_entities.list(name=fs_entity_name)
        assert isinstance(entity_list, ItemPaged)

        fs_entity = feature_store_client.feature_store_entities.get(name=fs_entity_name, version=version)
        assert isinstance(fs_entity, FeatureStoreEntity)
        assert fs_entity.name == fs_entity_name
