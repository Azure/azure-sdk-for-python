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
        featurestore_name = "my-featurestore"
        featurestore_location = "eastus"
        featurestore_subscription_id = os.environ["AZUREML_ARM_SUBSCRIPTION"]
        featurestore_resource_group_name = os.environ["AZUREML_ARM_RESOURCEGROUP"]
        credential = DefaultAzureCredential()

        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential
        from azure.ai.ml.entities import FeatureStore

        ml_client = MLClient(
            credential=credential,
            subscription_id=featurestore_subscription_id,
            resource_group_name=featurestore_resource_group_name,
        )

        featurestore = FeatureStore(name=featurestore_name, location=featurestore_location)
        
        # wait for featurestore creation
        # ml_client.feature_stores.begin_create(featurestore, update_dependent_resources=True)



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
        # [END configure_feature_set]
        


if __name__ == "__main__":
    sample = FeatureStoreConfigurationOptions()
    sample.feature_store()
