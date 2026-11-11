# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for data-import entities (smoke serialization suite).

``DataImport`` with ``Database``/``FileSystem`` sources are arm-absent models: the migration builds
their wire body hand (JSON-direct) rather than through a generated model, which is exactly the class of
change where an implicit serializer behavior can drift (see the distillation properties-bag finding).
This pins their request bodies byte-for-byte vs the pre-migration baseline. No mocking.
"""
from azure.ai.ml.entities._data_import.data_import import DataImport
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem


def build_data_import_database():
    """DataImport from a Database source (SQL query)."""
    return DataImport(
        name="smoke-data-import-db",
        path="azureml://datastores/workspaceblobstore/paths/smoke-import/",
        source=Database(
            query="SELECT * FROM smoke_table WHERE region = 'westus'",
            connection="azureml:smoke-sql-connection",
        ),
    )


def build_data_import_file_system():
    """DataImport from a FileSystem source (external S3-style path)."""
    return DataImport(
        name="smoke-data-import-fs",
        path="azureml://datastores/workspaceblobstore/paths/smoke-import-fs/",
        source=FileSystem(
            path="test1/*",
            connection="azureml:smoke-s3-connection",
        ),
    )


DATA_IMPORT_BUILDERS = {
    "data_import_database_entity": build_data_import_database,
    "data_import_file_system_entity": build_data_import_file_system,
}
