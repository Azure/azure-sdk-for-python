# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""This package includes the type classes which could be used in dsl.pipeline,
command function, or any other place that requires job inputs/outputs.

.. note::

    The following pseudo-code shows how to create a pipeline with such classes.

    .. code-block:: python

        @pipeline()
        def some_pipeline(
            input_param: Input(type="uri_folder", path="xxx", mode="ro_mount"),
            int_param0: Input(type="integer", default=0, min=-3, max=10),
            int_param1 = 2
            str_param = 'abc',
        ):
            pass


    The following pseudo-code shows how to create a command with such classes.

    .. code-block:: python

        my_command = command(
            name="my_command",
            display_name="my_command",
            description="This is a command",
            tags=dict(),
            command="python train.py --input-data ${{inputs.input_data}} --lr ${{inputs.learning_rate}}",
            code="./src",
            compute="cpu-cluster",
            environment="my-env:1",
            distribution=MpiDistribution(process_count_per_instance=4),
            environment_variables=dict(foo="bar"),
            # Customers can still do this:
            # resources=Resources(instance_count=2, instance_type="STANDARD_D2"),
            # limits=Limits(timeout=300),
            inputs={
                "float": Input(type="number", default=1.1, min=0, max=5),
                "integer": Input(type="integer", default=2, min=-1, max=4),
                "integer1": 2,
                "string0": Input(type="string", default="default_str0"),
                "string1": "default_str1",
                "boolean": Input(type="boolean", default=False),
                "uri_folder": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
                "uri_file": Input(type="uri_file", path="https://my-blob/path/to/data", mode="download"),
            },
            outputs={"my_model": Output(type="mlflow_model")},
        )
        node = my_command()
"""

from .enum_input import EnumInput
from .external_data import Database, FileSystem
from .group_input import GroupInput
from .input import Input
from .output import Output
from .utils import _get_param_with_standard_annotation, is_group

__all__ = [
    "Input",
    "Output",
    "EnumInput",
    "GroupInput",
    "is_group",
    "_get_param_with_standard_annotation",
    "Database",
    "FileSystem",
]
