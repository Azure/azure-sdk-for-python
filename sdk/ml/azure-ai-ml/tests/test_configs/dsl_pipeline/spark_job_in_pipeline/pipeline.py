from pathlib import Path

from azure.ai.ml import Input, Output, dsl, load_component, spark
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities import PipelineJob

parent_dir = str(Path(__file__).parent)
synapse_compute_name = "spark31"


def generate_dsl_pipeline_from_yaml() -> PipelineJob:
    add_greeting_column_func = load_component(parent_dir + "/add_greeting_column_component.yml")
    count_by_row_func = load_component(parent_dir + "/count_by_row_component.yml")

    @dsl.pipeline(description="submit a pipeline with spark job")
    def spark_pipeline_from_yaml(iris_data):
        add_greeting_column = add_greeting_column_func(file_input=iris_data)
        add_greeting_column.compute = synapse_compute_name
        count_by_row = count_by_row_func(file_input=iris_data)
        count_by_row.compute = synapse_compute_name
        return {"output": count_by_row.outputs.output}

    pipeline = spark_pipeline_from_yaml(
        iris_data=Input(path=parent_dir + "/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
    )
    pipeline.outputs.output.mode = "Direct"

    return pipeline


def generate_dsl_pipeline_from_builder() -> PipelineJob:
    # define the spark task
    iris_data = Input(path=parent_dir + "/dataset/iris.csv", type=AssetTypes.URI_FILE, mode=InputOutputModes.DIRECT)
    add_greeting_column_func = spark(
        code=parent_dir + "/src",
        entry={"file": "add_greeting_column.py"},
        py_files=["utils.zip"],
        files=["my_files.txt"],
        driver_cores=2,
        driver_memory="1g",
        executor_cores=1,
        executor_memory="1g",
        executor_instances=1,
        inputs=dict(file_input=iris_data),
        args="--file_input ${{inputs.file_input}}",
        compute=synapse_compute_name,
        # For HOBO spark, provide 'resources', not provide compute
        # resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
    )

    count_by_row_func = spark(
        code=parent_dir + "/src",
        entry={"file": "count_by_row.py"},
        jars=["scalaproj.jar"],
        files=["my_files.txt"],
        driver_cores=2,
        driver_memory="1g",
        executor_cores=1,
        executor_memory="1g",
        executor_instances=1,
        inputs=dict(file_input=iris_data),
        outputs=dict(output=Output(type="uri_folder", mode=InputOutputModes.DIRECT)),
        args="--file_input ${{inputs.file_input}} --output ${{outputs.output}}",
        compute=synapse_compute_name,
        # For HOBO spark, provide 'resources', not provide compute
        # resources={"instance_type": "Standard_E8S_V3", "runtime_version": "3.1.0"}
    )

    # Define pipeline
    @dsl.pipeline(description="submit a pipeline with spark job")
    def spark_pipeline_from_builder(iris_data):
        add_greeting_column = add_greeting_column_func(file_input=iris_data)
        count_by_row = count_by_row_func(file_input=iris_data)
        return {"output": count_by_row.outputs.output}

    pipeline = spark_pipeline_from_builder(
        iris_data=iris_data,
    )
    pipeline.outputs.output.mode = "Direct"
    return pipeline
