# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from typing import Dict, List, Tuple, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2021_10_01.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2021_10_01.models import JobOutput as RestJobOutput
from azure.ai.ml._restclient.v2021_10_01.models import Mpi, PyTorch, TensorFlow
from azure.ai.ml.constants import ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    INPUT_MOUNT_MAPPING_TO_REST,
    OUTPUT_MOUNT_MAPPING_TO_REST,
    INPUT_MOUNT_MAPPING_FROM_REST,
    OUTPUT_MOUNT_MAPPING_FROM_REST,
)


def process_sdk_component_job_io(
    io: Dict[str, Union[str, float, bool, Input]],
    io_binding_regex_list: List[str],
) -> Tuple[Dict[str, str], Dict[str, Union[str, float, bool, Input]]]:
    """Separates SDK ComponentJob inputs that are data bindings (i.e. string
    inputs prefixed with 'inputs.' or 'outputs.') and dataset and literal
    inputs/outputs.

    :param io: Input or output dictionary of an SDK ComponentJob
    :type io:  Dict[str, Union[str, float, bool, Input]]
    :return: A tuple of dictionaries: One mapping inputs to REST formatted ComponentJobInput/ComponentJobOutput for data binding io.
             The other dictionary contains any IO that is not a databinding that is yet to be turned into REST form
    :rtype: Tuple[Dict[str, str], Dict[str, Union[str, float, bool, Input]]]
    """
    io_bindings = {}
    dataset_literal_io = {}
    legacy_io_binding_regex_list = [
        ComponentJobConstants.LEGACY_INPUT_PATTERN,
        ComponentJobConstants.LEGACY_OUTPUT_PATTERN,
    ]
    for io_name, io_value in io.items():
        if isinstance(io_value, (Input, Output)) and isinstance(io_value.path, str):
            mode = io_value.mode
            path = io_value.path
            if any([re.match(item, path) for item in io_binding_regex_list]):
                # Yaml syntax requires using ${{}} to enclose inputs and outputs bindings
                # io_bindings[io_name] = io_value
                io_bindings.update({io_name: {"value": path}})
                # add mode to literal value for binding input
                if mode:
                    if isinstance(io_value, Input):
                        io_bindings[io_name].update({"mode": INPUT_MOUNT_MAPPING_TO_REST[mode]})
                    else:
                        io_bindings[io_name].update({"mode": OUTPUT_MOUNT_MAPPING_TO_REST[mode]})
            elif any([re.match(item, path) for item in legacy_io_binding_regex_list]):
                new_format = path.replace("{{", "{{parent.")
                msg = "{} has changed to {}, please change to use new format."
                raise ValidationException(
                    message=msg.format(path, new_format),
                    no_personal_data_message=msg.format("[io_value]", "[io_value_new_format]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                dataset_literal_io[io_name] = io_value
        else:
            # Collect non-input data inputs
            dataset_literal_io[io_name] = io_value
    return io_bindings, dataset_literal_io


def from_dict_to_rest_io(
    io: Dict[str, Union[str, dict]],
    rest_object_class,
    io_binding_regex_list: List[str],
) -> Tuple[Dict[str, str], Dict[str, Union[RestJobInput, RestJobOutput]]]:
    """Translate rest JObject dictionary to rest inputs/outputs and bindings.

    :param io: Input or output dictionary.
    :param rest_object_class: RestJobInput or RestJobOutput
    :return: Map from IO name to IO bindings and Map from IO name to IO objects.
    """
    io_bindings = {}
    rest_io_objects = {}

    for key, val in io.items():
        if isinstance(val, dict):
            io_value = val.get("value", "")
            io_mode = val.get("mode", None)
            if any([re.match(item, io_value) for item in io_binding_regex_list]):
                if io_mode:
                    # add mode to literal value for binding input
                    io_bindings.update({key: {"path": io_value}})
                    if io_mode in OUTPUT_MOUNT_MAPPING_FROM_REST:
                        io_bindings[key].update({"mode": OUTPUT_MOUNT_MAPPING_FROM_REST[io_mode]})
                    else:
                        io_bindings[key].update({"mode": INPUT_MOUNT_MAPPING_FROM_REST[io_mode]})
                else:
                    io_bindings[key] = io_value
            else:
                rest_obj = rest_object_class.from_dict(val)
                rest_io_objects[key] = rest_obj
        else:
            msg = "Got unsupported type of output: {}:" + f"{type(val)}"
            raise ValidationException(
                message=msg.format(val),
                no_personal_data_message=msg.format("[val]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
    return io_bindings, rest_io_objects


def from_dict_to_rest_distribution(distribution_dict: Dict[str, Union[str, int]]) -> Union[PyTorch, Mpi, TensorFlow]:
    target_type = distribution_dict["distribution_type"].lower()
    if target_type == "pytorch":
        return PyTorch(**distribution_dict)
    elif target_type == "mpi":
        return Mpi(**distribution_dict)
    elif target_type == "tensorflow":
        return TensorFlow(**distribution_dict)
    else:
        msg = "Distribution type must be pytorch, mpi or tensorflow: {}".format(target_type)
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.PIPELINE,
            error_category=ErrorCategory.USER_ERROR,
        )
