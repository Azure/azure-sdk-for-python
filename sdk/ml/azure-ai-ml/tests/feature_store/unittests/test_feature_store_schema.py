# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_feature_store


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreSchema:
    def test_feature_store_load(self, randstr: Callable[[], str]) -> None:
        name = f"unittest_{randstr('featureset')}"
        description = f"{name} description"
        params_override = [{"name": name}, {"description": description}]

        def feature_store_validation(featureset):
            assert featureset.name == name
            assert featureset.description == description

        verify_entity_load_and_dump(
            load_feature_store,
            feature_store_validation,
            "./tests/test_configs/feature_store/feature_store_full.yaml",
            params_override=params_override,
        )
