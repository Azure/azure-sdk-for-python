from pathlib import Path

from azure.ai.ml import Input, dsl
from azure.ai.ml.data_transfer import export_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    connection_target_azuresql = 'azureml:my_azuresql_connection'
    table_name = "merged_table"
    my_cosmos_folder = Input(type=AssetTypes.URI_FOLDER, path="azureml://datastores/my_cosmos/paths/source_cosmos")
    inputs = {"source": my_cosmos_folder}
    sink = {'type': 'database', 'connection': connection_target_azuresql, 'table_name': table_name}

    # DataTransferExport from export_data() function
    data_transfer_function = export_data(
        inputs=inputs,
        sink=sink,
        task=DataTransferTaskType.EXPORT_DATA,
    )

    @dsl.pipeline(description='submit a pipeline with data transfer export database job')
    def data_transfer_export_database_pipeline_from_builder(table_name, connection_target_azuresql, cosmos_folder):
        from azure.ai.ml.data_transfer import Database
        blob_azuresql_node_input = data_transfer_function(source=my_cosmos_folder)
        blob_azuresql_node_input.sink = sink

        source_snowflake = Database(table_name=table_name, connection=connection_target_azuresql)
        blob_azuresql = data_transfer_function(source=cosmos_folder)
        blob_azuresql.sink = source_snowflake

    pipeline = data_transfer_export_database_pipeline_from_builder(table_name, connection_target_azuresql, my_cosmos_folder)
    pipeline.settings.default_compute = "adf_compute"
    return pipeline
