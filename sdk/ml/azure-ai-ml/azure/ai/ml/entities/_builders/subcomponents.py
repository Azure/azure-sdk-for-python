# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# This file contains mldesigner decorator-produced components
# that are used within node constructors. Keep imports and
# general complexity in this file to a minimum.

from typing import List

from mldesigner import Output, command_component

from azure.ai.ml.constants._common import DefaultOpenEncoding


def save_mltable_yaml(path: str, mltable_paths: List[str]) -> None:
    """Save MLTable YAML.

    :param path: The path to save the MLTable YAML file.
    :type path: str
    :param mltable_paths: List of paths to be included in the MLTable.
    :type mltable_paths: List[str]
    :raises ValueError: If the given path points to a file.
    """
    import os

    path = os.path.abspath(path)

    if os.path.isfile(path):
        raise ValueError(f"The given path {path} points to a file.")

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    save_path = os.path.join(path, "MLTable")
    # Do not touch - this is MLTable syntax that is needed to mount these paths
    # To the MLTable's inputs
    mltable_file_content = "\n".join(["paths:"] + [f"- folder : {path}" for path in mltable_paths])

    with open(save_path, "w", encoding=DefaultOpenEncoding.WRITE) as f:
        f.write(mltable_file_content)


# TODO 2293610: add support for more types of outputs besides uri_folder and mltable
@command_component()
def create_scatter_output_table(aggregated_output: Output(type="mltable"), **kwargs: str) -> Output:  # type: ignore
    """Create scatter output table.

    This function is used by the FL scatter gather node to reduce a dynamic number of silo outputs
    into a single input for the user-supplied aggregation step.

    :param aggregated_output: The aggregated output MLTable.
    :type aggregated_output: ~mldesigner.Output(type="mltable")

    Keyword arguments represent input names and URI folder paths.
    """
    # kwargs keys are inputs names (ex: silo_output_silo_1)
    # values are uri_folder paths
    save_mltable_yaml(aggregated_output, list(kwargs.values()))
