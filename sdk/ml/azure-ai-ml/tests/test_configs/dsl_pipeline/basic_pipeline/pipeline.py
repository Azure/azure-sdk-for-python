from pathlib import Path

from azure.ai.ml import dsl, load_component
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    a_func = load_component(source=parent_dir + "/componentA.yml")
    b_func = load_component(source=parent_dir + "/componentB.yml")
    c_func = load_component(source=parent_dir + "/componentC.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        compute="cpu-cluster",
        description="Basic Pipeline Job with 3 Hello World components",
    )
    def basic_pipeline():
        component_a_job = a_func()
        component_b_job = b_func()
        component_c_job = c_func()
        # these 3 variables are required in the unit/e2e test for the dsl pipelines. To avoid the unused variable error, adding print call for these variables.
        print(component_a_job)
        print(component_b_job)
        print(component_c_job)

    pipeline = basic_pipeline()
    return pipeline
