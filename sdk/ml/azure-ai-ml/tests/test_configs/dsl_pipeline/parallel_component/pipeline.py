from azure.ai.ml import dsl, Input, load_component
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    get_data = load_component(path=parent_dir + "/get_data.yml")

    file_batch_inference = load_component(path=parent_dir + "/file_batch_inference.yml")
    file_batch_inference_duplicate = load_component(path=parent_dir + "/file_batch_inference.yml")
    tabular_batch_inference = load_component(path=parent_dir + "/tabular_batch_inference.yml")
    convert_data = load_component(path=parent_dir + "/convert_data.yml")

    # Construct pipeline
    @dsl.pipeline(default_compute="cpu-cluster")
    def parallel_in_pipeline(pipeline_job_data_path, pipeline_score_model):
        get_data_node = get_data(input_data=pipeline_job_data_path)
        get_data_node.outputs.file_output_data.type = AssetTypes.MLTABLE
        get_data_node.outputs.tabular_output_data.type = AssetTypes.MLTABLE

        file_batch_inference_node = file_batch_inference(job_data_path=get_data_node.outputs.file_output_data)
        file_batch_inference_node.inputs.job_data_path.mode = InputOutputModes.EVAL_MOUNT

        convert_data_node = convert_data(input_data=file_batch_inference_node.outputs.job_output_path)
        convert_data_node.outputs.file_output_data.type = AssetTypes.MLTABLE

        file_batch_inference_duplicate_node = file_batch_inference_duplicate(
            job_data_path=convert_data_node.outputs.file_output_data
        )
        file_batch_inference_duplicate_node.inputs.job_data_path.mode = InputOutputModes.EVAL_MOUNT

        tabular_batch_inference_node = tabular_batch_inference(
            job_data_path=get_data_node.outputs.tabular_output_data, score_model=pipeline_score_model
        )
        tabular_batch_inference_node.inputs.job_data_path.mode = InputOutputModes.DIRECT

        return {
            "pipeline_job_out_file": file_batch_inference_duplicate_node.outputs.job_output_path,
            "pipeline_job_out_tabular": tabular_batch_inference_node.outputs.job_out_path,
        }

    pipeline = parallel_in_pipeline(
        pipeline_job_data_path=Input(
            type=AssetTypes.MLTABLE, path=parent_dir + "/dataset/", mode=InputOutputModes.RO_MOUNT
        ),
        pipeline_score_model=Input(
            path=parent_dir + "/model/", type=AssetTypes.URI_FOLDER, mode=InputOutputModes.DOWNLOAD
        ),
    )
    pipeline.outputs.pipeline_job_out_file.mode = "upload"
    pipeline.outputs.pipeline_job_out_tabular.type = "uri_file"

    return pipeline
