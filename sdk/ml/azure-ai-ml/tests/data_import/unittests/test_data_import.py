import pytest

from azure.ai.ml import load_data
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.entities import DataImport
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem


@pytest.mark.unittest
@pytest.mark.data_import_test
class TestDataImport:
    def test_data_import_database(self):
        data_import1 = load_data(source="./tests/test_configs/data_import/data_import_database.yaml")
        data_import2 = DataImport(
            name="my_azuresqldb_asset",
            type="mltable",
            path="azureml://datastores/workspaceblobstore/paths/{name}",
            source=Database(query="select * from region", connection="azureml:my_azuresqldb_connection"),
        )

        assert isinstance(data_import1, DataImport)
        assert isinstance(data_import2, DataImport)
        assert data_import1.name == data_import2.name
        assert data_import1.type == data_import2.type
        assert data_import1.path == data_import2.path

        assert isinstance(data_import1.source, Database)
        assert isinstance(data_import2.source, Database)
        assert data_import1.source.type == data_import2.source.type
        assert data_import1.source.query == data_import2.source.query
        assert data_import1.source.connection == data_import2.source.connection

    def test_data_import_file_system(self):
        data_import = load_data(source="./tests/test_configs/data_import/data_import_file_system.yaml")
        import_job = import_data(
            source=FileSystem(path="test1/*", connection="azureml:my_s3_connection"),
            outputs={
                "sink": Output(
                    type="uri_folder", path="azureml://datastores/workspaceblobstore/paths/{name}", name="my_s3_asset"
                )
            },
        )

        assert isinstance(data_import, DataImport)
        assert data_import.name == import_job.outputs["sink"].name
        assert data_import.path == import_job.outputs["sink"].path

        assert isinstance(data_import.source, FileSystem)
        assert isinstance(import_job.source, FileSystem)
        assert data_import.source.type == import_job.source.type
        assert data_import.source.path == import_job.source.path
        assert data_import.source.connection == import_job.source.connection
