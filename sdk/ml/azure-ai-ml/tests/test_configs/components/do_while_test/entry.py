import os
import sys
from pathlib import Path

os.environ["AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED"] = "true"
os.environ["AZURE_ML_INTERNAL_COMPONENTS_ENABLED"] = "true"

from mldesigner import command_component
from mldesigner import dsl as designerdsl
from mldesigner._component_executor import ExecutorBase
from mldesigner.dsl import do_while

# from common.do_while_body import do_while_body_component, primitive_output_component_with_normal_input_output_v2
# from azure.ai.ml import dsl, load_component
from azure.ai.ml import Input, MLClient, Output, dsl, load_component
from azure.ai.ml.entities import PipelineJob
from azure.identity import DefaultAzureCredential

ENVIRONMENT_DICT = dict(
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
    conda_file={
        "name": "default_environment",
        "channels": ["defaults"],
        "dependencies": [
            "python=3.8.12",
            "pip=21.2.2",
            {
                "pip": [
                    "--extra-index-url=https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2",
                    "mldesigner==0.1.0b6",
                    "mlflow==1.29.0",
                    "azureml-mlflow==1.45.0",
                    "azure-ai-ml==1.0.0",
                    "azure-core==1.26.0",
                    "azure-common==1.1.28",
                    "azureml-core==1.45.0.post2",
                    "azure-ml-component==0.9.13.post1",
                    "azure-identity==1.11.0",
                ]
            },
        ],
    },
)


def write_text(input, output):
    input_data = Path(input)
    if input_data.is_dir():
        files = os.listdir(input_data)
        for f in files:
            lines = (Path(input_data) / f).read_text(encoding="utf-8")
            (Path(output) / f).write_text(lines)
    else:
        lines = (Path(input_data)).read_text(encoding="utf-8")
        (Path(output) / Path(input_data).name).write_text(lines)


@command_component(environment=ENVIRONMENT_DICT)
def primitive_component_with_normal_input_output_v2(
    input_data: Input,
    parambool: bool,
    paramint: int,
    paramfloat: float,
    paramstr: str,
    output_data: Output,
    bool_param_output: Output(type="boolean", is_control=True),
    int_param_output: Output(type="integer", is_control=True),
    float_param_output: Output(type="number", is_control=True),
    str_param_output: Output(type="string", is_control=True),
):
    if input_data is None or not Path(input_data).exists():
        (Path(output_data) / "file").write_text("abc")
        return

    write_text(input_data, output_data)

    bool_param_output = parambool
    int_param_output = paramint
    float_param_output = paramfloat
    str_param_output = paramstr
    print(
        f"output params are: bool_param_output: {bool_param_output}, int_param_output: {int_param_output}, float_param_output: {float_param_output}, str_param_output: {str_param_output}"
    )
    control_output_content = (
        '{"int_param_output": "%s", "bool_param_output": "%s", "float_param_output": "%s", "str_param_output": "%s"}'
        % (int_param_output, bool_param_output, float_param_output, str_param_output)
    )
    ExecutorBase._write_control_outputs_to_run_history(control_output_content=control_output_content)


@command_component(environment=ENVIRONMENT_DICT)
def do_while_body_component(
    input_1: Input,
    input_2: Input,
    bool_param: bool,
    int_param: int,
    float_param: float,
    str_param: str,
    output_1: Output,
    output_2: Output,
    condition: Output(type="boolean", is_control=True),
    bool_param_output: Output(type="boolean", is_control=True),
    int_param_output: Output(type="integer", is_control=True),
    float_param_output: Output(type="number", is_control=True),
    str_param_output: Output(type="string", is_control=True),
):
    if not (input_1 is None or not Path(input_1).exists()):
        write_text(input_1, output_1)
        print("finished writing input_1")

    if not (input_2 is None or not Path(input_2).exists()):
        write_text(input_2, output_2)
        print("finished writing input_2")

    condition = int_param < float_param
    print("condition is ", condition)
    int_param_output = int_param + 1
    print("int_param_output is ", int_param_output)
    float_param_output = float_param
    bool_param_output = bool_param
    str_param_output = str_param

    control_output_content = (
        '{"condition": "%s", "int_param_output": "%s", "bool_param_output": "%s", "float_param_output": "%s", "str_param_output": "%s"}'
        % (str(condition), int_param_output, bool_param_output, float_param_output, str_param_output)
    )
    ExecutorBase._write_control_outputs_to_run_history(control_output_content=control_output_content)
