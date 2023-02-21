from pathlib import Path

from azure.ai.ml import Input, Output, dsl, load_component
from azure.ai.ml.data_transfer import import_data, export_data
from azure.ai.ml.data_transfer import Database, FileSystem
from azure.ai.ml.constants._common import AssetTypes, SERVERLESS_COMPUTE
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    path_source_s3 = "test1/*"
    query_source_sql = "select top(10) Name from SalesLT.ProductCategory"

    connection_target_azuresql = "azureml:my_export_azuresqldb_connection"
    table_name = "dbo.Persons"
    my_cosmos_folder = Input(
        type=AssetTypes.URI_FILE, path=parent_dir + "/export_database/data/testFile_ForSqlDB.parquet"
    )
    inputs = {"source": my_cosmos_folder}
    sink = {"type": "database", "connection": connection_target_azuresql, "table_name": table_name}

    merge_files_func = load_component(parent_dir + "/copy_data/merge_files.yaml")

    @dsl.pipeline(description="submit a pipeline with data transfer job")
    def data_transfer_pipeline_from_yaml(query_source_sql, path_source_s3):
        source_snowflake = Database(query=query_source_sql, connection="azureml:my_azuresqldb_connection")
        snowflake_blob = import_data(source=source_snowflake, outputs={"sink": Output(type=AssetTypes.MLTABLE)})

        source_s3 = FileSystem(path=path_source_s3, connection="azureml:my-s3-connection")
        s3_blob = import_data(source=source_s3, outputs={"sink": Output(type=AssetTypes.URI_FOLDER)})

        merge_files = merge_files_func(folder1=s3_blob.outputs.sink, folder2=snowflake_blob.outputs.sink)
        blob_azuresql = export_data(inputs=inputs, sink=sink)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_pipeline_from_yaml(
        query_source_sql=query_source_sql,
        path_source_s3=path_source_s3,
    )

    pipeline.settings.default_compute = SERVERLESS_COMPUTE
    return pipeline
