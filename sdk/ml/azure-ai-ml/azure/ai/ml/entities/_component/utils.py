# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

from azure.ai.ml.entities._component.input_output import ComponentInput, ComponentOutput
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


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
        io = ComponentInput._from_rest_object(rest_obj)
        component_io_dict[name] = io
    return component_io_dict


def component_output_from_rest_obj(component_io: Dict):
    """Rest component inputs/outputs to dictionary."""
    component_io_dict = {}
    for name, rest_obj in component_io.items():
        io = ComponentOutput._from_rest_object(rest_obj)
        component_io_dict[name] = io
    return component_io_dict


def build_validate_input(io_dict: Dict):
    component_io = {}
    for name, port in io_dict.items():
        if not name.isidentifier():
            msg = "{!r} is not a valid parameter name"
            raise ValidationException(
                message=msg.format(name), no_personal_data_message=msg.format("[name]"), target=ErrorTarget.COMPONENT
            )
        else:
            component_io[name] = ComponentInput(port)
    return component_io


def build_validate_output(io_dict: Dict):
    component_io = {}
    for name, port in io_dict.items():
        if not name.isidentifier():
            msg = "{!r} is not a valid parameter name"
            raise ValidationException(
                message=msg.format(name), no_personal_data_message=msg.format("[name]"), target=ErrorTarget.COMPONENT
            )
        else:
            component_io[name] = ComponentOutput(port)
    return component_io
