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
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_adlsgen1_folder/versions/1",
            type=AssetTypes.URI_FOLDER,
        ),
        cosmos_folder_dup=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_gen2_folder/versions/1",
            type=AssetTypes.URI_FOLDER,
        ),
    )

    pipeline.outputs.merged_blob.path = "azureml://datastores/workspaceblobstore/paths/azureml/dtv2_merge_dest/"
    pipeline.settings.default_compute = "adftest"
    return pipeline


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    cosmos_folder = Input(
        path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_adlsgen1_folder/versions/1",
        type=AssetTypes.URI_FOLDER,
    )
    cosmos_folder_dup = Input(
        path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_gen2_folder/versions/1",
        type=AssetTypes.URI_FOLDER,
    )

    inputs = {
        "folder1": cosmos_folder,
        "folder2": cosmos_folder_dup,
    }
    outputs = {"output_folder": Output(type=AssetTypes.URI_FOLDER, path="azureml://datastores/workspaceblobstore/paths/azureml/dtv2_merge_dest/")}

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
    pipeline.outputs.merged_blob.path = "azureml://datastores/workspaceblobstore/paths/azureml/dtv2_merge_dest/"
    pipeline.settings.default_compute = "adftest"
    return pipeline


def generate_dsl_pipeline_copy_mixtype_from_yaml() -> PipelineJob:
    merge_files_func = load_component(parent_dir + "/merge_mixtype_files.yaml")

    @dsl.pipeline(description="submit a pipeline with data transfer copy job")
    def data_transfer_copy_pipeline_from_yaml(input1, input2, input3):
        merge_files = merge_files_func(input1=input1, input2=input2, input3=input3)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_yaml(
        input1=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_adlsgen1_folder/versions/1",
            type=AssetTypes.URI_FILE,
        ),
        input2=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_test_file/versions/1",
            type=AssetTypes.URI_FILE,
        ),
        input3=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_mltable/versions/1",
            type=AssetTypes.MLTABLE,
        ),
    )

    pipeline.outputs.merged_blob.path = "azureml://datastores/workspaceblobstore/paths/azureml/dtv2_merge_dest2/"
    pipeline.settings.default_compute = "adftest"
    return pipeline


def generate_dsl_pipeline_copy_urifile_from_yaml() -> PipelineJob:
    merge_files_func = load_component(parent_dir + "/copy_uri_files.yaml")

    @dsl.pipeline(description="submit a pipeline with data transfer copy job")
    def data_transfer_copy_pipeline_from_yaml(input1):
        merge_files = merge_files_func(input1=input1)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_yaml(
        input1=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_asset_uriFile/versions/1",
            type=AssetTypes.URI_FILE,
        ),
    )

    # pipeline.outputs.merged_blob.path will convert type to uri_folder, has a bug to track this: 2104275
    pipeline.outputs.merged_blob = Output(
        type=AssetTypes.URI_FILE,
        path="azureml://datastores/testadlsgen2datastore/paths/dtv2_parquet_dest/my.parquet")
    pipeline.settings.default_compute = "adftest"
    return pipeline


def generate_dsl_pipeline_copy_urifolder_from_yaml() -> PipelineJob:
    merge_files_func = load_component(parent_dir + "/copy_files.yaml")

    @dsl.pipeline(description="submit a pipeline with data transfer copy job")
    def data_transfer_copy_pipeline_from_yaml(input1):
        merge_files = merge_files_func(input1=input1)
        return {"merged_blob": merge_files.outputs.output_folder}

    pipeline = data_transfer_copy_pipeline_from_yaml(
        input1=Input(
            path="azureml://locations/centraluseuap/workspaces/80eaba04-c6ec-4775-8ddc-d538e9642c2d/data/dtv2_asset_uriFolder/versions/1",
            type=AssetTypes.URI_FOLDER,
        ),
    )

    # pipeline.outputs.merged_blob.path will convert type to uri_folder, has a bug to track this: 2104275
    pipeline.outputs.merged_blob.path = "azureml://datastores/workspaceblobstore/paths/azureml/dtv2_dest/"
    pipeline.settings.default_compute = "adftest"
    return pipeline
