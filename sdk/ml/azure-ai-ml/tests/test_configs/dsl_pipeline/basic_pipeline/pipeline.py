from azure.ai.ml import dsl
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
    @dsl.pipeline(
        compute="cpu-cluster",
        description="Basic Pipeline Job with 3 Hello World components",
    )
    def basic_pipeline():
        component_a_job = a_func()
        component_b_job = b_func()
        component_c_job = c_func()

    pipeline = basic_pipeline()
    return pipeline
