# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_featurestore_entity


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeaturestoreEntitySchema:
    def test_featurestore_entity_load(self, randstr: Callable[[], str]) -> None:
        name = f"unittest_{randstr('featurestore_entity')}"
        description = f"{name} description"
        params_override = [{"name": name}, {"description": description}]

        def featurestore_entity_validation(featurestore_entity):
            assert featurestore_entity.name == name
            assert featurestore_entity.description == description

        verify_entity_load_and_dump(
            load_featurestore_entity,
            featurestore_entity_validation,
            "./tests/test_configs/featurestore_entity/featurestore_entity_full.yaml",
            params_override=params_override,
        )
