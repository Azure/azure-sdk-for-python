from pathlib import Path

from azure.ai.ml import Input, dsl, load_component
from azure.ai.ml.constants._common import AssetTypes, InputOutputModes
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    batch_inference1 = load_component(source=parent_dir + "/tabular_input_e2e.yml")

    # Construct pipeline
    @dsl.pipeline(default_compute="cpu-cluster")
    def parallel_in_pipeline(pipeline_job_data_path, pipeline_score_model):
        batch_inference_node1 = batch_inference1(job_data_path=pipeline_job_data_path, score_model=pipeline_score_model)
        batch_inference_node1.compute = "cpu-cluster"
        batch_inference_node1.logging_level = "DEBUG"

        return {
            "pipeline_job_out_path": batch_inference_node1.outputs.job_out_path,
        }

    pipeline = parallel_in_pipeline(
        pipeline_job_data_path=Input(
            type=AssetTypes.MLTABLE, path=parent_dir + "/dataset/iris-mltable/", mode=InputOutputModes.DIRECT
        ),
        pipeline_score_model=Input(
            path=parent_dir + "/model/", type=AssetTypes.URI_FOLDER, mode=InputOutputModes.DOWNLOAD
        ),
    )

    pipeline.outputs.pipeline_job_out_path.type = AssetTypes.URI_FILE
    pipeline.outputs.pipeline_job_out_path.mode = InputOutputModes.RW_MOUNT
    return pipeline
