from azure.ai.ml import dsl, Input
from azure.ai.ml.entities import load_component
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(
        yaml_file=parent_dir + "/component.yml"
    )

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Component with inputs and outputs",
    )
    def component_with_input_output(
            pipeline_sample_input_data,
            pipeline_sample_input_string,
    ):
        hello_python_world_job = basic_func(
            sample_input_data=pipeline_sample_input_data, sample_input_string=pipeline_sample_input_string
        )
        hello_python_world_job.compute = "cpu-cluster"
        return {"pipeline_sample_output_data": hello_python_world_job.outputs.sample_output_data}

    pipeline = component_with_input_output(
        Input(type='uri_file', path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"),
        "Hello_Pipeline_World",
    )
    pipeline.outputs.pipeline_sample_output_data.mode = "upload"
    return pipeline
