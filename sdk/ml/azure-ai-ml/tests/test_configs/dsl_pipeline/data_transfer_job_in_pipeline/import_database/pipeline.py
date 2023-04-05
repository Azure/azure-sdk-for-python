from pathlib import Path

from azure.ai.ml import Output, dsl
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.constants._common import AssetTypes, SERVERLESS_COMPUTE
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    query_source_snowflake = "select * from TPCH_SF1000.PARTSUPP limit 10"
    connection_target_azuresql = "azureml:my_snowflake_connection"
    outputs = {
        "sink": Output(
            type=AssetTypes.MLTABLE,
            path="azureml://datastores/workspaceblobstore_sas/paths/importjob/${{name}}/output_dir/snowflake/",
        )
    }
    source = {"connection": connection_target_azuresql, "query": query_source_snowflake}

    @dsl.pipeline(description="submit a pipeline with data transfer import database job")
    def data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql):
        from azure.ai.ml.data_transfer import Database

        snowflake_blob_node_input = import_data(
            source=Database(**source),
            outputs=outputs,
        )

        source_snowflake = Database(query=query_source_snowflake, connection=connection_target_azuresql)
        snowflake_blob = import_data(
            source=source_snowflake,
            outputs=outputs,
        )

    pipeline = data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql)
    pipeline.settings.default_compute = SERVERLESS_COMPUTE
    return pipeline


def generate_dsl_pipeline_from_builder_sql() -> PipelineJob:
    query_source_snowflake = "select top(10) Name from SalesLT.ProductCategory"
    connection_target_azuresql = "azureml:my_azuresqldb_connection"
    outputs = {"sink": Output(type=AssetTypes.MLTABLE)}
    source = {"connection": connection_target_azuresql, "query": query_source_snowflake}

    @dsl.pipeline(description="submit a pipeline with data transfer import database job")
    def data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql):
        from azure.ai.ml.data_transfer import Database

        sql_blob_node_input = import_data(
            source=Database(**source),
            outputs=outputs,
        )

        source_snowflake = Database(query=query_source_snowflake, connection=connection_target_azuresql)
        sql_blob = import_data(
            source=source_snowflake,
            outputs=outputs,
        )

    pipeline = data_transfer_import_database_pipeline_from_builder(query_source_snowflake, connection_target_azuresql)
    pipeline.settings.default_compute = SERVERLESS_COMPUTE
    return pipeline
