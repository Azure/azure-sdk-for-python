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
        compute="cpu-cluster",
        description="Example of using data folder from a Workspace Datastore as pipeline input",
    )
    def datastore_datapath_uri_folder(
            pipeline_sample_input_data,
            pipeline_sample_input_string,
    ):
        hello_python_world_job = basic_func(
            sample_input_data=pipeline_sample_input_data,
            sample_input_string=pipeline_sample_input_string,
        )
        return {
            "pipeline_sample_output_data": hello_python_world_job.outputs.sample_output_data,
        }

    pipeline = datastore_datapath_uri_folder(
        Input(
            type="uri_folder",
            path="azureml://datastores/workspaceblobstore/paths/LocalUpload"
                                   "/cec6841f346975cde1ee7d5289c5559f/data",
            mode="download"
        ),
        "Hello_Pipeline_World")
    pipeline.inputs.pipeline_sample_input_data.mode = "download"
    pipeline.outputs.pipeline_sample_output_data.mode = "upload"
    return pipeline
