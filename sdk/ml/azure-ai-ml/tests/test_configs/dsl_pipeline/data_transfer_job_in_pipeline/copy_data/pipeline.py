from pathlib import Path

from azure.ai.ml import Input, Output, dsl, load_component
from azure.ai.ml.data_transfer import copy_data
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import DataTransferTaskType, DataCopyMode
from azure.ai.ml.entities import PipelineJob


parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline_from_yaml() -> PipelineJob:
    merge_files_func = load_component(parent_dir + "/merge_files.yaml")

    @dsl.pipeline(description="submit a pipeline with data transfer copy job")
    def data_transfer_copy_pipeline_from_yaml(cosmos_folder, cosmos_folder_dup):
        merge_files = merge_files_func(folder1=cosmos_folder, folder2=cosmos_folder_dup)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_yaml(
        cosmos_folder=Input(
            path="azureml://datastores/my_cosmos/paths/source_cosmos",
            type=AssetTypes.URI_FOLDER,
        ),
        cosmos_folder_dup=Input(
            path="azureml://datastores/my_cosmos/paths/source_cosmos",
            type=AssetTypes.URI_FOLDER,
        ),
    )

    pipeline.outputs.merged_blob.path = "azureml://datastores/my_blob/paths/merged_blob"
    pipeline.settings.default_compute = "adf_compute"
    return pipeline


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    cosmos_folder = Input(
        path="azureml://datastores/my_cosmos/paths/source_cosmos",
        type=AssetTypes.URI_FOLDER,
    )
    cosmos_folder_dup = Input(
        path="azureml://datastores/my_cosmos/paths/source_cosmos",
        type=AssetTypes.URI_FOLDER,
    )

    inputs = {
        "folder1": cosmos_folder,
        "folder2": cosmos_folder_dup,
    }
    outputs = {"output_folder": Output(type=AssetTypes.URI_FOLDER, path="azureml://datastores/my_blob/paths/merged_blob")}

    merge_files_func = copy_data(
        inputs=inputs,
        outputs=outputs,
        task=DataTransferTaskType.COPY_DATA,
        data_copy_mode=DataCopyMode.MERGE_WITH_OVERWRITE,
    )

    # Define pipeline
    @dsl.pipeline(description="submit a pipeline with data transfer copy job")
    def data_transfer_copy_pipeline_from_builder(cosmos_folder, cosmos_folder_dup):
        merge_files = merge_files_func(folder1=cosmos_folder, folder2=cosmos_folder_dup)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_builder(
        cosmos_folder=cosmos_folder,
        cosmos_folder_dup=cosmos_folder_dup
    )
    pipeline.outputs.merged_blob.path = "azureml://datastores/my_blob/paths/merged_blob"
    pipeline.settings.default_compute = "adf_compute"
    return pipeline
