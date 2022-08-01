from pathlib import Path
from uuid import uuid4
from random import random

from mldesigner import command_component
from azure.ai.ml import Input, Output
from azure.ai.ml.entities import Environment
from mldesigner import command_component


# init customer environment with conda YAML
# the YAML file shall be put under your code folder.
conda_env = Environment(
    conda_file=Path(__file__).parent / "conda.yaml", image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04"
)


@command_component(
    name="mldesigner_train_component",
    display_name="Train",
    description="A dummy train component defined by mldesigner component.",
    version="0.0.2",
    environment=conda_env,
)
def train_component_func(
    training_data: Input,
    model_output: Output,
    batch_size: int = 32,
    first_layer_neurons: int = 40,
    second_layer_neurons: int = 20,
    third_layer_neurons: int = 5,
    epochs: int = 3,
    momentum: float = 10,
    weight_decay: float = 0.5,
    learning_rate: float = 0.02,
    f1: float = 0.5,
    f2: float = 0.5,
    random_seed: int = 0,
):
    accuracy = random()
    for param_name, param_value in [
        ("training_data", training_data),
        ("batch_size", batch_size),
        ("first_layer_neurons", first_layer_neurons),
        ("second_layer_neurons", second_layer_neurons),
        ("third_layer_neurons", third_layer_neurons),
        ("epochs", epochs),
        ("momentum", momentum),
        ("weight_decay", weight_decay),
        ("learning_rate", learning_rate),
        ("f1", f1),
        ("f2", f2),
        ("model_output", model_output),
        ("random_seed", random_seed),
        ("accuracy", accuracy),
    ]:
        print(f"{param_name}: {param_value}")

    from azureml.core import Run

    run = Run.get_context()
    run.log("accuracy", accuracy)

    # Do the train and save the trained model as a file into the output folder.
    # Here only output a dummy data for demo.
    model = str(uuid4())
    (Path(model_output) / "model").write_text(model)


@command_component(
    name="mldesigner_score_component",
    display_name="Score",
    description="A dummy score component defined by mldesigner component.",
    environment=conda_env,
    version="0.0.1",
)
def score_component_func(
    model_input: Input,
    test_data: Input,
    score_output: Output,
):

    lines = [
        f"Model path: {model_input}",
        f"Test data path: {test_data}",
        f"Scoring output path: {score_output}",
    ]

    for line in lines:
        print(line)

    # Load the model from input port
    # Here only print the model as text since it is a dummy one
    model = (Path(model_input) / "model").read_text()
    print("Model:", model)

    # Do scoring with the input model
    # Here only print text to output file as demo
    (Path(score_output) / "score").write_text("scored with {}".format(model))


@command_component(
    name="mldesigner_eval_component",
    display_name="Evaluate",
    description="A dummy evaluate component defined by mldesigner component.",
    environment=conda_env,
    version="0.0.1",
)
def eval_component_func(
    scoring_result: Input,
    eval_output: Output,
):
    lines = [
        f"Scoring result path: {scoring_result}",
        f"Evaluation output path: {eval_output}",
    ]

    for line in lines:
        print(line)

    # Evaluate the incoming scoring result and output evaluation result.
    # Here only output a dummy file for demo.
    (Path(eval_output) / "eval_result").write_text("eval_result")
