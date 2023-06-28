from pathlib import Path

from azure.ai.ml import Input, dsl
from azure.ai.ml.data_transfer import export_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    path_source_s3 = "s3://my_bucket/my_folder"
    connection_target = "azureml:my_s3_connection"

    my_cosmos_folder = Input(
        type=AssetTypes.URI_FOLDER,
        path="azureml://datastores/my_cosmos/paths/source_cosmos",
    )
    inputs = {"source": my_cosmos_folder}
    sink = {
        "type": "file_system",
        "connection": connection_target,
        "path": path_source_s3,
    }

    @dsl.pipeline(description="submit a pipeline with data transfer export file system job")
    def data_transfer_export_file_system_pipeline_from_builder(path_source_s3, connection_target, cosmos_folder):
        from azure.ai.ml.data_transfer import FileSystem

        s3_blob_input = export_data(inputs=inputs, sink=sink)

        source_snowflake = FileSystem(path=path_source_s3, connection=connection_target)
        s3_blob = export_data(inputs={"source": cosmos_folder}, sink=source_snowflake)

    pipeline = data_transfer_export_file_system_pipeline_from_builder(
        path_source_s3, connection_target, my_cosmos_folder
    )
    pipeline.settings.default_compute = "serverless"
    return pipeline
