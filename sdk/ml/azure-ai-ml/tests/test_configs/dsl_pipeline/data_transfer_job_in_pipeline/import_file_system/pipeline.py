from pathlib import Path

from azure.ai.ml import Output, dsl
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    path_source_s3 = 's3://my_bucket/my_folder'
    connection_target = 'azureml:my_s3_connection'
    outputs = {"sink": Output(type=AssetTypes.URI_FOLDER, path="azureml://datastores/managed/paths/some_path")}
    source = {'type': 'file_system', 'connection': connection_target, 'path': path_source_s3}

    # DataTransferImport from import_data() function
    data_transfer_function = import_data(
        source=source,
        outputs=outputs,
        task=DataTransferTaskType.IMPORT_DATA,
    )

    @dsl.pipeline(description='submit a pipeline with data transfer import file system job')
    def data_transfer_import_file_system_pipeline_from_builder(path_source_s3, connection_target):
        from azure.ai.ml.data_transfer import FileSystem
        s3_blob_input = data_transfer_function(source=FileSystem(**source))

        source_snowflake = FileSystem(path=path_source_s3, connection=connection_target)
        s3_blob = data_transfer_function(source=source_snowflake)

    pipeline = data_transfer_import_file_system_pipeline_from_builder(path_source_s3, connection_target)
    pipeline.settings.default_compute = "adf_compute"
    return pipeline
