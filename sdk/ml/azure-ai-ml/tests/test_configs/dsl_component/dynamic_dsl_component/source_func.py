from pathlib import Path
from uuid import uuid4

from azure.ai.ml.entities._inputs_outputs import Input, Output


def train_func(
    training_data: Input,
    max_epochs: int,
    model_output: Output,
    learning_rate=0.01,
):
    """ component run logic goes here """
    lines = [
        f"Training data path: {training_data}",
        f"Max epochs: {max_epochs}",
        f"Learning rate: {learning_rate}",
        f"Model output path: {model_output}",
    ]

    for line in lines:
        print(line)

    # Do the train and save the trained model as a file into the output folder.
    # Here only output a dummy data for demo.
    model = str(uuid4())
    (Path(model_output) / "model").write_text(model)
