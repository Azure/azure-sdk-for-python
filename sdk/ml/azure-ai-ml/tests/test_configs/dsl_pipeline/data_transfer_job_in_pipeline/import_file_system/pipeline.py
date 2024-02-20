from pathlib import Path

from azure.ai.ml import Output, dsl
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.constants._common import AssetTypes, SERVERLESS_COMPUTE
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    path_source_s3 = "test1/*"
    connection_target = "azureml:my-s3-connection"
    outputs = {"sink": Output(type=AssetTypes.URI_FOLDER)}
    source = {"type": "file_system", "connection": connection_target, "path": path_source_s3}

    @dsl.pipeline(description="submit a pipeline with data transfer import file system job")
    def data_transfer_import_file_system_pipeline_from_builder(path_source_s3, connection_target):
        from azure.ai.ml.data_transfer import FileSystem

        s3_blob_input = import_data(source=source, outputs=outputs)

        source_snowflake = FileSystem(path=path_source_s3, connection=connection_target)
        s3_blob = import_data(source=source_snowflake, outputs=outputs)

    pipeline = data_transfer_import_file_system_pipeline_from_builder(path_source_s3, connection_target)
    pipeline.settings.default_compute = SERVERLESS_COMPUTE
    return pipeline
