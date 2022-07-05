# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

from azure.ai.ml.entities._inputs_outputs import Input, Output


def component_io_to_rest_obj(io_dict: Dict):
    """Component inputs/outputs entity to rest object."""
    rest_component_io = {}
    for name, port in io_dict.items():
        rest_component_io[name] = port._to_rest_object()
    return rest_component_io


def component_input_from_rest_obj(component_io: Dict):
    """Rest component inputs/outputs to dictionary."""
    component_io_dict = {}
    for name, rest_obj in component_io.items():
        io = Input._from_rest_object(rest_obj)
        component_io_dict[name] = io
    return component_io_dict


def component_output_from_rest_obj(component_io: Dict):
    """Rest component inputs/outputs to dictionary."""
    component_io_dict = {}
    for name, rest_obj in component_io.items():
        io = Output._from_rest_object(rest_obj)
        component_io_dict[name] = io
    return component_io_dict
