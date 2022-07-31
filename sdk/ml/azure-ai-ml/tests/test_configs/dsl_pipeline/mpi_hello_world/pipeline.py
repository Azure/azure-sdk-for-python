from azure.ai.ml import dsl
from azure.ai.ml.entities import load_component
from azure.ai.ml import MpiDistribution
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

from azure.ai.ml.entities import ResourceConfiguration

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    mpi_func = load_component(yaml_file=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(description="Show the MPI training environment")
    def mpi_hello_world():
        tf_job = mpi_func()
        tf_job.compute = "cpu-cluster"
        tf_job.distribution = MpiDistribution()
        tf_job.distribution.process_count_per_instance = 1
        tf_job.resources = ResourceConfiguration()
        tf_job.resources.instance_count = 2

    pipeline = mpi_hello_world()
    return pipeline
