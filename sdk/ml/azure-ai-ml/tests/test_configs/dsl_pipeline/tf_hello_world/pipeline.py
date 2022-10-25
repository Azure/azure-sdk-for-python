from pathlib import Path

from azure.ai.ml import TensorFlowDistribution, dsl, load_component
from azure.ai.ml.entities import JobResourceConfiguration, PipelineJob

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    tensorflow_func = load_component(source=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="TensorFlow hello-world showing training environment with $TF_CONFIG",
    )
    def tf_hello_world():
        tf_job = tensorflow_func()
        tf_job.compute = "cpu-cluster"
        tf_job.distribution = TensorFlowDistribution()
        tf_job.distribution.worker_count = 1
        tf_job.resources = JobResourceConfiguration()
        tf_job.resources.instance_count = 2

    pipeline = tf_hello_world()
    return pipeline
