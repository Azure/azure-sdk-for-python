from pathlib import Path

from azure.ai.ml import dsl, load_component
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(source=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline()
    def env_public_docker_image():
        hello_python_world_job = basic_func()
        hello_python_world_job.compute = "cpu-cluster"

    pipeline = env_public_docker_image()
    return pipeline
