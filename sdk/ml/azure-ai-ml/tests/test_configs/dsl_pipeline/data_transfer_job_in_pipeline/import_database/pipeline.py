from pathlib import Path

from azure.ai.ml import Output, dsl
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    query_source_snowflake = 'SELECT * FROM my_table'
    connection_target_azuresql = 'azureml:my_azuresql_connection'
    outputs = {"sink": Output(type=AssetTypes.MLTABLE)}
    source = {'type': 'database', 'connection': 'azureml:my_snowflake_connection',
              'query': query_source_snowflake}

    # DataTransferImport from import_data() function
    data_transfer_function = import_data(
        source=source,
        outputs=outputs,
        task=DataTransferTaskType.IMPORT_DATA,
    )

    @dsl.pipeline(description='submit a pipeline with data transfer import database job')
    def data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql):
        from azure.ai.ml.data_transfer import Database
        snowflake_blob_node_input = data_transfer_function(source=Database(**source))

        source_snowflake = Database(query=query_source_snowflake, connection=connection_target_azuresql)
        snowflake_blob = data_transfer_function(source=source_snowflake)

    pipeline = data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql)
    pipeline.settings.default_compute = "adf_compute"
    return pipeline
