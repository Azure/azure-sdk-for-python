# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_featurestore.py
DESCRIPTION:
    These samples demonstrate different ways to configure Feature Store and related resources.
USAGE:
    python ml_samples_featurestore.py

"""

import os


class FeatureStoreConfigurationOptions(object):
    def feature_store(self):
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.environ["AZUREML_ARM_SUBSCRIPTION"]
        resource_group = os.environ["AZUREML_ARM_RESOURCEGROUP"]
        storage_account_name = "<FEATURE_STORAGE_ACCOUNT_NAME>"
        storage_file_system_name = "offlinestore"
        redis_cache_name = "onlinestore"
        credential = DefaultAzureCredential()

        ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
        )

        # [START configure_feature_store_settings]
        from azure.ai.ml.entities import ComputeRuntime, FeatureStoreSettings

        offline_store_target = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account_name}/blobServices/default/containers/{storage_file_system_name}"

        online_store_target = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Cache/Redis/{redis_cache_name}"

        FeatureStoreSettings(
            compute_runtime=ComputeRuntime(spark_runtime_version="3.3.0"),
            offline_store_connection_name=offline_store_target,
            online_store_connection_name=online_store_target,
        )
        # [END configure_feature_store_settings]

        # [START create_feature_store]
        from azure.ai.ml.entities import FeatureStore

        featurestore_name = "my-featurestore"
        featurestore_location = "eastus"
        featurestore = FeatureStore(name=featurestore_name, location=featurestore_location)

        # wait for featurestore creation
        fs_poller = ml_client.feature_stores.begin_create(featurestore, update_dependent_resources=True)
        print(fs_poller.result())
        # [END create_feature_store]

        featurestore_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=featurestore_name,
        )

        # [START configure_feature_store_entity]
        from azure.ai.ml.entities import DataColumn, DataColumnType, FeatureStoreEntity

        account_column = DataColumn(name="accountID", type=DataColumnType.STRING)

        account_entity_config = FeatureStoreEntity(
            name="account",
            version="1",
            index_columns=[account_column],
            stage="Development",
            description="This entity represents user account index key accountID.",
            tags={"data_type": "nonPII"},
        )

        # wait for featurestore entity creation
        fs_entity_poller = featurestore_client.feature_store_entities.begin_create_or_update(account_entity_config)
        print(fs_entity_poller.result())
        # [END configure_feature_store_entity]

        # [START configure_feature_set]
        from azure.ai.ml.entities import FeatureSet, FeatureSetSpecification

        transaction_fset_config = FeatureSet(
            name="transactions",
            version="1",
            description="7-day and 3-day rolling aggregation of transactions featureset",
            entities=["azureml:account:1"],
            stage="Development",
            specification=FeatureSetSpecification(path="../azure-ai-ml/tests/test_configs/feature_set/code_sample/"),
            tags={"data_type": "nonPII"},
        )

        feature_set_poller = featurestore_client.feature_sets.begin_create_or_update(transaction_fset_config)
        print(feature_set_poller.result())
        # [END configure_feature_set]

        # [START configure_materialization_store]
        from azure.ai.ml.entities import ManagedIdentityConfiguration, MaterializationStore

        gen2_container_arm_id = "/subscriptions/{sub_id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account}/blobServices/default/containers/{container}".format(
            sub_id=subscription_id,
            rg=resource_group,
            account=storage_account_name,
            container=storage_file_system_name,
        )

        offline_store = MaterializationStore(
            type="azure_data_lake_gen2",
            target=gen2_container_arm_id,
        )

        # Must define materialization identity when defining offline/online store.
        fs = FeatureStore(
            name=featurestore_name,
            offline_store=offline_store,
            materialization_identity=ManagedIdentityConfiguration(
                client_id="<YOUR-UAI-CLIENT-ID>",
                resource_id="<YOUR-UAI-RESOURCE-ID>",
                principal_id="<YOUR-UAI-PRINCIPAL-ID>",
            ),
        )
        # [END configure_materialization_store]

        # Clean up created feature store for sample
        ml_client.feature_stores.begin_delete(featurestore.name, delete_dependent_resources=True)


if __name__ == "__main__":
    sample = FeatureStoreConfigurationOptions()
    sample.feature_store()
