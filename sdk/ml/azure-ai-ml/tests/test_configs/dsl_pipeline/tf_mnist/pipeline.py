from azure.ai.ml import dsl, TensorFlowDistribution, load_component
from azure.ai.ml.entities import PipelineJob
from pathlib import Path

from azure.ai.ml.entities import ResourceConfiguration

parent_dir = str(Path(__file__).parent)


def generate_dsl_pipeline() -> PipelineJob:
    # 1. Load component funcs
    tf_func = load_component(path=parent_dir + "/component.yml")

    # 2. Construct pipeline
    @dsl.pipeline(
        description="Train using TF component",
    )
    def tf_mnist():
        tf_job = tf_func(epochs=1)
        tf_job.compute = "cpu-cluster"
        tf_job.outputs.trained_model_output.mode = "upload"
        tf_job.distribution = TensorFlowDistribution()
        tf_job.distribution.worker_count = 1
        tf_job.resources = ResourceConfiguration()
        tf_job.resources.instance_count = 2

    pipeline = tf_mnist()
    return pipeline
