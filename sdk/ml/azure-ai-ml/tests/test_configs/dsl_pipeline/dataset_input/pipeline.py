from pathlib import Path

from azure.ai.ml import Input, MLClient, dsl, load_component, load_data
from azure.ai.ml.entities import Data, PipelineJob
from azure.core.exceptions import ResourceNotFoundError

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline(client: MLClient) -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(source=parent_dir + "/component.yml")

    try:
        _ = client.data.get(name="sampledata1235", version="2")
    except ResourceNotFoundError:
        # Create the data version if not exits
        data = load_data(source=parent_dir + "/data.yml")
        _ = client.data.create_or_update(data)

    data_input = Input(type="uri_file", path="azureml:sampledata1235:2")
    mltable_input = Input(type="mltable", path="azureml:sampledata1235:2", mode="eval_mount")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Example of using data from a Dataset as pipeline input",
    )
    def dataset_input(
        pipeline_sample_input_data,
        pipeline_sample_input_string,
    ):
        hello_python_world_job = basic_func(
            sample_input_data=pipeline_sample_input_data,
            sample_input_string=pipeline_sample_input_string,
        )
        hello_python_world_job.compute = "cpu-cluster"

        mltable_job = basic_func(
            sample_input_data=mltable_input,
            sample_input_string=pipeline_sample_input_string,
        )
        mltable_job.compute = "cpu-cluster"

        return {
            "pipeline_sample_output_data": hello_python_world_job.outputs.sample_output_data,
        }

    pipeline = dataset_input(data_input, "Hello_Pipeline_World")
    pipeline.outputs.pipeline_sample_output_data.mode = "upload"
    return pipeline
