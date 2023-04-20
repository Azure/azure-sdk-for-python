from pathlib import Path

from azure.ai.ml import Input, command, dsl, load_component
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)
cluster_name = "cpu-cluster"


def generate_dsl_pipeline_from_yaml() -> PipelineJob:
    spark_component_func = load_component(parent_dir + "/component.yml")

    @dsl.pipeline(description="submit a pipeline with spark job")
    def spark_pipeline_from_yaml(sample_data):
        kmeans_cluster = spark_component_func(file_input=sample_data)
        kmeans_cluster.resources = {"instance_type": "standard_e4s_v3", "runtime_version": "3.2.0"}

        command_func = command(
            inputs=dict(spark_output=Input(type=AssetTypes.URI_FOLDER)),
            command="ls ${{inputs.spark_output}}",
            environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        )
        show_output = command_func(spark_output=kmeans_cluster.outputs.output)
        show_output.compute = cluster_name
        return {"output": kmeans_cluster.outputs.output}

    pipeline_job = spark_pipeline_from_yaml(
        sample_data=Input(
            path=parent_dir + "/dataset/sample_kmeans_data.txt", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT
        )
    )
    pipeline_job.outputs.output.mode = InputOutputModes.DIRECT

    return pipeline_job
