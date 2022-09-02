from pathlib import Path

from azure.ai.ml import Input, ManagedIdentity, Output, dsl, load_component, spark
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._assets.environment import Environment

parent_dir = str(Path(__file__).parent)
synapse_compute_name = "spark31"


def generate_dsl_pipeline_from_yaml() -> PipelineJob:
    spark_component_func = load_component(path=parent_dir + "/component.yml")

    @dsl.pipeline(description="submit a spark job using component sdk")
    def spark_pipeline_from_yaml(iris_data):
        spark_job = spark_component_func(file_input1=iris_data, file_input2=iris_data)
        # spark_job.outputs.output = Output(
        #     path="azureml://datastores/workspaceblobstore/paths/azureml/spark_comp/outputs/output"
        # )
        spark_job.compute = synapse_compute_name
        return {"output": spark_job.outputs.output}

    pipeline = spark_pipeline_from_yaml(
        iris_data=Input(path=parent_dir + "/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
    )
    pipeline.outputs.output.mode = "Direct"

    return pipeline


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    # define the spark task
    iris_data = Input(path=parent_dir + "/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
    spark_node = spark(
        code=parent_dir + "/src",
        entry={"file": "entry.py"},
        py_files=["utils.zip"],
        jars=["scalaproj.jar"],
        files=["my_files.txt"],
        driver_cores=2,
        driver_memory="1g",
        executor_cores=1,
        executor_memory="1g",
        executor_instances=1,
        inputs=dict(file_input1=iris_data, file_input2=iris_data),
        outputs=dict(output=Output(type="uri_folder", mode=InputOutputModes.DIRECT)),
        args="--file_input1 ${{inputs.file_input1}} --file_input2 ${{inputs.file_input2}} --output ${{outputs.output}}",
        compute=synapse_compute_name,
        # For HOBO spark, provide 'resources', not provide compute
        # resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
    )

    # Define pipeline
    @dsl.pipeline(description="submit a spark job using component sdk")
    def spark_pipeline_from_builder(iris_data):
        spark_job = spark_node(file_input1=iris_data, file_input2=iris_data)
        return {"output": spark_job.outputs.output}

    pipeline = spark_pipeline_from_builder(
        iris_data=iris_data,
    )
    pipeline.outputs.output.mode = "Direct"
    return pipeline
