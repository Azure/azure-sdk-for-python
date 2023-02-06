from pathlib import Path

from azure.ai.ml import Input, Output, dsl, load_component
from azure.ai.ml.data_transfer import import_data, export_data
from azure.ai.ml.data_transfer import Database, FileSystem
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    path_source_s3 = 's3://my_bucket/my_folder'
    query_source_snowflake = 'SELECT * FROM my_table'
    connection_target_s3 = 'azureml:my_s3_connection'
    inputs = {"source": Input(type=AssetTypes.URI_FOLDER)}

    # DataTransferImport from import_data() function
    snowflake_blob_func = import_data(
        source={'type': 'database', 'connection': 'azureml:my_snowflake_connection', 'query': query_source_snowflake},
        outputs={"sink": Output(type=AssetTypes.MLTABLE)},
        task=DataTransferTaskType.IMPORT_DATA,
    )

    s3_blob_func = import_data(
        source={'type': 'file_system', 'connection': connection_target_s3, 'path': path_source_s3},
        outputs={"sink": Output(type=AssetTypes.URI_FOLDER)},
        task=DataTransferTaskType.IMPORT_DATA,
    )

    merge_files_func = load_component(parent_dir + "/copy_data/merge_files.yaml")

    # DataTransferExport from export_data() function
    blob_s3_func = export_data(
        inputs=inputs,
        sink = {'type': 'file_system', 'connection': connection_target_s3, 'path': path_source_s3},
        task=DataTransferTaskType.EXPORT_DATA,
    )

    @dsl.pipeline(description="submit a pipeline with data transfer job")
    def data_transfer_copy_pipeline_from_yaml(query_source_snowflake, path_source_s3, connection_target_s3):
        source_snowflake = Database(query=query_source_snowflake, connection='azureml:my_snowflake_connection')
        snowflake_blob = snowflake_blob_func(source=source_snowflake)
        snowflake_blob.compute = 'adf_compute1'

        source_s3= FileSystem(path=path_source_s3, connection="azureml:my_s3_connection")
        s3_blob = s3_blob_func(source=source_s3)

        merge_files = merge_files_func(folder1=s3_blob.outputs.sink, folder2=snowflake_blob.outputs.sink)

        sink_s3 = FileSystem(path=path_source_s3, connection=connection_target_s3)
        blob_s3 = blob_s3_func(source=merge_files.outputs.output_folder)
        blob_s3.sink = sink_s3

        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_yaml(
        query_source_snowflake=query_source_snowflake,
        path_source_s3=path_source_s3,
        connection_target_s3=connection_target_s3,
        )
    pipeline.outputs.merged_blob.path = "azureml://datastores/my_blob/paths/merged_blob"

    pipeline.settings.default_compute = "adf_compute"
    return pipeline
