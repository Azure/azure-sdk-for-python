from pathlib import Path

from azure.ai.ml import Input, dsl, load_component
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(source=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Example of using a file hosted at a web URL as pipeline input",
    )
    def web_url_input(
        pipeline_sample_input_data,
        pipeline_sample_input_string,
    ):
        hello_python_world_job = basic_func(
            sample_input_data=pipeline_sample_input_data,
            sample_input_string=pipeline_sample_input_string,
        )
        hello_python_world_job.compute = "cpu-cluster"
        return {
            "pipeline_sample_output_data": hello_python_world_job.outputs.sample_output_data,
        }

    pipeline = web_url_input(
        Input(path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv", type="uri_file"),
        "Hello_Pipeline_World",
    )
    return pipeline
