# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for feature-store + data-import entities."""
from azure.ai.ml.data_transfer import Database
from azure.ai.ml.entities import DataImport, FeatureSet, FeatureStoreEntity
from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification
from azure.ai.ml.entities._feature_store_entity.data_column import DataColumn
from azure.ai.ml.entities._feature_store_entity.data_column_type import DataColumnType

_ENTITY_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/smoke-rg/providers"
    "/Microsoft.MachineLearningServices/workspaces/smoke-ws/featurestoreEntities/smoke-entity/versions/1"
)


def build_feature_set():
    """FeatureSet with a spec path, entity reference and stage."""
    return FeatureSet(
        name="smoke-feature-set",
        version="1",
        description="smoke feature set",
        tags={"tag1": "value1"},
        entities=[_ENTITY_ID],
        stage="Development",
        specification=FeatureSetSpecification(path="azureml://datastores/workspaceblobstore/paths/smoke/spec/"),
    )


def build_feature_store_entity():
    """FeatureStoreEntity with index columns."""
    return FeatureStoreEntity(
        name="smoke-feature-store-entity",
        version="1",
        description="smoke feature store entity",
        tags={"tag1": "value1"},
        stage="Development",
        index_columns=[
            DataColumn(name="customer_id", type=DataColumnType.STRING),
            DataColumn(name="region_id", type=DataColumnType.INTEGER),
        ],
    )


def build_data_import_database():
    """DataImport from a database source."""
    return DataImport(
        name="smoke-data-import",
        description="smoke data import",
        tags={"tag1": "value1"},
        path="azureml://datastores/workspaceblobstore/paths/smoke/imported/",
        source=Database(query="SELECT * FROM my_table", connection="azureml:my_connection"),
    )


FEATURE_SET_BUILDERS = {
    "feature_set": build_feature_set,
}

FEATURE_STORE_ENTITY_BUILDERS = {
    "feature_store_entity": build_feature_store_entity,
}

DATA_IMPORT_BUILDERS = {
    "data_import_database": build_data_import_database,
}
