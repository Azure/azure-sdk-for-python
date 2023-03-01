# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import is_live

from azure.ai.ml import MLClient
from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.data_experiences_test
@pytest.mark.usefixtures(
    "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestFeatureStore:
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_feature_store_create_update_and_delete(
        self, client: MLClient, randstr: Callable[[], str], location: str
    ) -> None:
        fs_name = f"e2etest_{randstr('fs_name')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs = FeatureStore(
            name=fs_name, description=fs_description, display_name=fs_display_name, location="westcentralus"
        )
        fs_poller = client.featurestores.begin_create(feature_store=fs)
        assert isinstance(fs_poller, LROPoller)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)

        fs_result = client.featurestores.get(fs_name)
        assert isinstance(fs_result, FeatureStore)
        assert fs_result.name == fs_name

        fs_list = client.featurestores.list()
        assert any(fs_name == fs.name for fs in fs_list)

        fs_poller = client.featurestores.begin_delete(name=fs_name, delete_dependent_resources=True)
        assert isinstance(fs_poller, LROPoller)
        fs_poller.result()

        with pytest.raises(Exception):
            client.featurestores.get(fs_name)
