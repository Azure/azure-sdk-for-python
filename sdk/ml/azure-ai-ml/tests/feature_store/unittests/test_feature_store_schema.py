# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import yaml

from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._load_functions import load_feature_store


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreSchema:
    def test_feature_store_constructor(self):
        from azure.ai.ml.entities import ManagedIdentityConfiguration
        from azure.ai.ml.entities._feature_store._constants import (
            OFFLINE_MATERIALIZATION_STORE_TYPE,
            ONLINE_MATERIALIZATION_STORE_TYPE,
        )
        from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
        from azure.ai.ml.exceptions import ValidationException

        IDENTITY_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/test_rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/exist_identity"
        OFFLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/test_rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/exist"
        ONLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/exist"

        feature_store = FeatureStore(
            name="dummy_name",
            materialization_identity=ManagedIdentityConfiguration(resource_id=IDENTITY_RESOURCE_ID),
            offline_store=MaterializationStore(
                type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=OFFLINE_STORE_RESOURCE_ID
            ),
            online_store=MaterializationStore(type=ONLINE_MATERIALIZATION_STORE_TYPE, target=ONLINE_STORE_RESOURCE_ID),
            description="dummy_description",
            display_name="dummy_display_name",
            identity=ManagedIdentityConfiguration(resource_id=IDENTITY_RESOURCE_ID),
            resource_group="rg",
            location="eastus",
            tags={
                "key": "value",
            },
        )

        assert feature_store.name == "dummy_name"
        assert feature_store.materialization_identity is not None
        assert feature_store.offline_store is not None
        assert feature_store.online_store is not None
        assert feature_store.description == "dummy_description"
        assert feature_store.display_name == "dummy_display_name"
        assert feature_store.identity is not None
        assert feature_store._feature_store_settings is not None
        assert feature_store._feature_store_settings.online_store_connection_name is None
        assert feature_store._feature_store_settings.offline_store_connection_name is None
        assert feature_store._feature_store_settings.compute_runtime is not None
        assert feature_store.location == "eastus"
        assert feature_store.resource_group == "rg"
        assert feature_store.tags is not None
        assert feature_store.hbi_workspace is False
        assert feature_store.storage_account is None
        assert feature_store.container_registry is None
        assert feature_store.key_vault is None
        assert feature_store.application_insights is None
        assert feature_store.customer_managed_key is None
        assert feature_store.image_build_compute is None
        assert feature_store.public_network_access is None
        assert feature_store.primary_user_assigned_identity is None
        assert feature_store.managed_network is None

    def test_feature_store_load(self) -> None:
        test_path = "./tests/test_configs/feature_store/feature_store_full.yaml"
        with open(test_path, "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            feature_store: FeatureStore = load_feature_store(source=test_path)
        assert feature_store.name == target["name"]
        assert feature_store.description == target["description"]
        assert feature_store.materialization_identity is not None
        assert feature_store.offline_store is not None
        assert feature_store.tags is not None
        assert feature_store.properties is not None
        assert feature_store.managed_network is not None
        assert feature_store.managed_network.outbound_rules is not None

    def test_materialization_store(self):
        from azure.ai.ml.entities._feature_store._constants import (
            OFFLINE_MATERIALIZATION_STORE_TYPE,
            ONLINE_MATERIALIZATION_STORE_TYPE,
        )
        from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
        from azure.ai.ml.exceptions import ValidationException

        with pytest.raises(ValidationException) as ve:
            FeatureStore(
                name="name",
                description="description",
                offline_store=MaterializationStore(
                    type=OFFLINE_MATERIALIZATION_STORE_TYPE, target="offline_store_resource_id"
                ),
            )
        assert "Invalid ARM Id" in str(ve)

        with pytest.raises(ValidationException) as ve:
            FeatureStore(
                name="name",
                description="description",
                online_store=MaterializationStore(
                    type=ONLINE_MATERIALIZATION_STORE_TYPE, target="online_store_resource_id"
                ),
            )
        assert "Invalid ARM Id" in str(ve)
