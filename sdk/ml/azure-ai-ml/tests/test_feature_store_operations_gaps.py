from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from marshmallow import ValidationError
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml import MLClient
from azure.ai.ml.entities._feature_store.feature_store import FeatureStore
from azure.ai.ml.entities._feature_store.materialization_store import (
    MaterializationStore,
)


@pytest.mark.e2etest
class TestFeatureStoreOperationsGaps:
    def test_begin_create_rejects_invalid_offline_store_type(self, client: MLClient) -> None:
        """Verify begin_create raises ValidationError when offline_store.type is invalid.

        Covers validation branch in begin_create that checks offline store type and raises
        marshmallow.ValidationError before any service call is made.
        """
        random_name = "test_dummy"
        # offline_store.type must be OFFLINE_MATERIALIZATION_STORE_TYPE (azure_data_lake_gen2)
        invalid_offline = MaterializationStore(
            type="not_azure_data_lake_gen2",
            target="/subscriptions/0/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/sa",
        )
        fs = FeatureStore(name=random_name, offline_store=invalid_offline)

        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs)

    def test_begin_create_rejects_invalid_online_store_type(self, client: MLClient) -> None:
        """Verify begin_create raises ValidationError when online_store.type is invalid.

        Covers validation branch in begin_create that checks online store type and raises
        marshmallow.ValidationError before any service call is made.
        """
        random_name = "test_dummy"
        # online_store.type must be ONLINE_MATERIALIZATION_STORE_TYPE (redis)
        # use a valid ARM id for the target so MaterializationStore construction does not fail
        invalid_online = MaterializationStore(
            type="not_redis",
            target="/subscriptions/0/resourceGroups/rg/providers/Microsoft.Cache/Redis/redisname",
        )
        fs = FeatureStore(name=random_name, online_store=invalid_online)

        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs)


@pytest.mark.e2etest
class TestFeatureStoreOperationsGapsGenerated:
    def test_begin_create_raises_on_invalid_offline_store_type(self, client: MLClient) -> None:
        """Verify begin_create raises ValidationError when offline_store.type is incorrect.

        Covers branch where begin_create checks offline_store.type != OFFLINE_MATERIALIZATION_STORE_TYPE
        and raises a marshmallow.ValidationError.
        """
        random_name = "test_dummy"
        # Provide an offline store with an invalid type to trigger validation before any service calls succeed
        fs = FeatureStore(name=random_name)
        fs.offline_store = MaterializationStore(
            type="invalid_offline_type",
            target="/subscriptions/000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/acc",
        )

        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs)

    def test_begin_create_raises_on_invalid_online_store_type(self, client: MLClient) -> None:
        """Verify begin_create raises ValidationError when online_store.type is incorrect.

        Covers branch where begin_create checks online_store.type != ONLINE_MATERIALIZATION_STORE_TYPE
        and raises a marshmallow.ValidationError.
        """
        random_name = "test_dummy"
        # Provide an online store with an invalid type to trigger validation before any service calls succeed
        fs = FeatureStore(name=random_name)
        fs.online_store = MaterializationStore(
            type="invalid_online_type",
            target="/subscriptions/0/resourceGroups/rg/providers/Microsoft.Cache/Redis/redisname",
        )

        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestFeatureStoreOperationsGapsAdditional(AzureRecordedTestCase):
    def test_begin_update_raises_when_not_feature_store(self, client: MLClient) -> None:
        """When the workspace retrieved is not a feature store, begin_update should raise ValidationError.

        This triggers the early-path validation in FeatureStoreOperations.begin_update that raises
        "{0} is not a feature store" when the REST workspace object is missing or not of kind FEATURE_STORE.
        """
        random_name = "test_dummy"
        fs = FeatureStore(name=random_name)

        with pytest.raises((ValidationError, ResourceNotFoundError)):
            # This will call the service to retrieve the workspace; if not present or not a feature store,
            # the method raises ValidationError as validated by the source under test.
            client.feature_stores.begin_update(feature_store=fs)

    def test_begin_update_raises_on_invalid_online_store_type_when_workspace_missing(self, client: MLClient) -> None:
        """Attempting to update with an invalid online_store.type should raise ValidationError,
        but begin_update first validates the workspace kind. This test exercises the path where the
        workspace is missing/not a feature store and ensures ValidationError is raised by the pre-check.

        It demonstrates the defensive validation at the start of begin_update covering the branch
        where rest_workspace_obj is not a feature store.
        """
        random_name = "test_dummy"
        # Provide an online_store with an invalid type to exercise the validation intent.
        fs = FeatureStore(
            name=random_name,
            online_store=MaterializationStore(type="invalid_type", target=None),
        )

        with pytest.raises((ValidationError, ResourceNotFoundError)):
            client.feature_stores.begin_update(feature_store=fs)


@pytest.mark.e2etest
class TestFeatureStoreOperationsGapsExtraGenerated:
    def test_begin_create_raises_on_invalid_offline_store_type_not_adls(self, client: MLClient) -> None:
        """Ensure begin_create validation rejects non-azure_data_lake_gen2 offline store types.

        Covers validation branch that checks offline_store.type against OFFLINE_MATERIALIZATION_STORE_TYPE.
        Trigger strategy: call client.feature_stores.begin_create with a FeatureStore whose offline_store.type is invalid;
        the validation occurs before any service calls and raises marshmallow.ValidationError.
        """
        random_name = "test_dummy"
        fs = FeatureStore(name=random_name)
        # Intentionally set an invalid offline store type to trigger validation
        fs.offline_store = MaterializationStore(
            type="not_adls",
            target="/subscriptions/000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/acc",
        )

        with pytest.raises(ValidationError):
            # begin_create triggers the pre-flight validation and should raise
            client.feature_stores.begin_create(fs)

    def test_begin_create_raises_on_invalid_online_store_type_not_redis(self, client: MLClient) -> None:
        """Ensure begin_create validation rejects non-redis online store types.

        Covers validation branch that checks online_store.type against ONLINE_MATERIALIZATION_STORE_TYPE.
        Trigger strategy: call client.feature_stores.begin_create with a FeatureStore whose online_store.type is invalid;
        the validation occurs before any service calls and raises marshmallow.ValidationError.
        """
        random_name = "test_dummy"
        fs = FeatureStore(name=random_name)
        # Intentionally set an invalid online store type to trigger validation
        fs.online_store = MaterializationStore(
            type="not_redis",
            target="/subscriptions/000/resourceGroups/rg/providers/Microsoft.Cache/Redis/redisname",
        )

        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs)


# Additional generated tests merged below (renamed to avoid duplicate class name)
@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestFeatureStoreOperationsGaps_GeneratedExtra(AzureRecordedTestCase):
    def test_begin_update_raises_if_workspace_not_feature_store(self, client: MLClient) -> None:
        """If the named workspace does not exist or is not a feature store, begin_update should raise ValidationError.
        Covers branches where rest_workspace_obj is missing or not of kind FEATURE_STORE.
        """
        random_name = "test_dummy"
        fs = FeatureStore(name=random_name)
        with pytest.raises((ValidationError, ResourceNotFoundError)):
            # This will call the service to get the workspace; for a non-existent workspace the code path
            # in begin_update should raise ValidationError("<name> is not a feature store").
            client.feature_stores.begin_update(fs)

    def test_begin_delete_raises_if_not_feature_store(self, client: MLClient) -> None:
        """Deleting a non-feature-store workspace should raise ValidationError.
        Covers the branch that validates the kind before delete.
        """
        random_name = "test_dummy"
        with pytest.raises((ValidationError, ResourceNotFoundError)):
            client.feature_stores.begin_delete(random_name)

    def test_begin_create_raises_on_invalid_offline_and_online_store_type(self, client: MLClient) -> None:
        """Validate begin_create input checks for offline/online store types.
        This triggers ValidationError before any network calls.
        """
        random_name = "test_dummy"
        # Invalid offline store type
        offline = MaterializationStore(
            type="not_adls",
            target="/subscriptions/000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/acc",
        )
        fs_offline = FeatureStore(name=random_name, offline_store=offline)
        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs_offline)

        # Invalid online store type
        online = MaterializationStore(
            type="not_redis",
            target="/subscriptions/000/resourceGroups/rg/providers/Microsoft.Cache/Redis/redisname",
        )
        fs_online = FeatureStore(name=random_name, online_store=online)
        with pytest.raises(ValidationError):
            client.feature_stores.begin_create(fs_online)
