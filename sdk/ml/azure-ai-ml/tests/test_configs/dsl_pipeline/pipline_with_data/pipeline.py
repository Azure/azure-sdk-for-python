from azure.ai.ml import dsl, Input
from azure.ai.ml.entities import load_component
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    a_func = load_component(yaml_file=parent_dir + "/componentA.yml")
    b_func = load_component(yaml_file=parent_dir + "/componentB.yml")
    c_func = load_component(yaml_file=parent_dir + "/componentC.yml")

    # 2. Construct pipeline
    @dsl.pipeline(compute="cpu-cluster")
    def pipeline_with_data(pipeline_sample_input_data):
        component_a_job = a_func(componentA_input=pipeline_sample_input_data)
        component_b_job = b_func(componentB_input=component_a_job.outputs.componentA_output)
        component_c_job = c_func(componentC_input=component_b_job.outputs.componentB_output)
        return {
            "pipeline_sample_output_data_A": component_a_job.outputs.componentA_output,
            "pipeline_sample_output_data_B": component_b_job.outputs.componentB_output,
            "pipeline_sample_output_data_C": component_c_job.outputs.componentC_output,
        }

    pipeline = pipeline_with_data(
        Input(type='uri_file', path="https://dprepdata.blob.core.windows.net/demo/Titanic.csv"))
    pipeline.outputs.pipeline_sample_output_data_A.mode = "upload"
    pipeline.outputs.pipeline_sample_output_data_B.mode = "rw_mount"
    pipeline.outputs.pipeline_sample_output_data_C.mode = "upload"
    return pipeline
