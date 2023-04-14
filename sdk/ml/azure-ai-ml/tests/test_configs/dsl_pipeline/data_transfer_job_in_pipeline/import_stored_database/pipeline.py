from pathlib import Path

from azure.ai.ml import Output, dsl
from azure.ai.ml.data_transfer import import_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    stored_procedure = "SelectEmployeeByJobAndDepartment"
    stored_procedure_params = [
        {"name": "job", "value": "Engineer", "type": "String"},
        {"name": "department", "value": "Engineering", "type": "String"},
    ]
    outputs = {"sink": Output(type=AssetTypes.MLTABLE)}
    source = {
        "connection": "azureml:my_sql_connection",
        "stored_procedure": stored_procedure,
        "stored_procedure_params": stored_procedure_params,
    }

    @dsl.pipeline(description="submit a pipeline with data transfer import stored database job")
    def data_transfer_import_database_pipeline_from_builder():
        from azure.ai.ml.data_transfer import Database

        snowflake_blob = import_data(
            source=Database(**source),
            outputs=outputs,
        )

    pipeline = data_transfer_import_database_pipeline_from_builder()
    pipeline.settings.default_compute = "serverless"
    return pipeline
