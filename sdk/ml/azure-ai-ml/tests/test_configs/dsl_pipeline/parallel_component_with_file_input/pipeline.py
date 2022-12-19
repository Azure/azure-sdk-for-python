from pathlib import Path

from azure.ai.ml import Input, dsl, load_component
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    file_batch_inference = load_component(source=parent_dir + "/score.yml")
    file_batch_inference_duplicate = load_component(source=parent_dir + "/score.yml")
    convert_data = load_component(source=parent_dir + "/convert_data.yml")
    # Construct pipeline

    @dsl.pipeline(compute="cpu-cluster")
    def parallel_in_pipeline(pipeline_job_data_path):
        file_batch_inference_node = file_batch_inference(job_data_path=pipeline_job_data_path)
        file_batch_inference_node.compute = "cpu-cluster"

        convert_data_node = convert_data(input_data=file_batch_inference_node.outputs.job_output_path)
        convert_data_node.outputs.file_output_data.type = AssetTypes.MLTABLE

        file_batch_inference_duplicate_node = file_batch_inference_duplicate(
            job_data_path=convert_data_node.outputs.file_output_data
        )
        file_batch_inference_duplicate_node.inputs.job_data_path.mode = InputOutputModes.EVAL_MOUNT

        file_batch_inference_duplicate_node.compute = "cpu-cluster"

        return {
            "pipeline_job_out_path": file_batch_inference_duplicate_node.outputs.job_output_path,
        }

    pipeline = parallel_in_pipeline(
        pipeline_job_data_path=Input(
            type=AssetTypes.MLTABLE,
            path=parent_dir + "/dataset/mnist-data/",
            mode=InputOutputModes.EVAL_MOUNT,
        ),
    )

    pipeline.outputs.pipeline_job_out_path.mode = "upload"
    return pipeline
