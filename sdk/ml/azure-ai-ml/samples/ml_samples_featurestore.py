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

        featurestore_subscription_id = os.environ["AZUREML_ARM_SUBSCRIPTION"]
        featurestore_resource_group_name = os.environ["AZUREML_ARM_RESOURCEGROUP"]
        credential = DefaultAzureCredential()

        ml_client = MLClient(
            credential=credential,
            subscription_id=featurestore_subscription_id,
            resource_group_name=featurestore_resource_group_name,
        )

        # [START create_feature_store]
        from azure.ai.ml.entities import FeatureStore

        featurestore_name = "my-featurestore"
        featurestore_location = "eastus"
        featurestore = FeatureStore(name=featurestore_name, location=featurestore_location)

        # wait for featurestore creation
        fs_poller = ml_client.feature_stores.begin_create(fs, update_dependent_resources=True)
        print(fs_poller.result())
        # [END create_feature_store]

        featurestore_client = MLClient(
            credential=credential,
            subscription_id=featurestore_subscription_id,
            resource_group_name=featurestore_resource_group_name,
            workspace_name=featurestore_name,
        )

        # [START configure_feature_store_entity]
        from azure.ai.ml.entities import DataColumn, DataColumnType, FeatureStoreEntity

        account_entity_config = FeatureStoreEntity(
            name="account",
            version="1",
            index_columns=[DataColumn(name="accountID", type=DataColumnType.STRING)],
            stage="Development",
            description="This entity represents user account index key accountID.",
            tags={"data_type": "nonPII"},
        )

        # wait for featurestore entity creation
        fs_entity_poller = featurestore_client.feature_store_entities.begin_create_or_update(account_entity_config)
        print(fs_entity_poller.result())
        # [END configure_feature_store_entity]

        # [START configure_feature_set]
        from azure.ai.ml.entities import FeatureSetSpecification
        from azure.ai.ml.entities import FeatureSet

        transaction_fset_config = FeatureSet(
            name="transactions",
            version="1",
            description="7-day and 3-day rolling aggregation of transactions featureset",
            entities=["azureml:account:1"],
            stage="Development",
            specification=FeatureSetSpecification(path="<path-to-feature-set-spec-yaml>"),
            tags={"data_type": "nonPII"},
        )
        feature_set_poller = featurestore_client.feature_sets.begin_create_or_update(transaction_fset_config)
        print(feature_set_poller.result())
        # [END configure_feature_set]
        


if __name__ == "__main__":
    sample = FeatureStoreConfigurationOptions()
    sample.feature_store()
