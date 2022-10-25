from pathlib import Path

from azure.ai.ml import Input, command, dsl, load_component
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)
synapse_compute_name = "spark31"
cluster_name = "cpu-cluster"


def generate_dsl_pipeline_from_yaml() -> PipelineJob:
    spark_component_func = load_component(parent_dir + "/component.yml")

    @dsl.pipeline(description="submit a pipeline with spark job")
    def spark_pipeline_from_yaml(sample_data):
        kmeans_cluster = spark_component_func(file_input=sample_data)
        kmeans_cluster.compute = synapse_compute_name

        command_func = command(
            inputs=dict(spark_output=Input(type=AssetTypes.URI_FOLDER, mode=InputOutputModes.DIRECT)),
            command="ls ${{inputs.spark_output}}",
            environment="AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
        )
        show_output = command_func(spark_output=kmeans_cluster.outputs.output)
        return {"output": kmeans_cluster.outputs.output}

    pipeline_job = spark_pipeline_from_yaml(
        sample_data=Input(
            path=parent_dir + "/dataset/sample_kmeans_data.txt", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT
        )
    )
    pipeline_job.outputs.output.mode = InputOutputModes.DIRECT
    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name

    return pipeline_job
