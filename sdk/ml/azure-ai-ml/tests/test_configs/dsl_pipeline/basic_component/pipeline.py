from azure.ai.ml import dsl, load_component
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    basic_func = load_component(path=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Hello World component example",
    )
    def basic_component():
        hello_python_world_job = basic_func()
        hello_python_world_job.compute = "cpu-cluster"

    pipeline = basic_component()
    return pipeline
