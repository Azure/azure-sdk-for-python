# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_featureset


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeaturesetSchema:
    def test_featureset_load(self, randstr: Callable[[], str]) -> None:
        name = f"unittest_{randstr('featureset')}"
        description = f"{name} description"
        params_override = [{"name": name}, {"description": description}]

        def featureset_validation(featureset):
            assert featureset.name == name
            assert featureset.description == description

        verify_entity_load_and_dump(
            load_featureset,
            featureset_validation,
            "./tests/test_configs/featureset/featureset_full.yaml",
            params_override=params_override,
        )
