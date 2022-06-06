from pathlib import Path
from uuid import uuid4
from datetime import datetime
from enum import Enum

# from azure.ai.ml import Input, Output
from mldesigner import command_component, Input, Output


class SampleEnum(Enum):
    Enum0 = 'Enum0'
    Enum1 = 'Enum1'
    Enum2 = 'Enum_2'
    Enum3 = 3


@command_component(name=f"dsl_component_train", display_name="my-train-job")
def train_func(
        training_data: Input(),
        max_epocs=20,
        learning_rate=1.8,
        learning_rate_schedule="time-based",
        model_output: Output = None,
        enum_param0: SampleEnum = "Enum0",
):
    """train component"""
    print("hello training world...")

    lines = [
        f"Training data: {training_data}",
        f"Max epocs: {max_epocs}",
        f"Learning rate: {learning_rate}",
        f"Learning rate schedule: {learning_rate_schedule}",
        f"Model output path: {model_output}",
        f"enum param0: {enum_param0}",
    ]

    for line in lines:
        print(line)

    # Do the train and save the trained model as a file into the output folder.
    # Here only output a dummy data for demo.
    curtime = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
    model = f"This is a dummy model with id: {str(uuid4())} generated at: {curtime}\n"
    (Path(model_output) / "model.txt").write_text(model)


@command_component(name=f"dsl_component_score", display_name="my-score-job")
def score_func(model_input: Input, test_data: Input, score_output: Output = None):
    """score component"""
    print("hello scoring world...")

    lines = [
        f"Model path: {model_input}",
        f"Test data path: {test_data}",
        f"Scoring output path: {score_output}",
    ]

    for line in lines:
        print(line)

    # Load the model from input port
    # Here only print the model as text since it is a dummy one
    model = (Path(model_input) / "model.txt").read_text()
    print("Model: ", model)

    # Do scoring with the input model
    # Here only print text to output file as demo
    (Path(score_output) / "score.txt").write_text("Scored with the following mode:\n{}".format(model))


@command_component(name=f"dsl_component_eval", display_name="my-evaluate-job")
def eval_func(scoring_result: Input, eval_output: Output = None):
    """eval component"""
    print("hello evaluation world...")

    lines = [
        f"Scoring result path: {scoring_result}",
        f"Evaluation output path: {eval_output}",
    ]

    for line in lines:
        print(line)

    # Evaluate the incoming scoring result and output evaluation result.
    # Here only output a dummy file for demo.
    curtime = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
    eval_msg = f"Eval done at {curtime}\n"
    (Path(eval_output) / "eval_result.txt").write_text(eval_msg)
