from pathlib import Path

from azure.ai.ml import PyTorchDistribution, dsl, load_component
from azure.ai.ml.entities import JobResourceConfiguration, PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    pytorch_func = load_component(source=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Prints the environment variables useful for scripts " "running in a PyTorch training environment",
    )
    def pytorch_hello_world():
        pytorch_job = pytorch_func()
        pytorch_job.compute = "cpu-cluster"
        pytorch_job.distribution = PyTorchDistribution()
        pytorch_job.distribution.process_count_per_instance = 1
        pytorch_job.resources = JobResourceConfiguration()
        pytorch_job.resources.instance_count = 2

    pipeline = pytorch_hello_world()
    return pipeline
