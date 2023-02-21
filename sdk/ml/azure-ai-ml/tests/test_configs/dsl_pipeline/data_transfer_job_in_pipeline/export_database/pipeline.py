from pathlib import Path

from azure.ai.ml import Input, dsl
from azure.ai.ml.data_transfer import export_data
from azure.ai.ml.constants._common import AssetTypes, SERVERLESS_COMPUTE
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    connection_target_azuresql = "azureml:my_export_azuresqldb_connection"
    table_name = "dbo.Persons"
    my_cosmos_folder = Input(type=AssetTypes.URI_FILE, path=parent_dir + "/data/testFile_ForSqlDB.parquet")
    inputs = {"source": my_cosmos_folder}
    sink = {"type": "database", "connection": connection_target_azuresql, "table_name": table_name}

    @dsl.pipeline(description="submit a pipeline with data transfer export database job")
    def data_transfer_export_database_pipeline_from_builder(table_name, connection_target_azuresql, cosmos_folder):
        from azure.ai.ml.data_transfer import Database

        blob_azuresql_node_input = export_data(inputs=inputs, sink=sink)

        source_snowflake = Database(table_name=table_name, connection=connection_target_azuresql)
        blob_azuresql = export_data(inputs={"source": cosmos_folder}, sink=source_snowflake)

    pipeline = data_transfer_export_database_pipeline_from_builder(
        table_name, connection_target_azuresql, my_cosmos_folder
    )
    pipeline.settings.default_compute = SERVERLESS_COMPUTE
    return pipeline
