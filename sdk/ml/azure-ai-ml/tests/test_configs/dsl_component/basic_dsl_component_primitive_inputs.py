from uuid import uuid4
from datetime import datetime
from enum import Enum

from mldesigner import command_component


class SampleEnum(Enum):
    Enum0 = 'Enum0'
    Enum1 = 'Enum1'
    Enum2 = 'Enum_2'
    Enum3 = 3


@command_component(name=f"dsl_component_train", display_name="my-train-job")
def train_func(
        max_epocs=20,
        learning_rate=1.8,
        learning_rate_schedule="time-based",
        enum_param0: SampleEnum = "Enum0",
):
    """train component"""
    print("hello training world...")

    lines = [
        f"Max epocs: {max_epocs}",
        f"Learning rate: {learning_rate}",
        f"Learning rate schedule: {learning_rate_schedule}",
        f"enum param0: {enum_param0}",
    ]

    for line in lines:
        print(line)

    # Do the train and save the trained model as a file into the output folder.
    # Here only output a dummy data for demo.
    curtime = datetime.now().strftime("%b-%d-%Y %H:%M:%S")
    model = f"This is a dummy model with id: {str(uuid4())} generated at: {curtime}\n"
