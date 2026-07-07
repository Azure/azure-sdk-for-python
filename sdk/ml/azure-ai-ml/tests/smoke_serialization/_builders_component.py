# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for component entities (Command, Spark)."""
from azure.ai.ml import Input, Output
from azure.ai.ml.entities import CommandComponent, SparkComponent


def build_command_component():
    """CommandComponent with typed inputs/outputs, command and environment."""
    return CommandComponent(
        name="smoke_command_component",
        version="1",
        display_name="smoke command component",
        description="smoke command component",
        tags={"tag1": "value1"},
        command="echo ${{inputs.learning_rate}} ${{inputs.data}} && echo ${{outputs.model}}",
        environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu:33",
        inputs={
            "learning_rate": Input(type="number", default=0.01),
            "epochs": Input(type="integer", default=10),
            "data": Input(type="uri_folder"),
            "flag": Input(type="boolean", default=True),
        },
        outputs={
            "model": Output(type="uri_folder"),
        },
    )


def build_spark_component():
    """SparkComponent with entry, conf and typed inputs/outputs."""
    return SparkComponent(
        name="smoke_spark_component",
        version="1",
        display_name="smoke spark component",
        description="smoke spark component",
        tags={"tag1": "value1"},
        code="./src",
        entry={"file": "main.py"},
        driver_cores=1,
        driver_memory="2g",
        executor_cores=2,
        executor_memory="2g",
        executor_instances=2,
        inputs={
            "data": Input(type="uri_file", mode="direct"),
        },
        outputs={
            "output": Output(type="uri_folder", mode="direct"),
        },
        args="--input ${{inputs.data}} --output ${{outputs.output}}",
    )


COMMAND_COMPONENT_BUILDERS = {
    "command_component": build_command_component,
}

SPARK_COMPONENT_BUILDERS = {
    "spark_component": build_spark_component,
}
