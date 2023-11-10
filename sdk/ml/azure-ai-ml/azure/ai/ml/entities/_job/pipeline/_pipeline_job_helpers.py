# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from typing import Dict, List, Tuple, Type, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import InputDeliveryMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import Mpi, PyTorch, Ray, TensorFlow
from azure.ai.ml.constants._component import ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    INPUT_MOUNT_MAPPING_FROM_REST,
    INPUT_MOUNT_MAPPING_TO_REST,
    OUTPUT_MOUNT_MAPPING_FROM_REST,
    OUTPUT_MOUNT_MAPPING_TO_REST,
)
from azure.ai.ml.entities._util import normalize_job_input_output_type
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


def process_sdk_component_job_io(
    io: Dict,
    io_binding_regex_list: List[str],
) -> Tuple:
    """Separates SDK ComponentJob inputs that are data bindings (i.e. string inputs prefixed with 'inputs.' or
    'outputs.') and dataset and literal inputs/outputs.

    :param io: Input or output dictionary of an SDK ComponentJob
    :type io:  Dict[str, Union[str, float, bool, Input]]
    :param io_binding_regex_list: A list of regexes for io bindings
    :type io_binding_regex_list: List[str]
    :return: A tuple of dictionaries:
      * One mapping inputs to REST formatted ComponentJobInput/ComponentJobOutput for data binding io.
      * The other dictionary contains any IO that is not a databinding that is yet to be turned into REST form
    :rtype: Tuple[Dict[str, str], Dict[str, Union[str, float, bool, Input]]]
    """
    io_bindings: Dict = {}
    dataset_literal_io: Dict = {}
    legacy_io_binding_regex_list = [
        ComponentJobConstants.LEGACY_INPUT_PATTERN,
        ComponentJobConstants.LEGACY_OUTPUT_PATTERN,
    ]
    for io_name, io_value in io.items():
        if isinstance(io_value, (Input, Output)) and isinstance(io_value.path, str):
            mode = io_value.mode
            path = io_value.path
            name = io_value.name if hasattr(io_value, "name") else None
            version = io_value.version if hasattr(io_value, "version") else None
            if any(re.match(item, path) for item in io_binding_regex_list):
                # Yaml syntax requires using ${{}} to enclose inputs and outputs bindings
                # io_bindings[io_name] = io_value
                io_bindings.update({io_name: {"value": path}})
                # add mode to literal value for binding input
                if mode:
                    if isinstance(io_value, Input):
                        io_bindings[io_name].update({"mode": INPUT_MOUNT_MAPPING_TO_REST[mode]})
                    else:
                        io_bindings[io_name].update({"mode": OUTPUT_MOUNT_MAPPING_TO_REST[mode]})
                if name or version:
                    assert isinstance(io_value, Output)
                    if name:
                        io_bindings[io_name].update({"name": name})
                    if version:
                        io_bindings[io_name].update({"version": version})
                if isinstance(io_value, Output) and io_value.name is not None:
                    # when the output should be registered,
                    # we add io_value to dataset_literal_io for further to_rest_data_outputs
                    dataset_literal_io[io_name] = io_value
            elif any(re.match(item, path) for item in legacy_io_binding_regex_list):
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
    rest_object_class: Union[Type[RestJobInput], Type[RestJobOutput]],
    io_binding_regex_list: List[str],
) -> Tuple[Dict[str, str], Dict[str, Union[RestJobInput, RestJobOutput]]]:
    """Translate rest JObject dictionary to rest inputs/outputs and bindings.

    :param io: Input or output dictionary.
    :type io: Dict[str, Union[str, dict]]
    :param rest_object_class: RestJobInput or RestJobOutput
    :type rest_object_class: Union[Type[RestJobInput], Type[RestJobOutput]]
    :param io_binding_regex_list: A list of regexes for io bindings
    :type io_binding_regex_list: List[str]
    :return: Map from IO name to IO bindings and Map from IO name to IO objects.
    :rtype: Tuple[Dict[str, str], Dict[str, Union[RestJobInput, RestJobOutput]]]
    """
    io_bindings: dict = {}
    rest_io_objects = {}
    DIRTY_MODE_MAPPING = {
        "Mount": InputDeliveryMode.READ_ONLY_MOUNT,
        "RoMount": InputDeliveryMode.READ_ONLY_MOUNT,
        "RwMount": InputDeliveryMode.READ_WRITE_MOUNT,
    }
    for key, val in io.items():
        if isinstance(val, dict):
            # convert the input of camel to snake to be compatible with the Jun api
            # todo: backend help convert node level input/output type
            normalize_job_input_output_type(val)

            # Add casting as sometimes we got value like 1(int)
            io_value = str(val.get("value", ""))
            io_mode = val.get("mode", None)
            io_name = val.get("name", None)
            io_version = val.get("version", None)
            if any(re.match(item, io_value) for item in io_binding_regex_list):
                io_bindings.update({key: {"path": io_value}})
                # add mode to literal value for binding input
                if io_mode:
                    # deal with dirty mode data submitted before
                    if io_mode in DIRTY_MODE_MAPPING:
                        io_mode = DIRTY_MODE_MAPPING[io_mode]
                        val["mode"] = io_mode
                    if io_mode in OUTPUT_MOUNT_MAPPING_FROM_REST:
                        io_bindings[key].update({"mode": OUTPUT_MOUNT_MAPPING_FROM_REST[io_mode]})
                    else:
                        io_bindings[key].update({"mode": INPUT_MOUNT_MAPPING_FROM_REST[io_mode]})
                # add name and version for binding input
                if io_name or io_version:
                    assert rest_object_class.__name__ == "JobOutput"
                    # current code only support dump name and version for JobOutput
                    # this assert can be deleted if we need to dump name/version for JobInput
                    if io_name:
                        io_bindings[key].update({"name": io_name})
                    if io_version:
                        io_bindings[key].update({"version": io_version})
                if not io_mode and not io_name and not io_version:
                    io_bindings[key] = io_value
            else:
                if rest_object_class.__name__ == "JobOutput":
                    # current code only support dump name and version for JobOutput
                    # this condition can be deleted if we need to dump name/version for JobInput
                    if "name" in val.keys():
                        val["asset_name"] = val.pop("name")
                    if "version" in val.keys():
                        val["asset_version"] = val.pop("version")
                rest_obj = rest_object_class.from_dict(val)
                rest_io_objects[key] = rest_obj
        else:
            msg = "Got unsupported type of input/output: {}:" + f"{type(val)}"
            raise ValidationException(
                message=msg.format(val),
                no_personal_data_message=msg.format("[val]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
    return io_bindings, rest_io_objects


def from_dict_to_rest_distribution(distribution_dict: Dict) -> Union[PyTorch, Mpi, TensorFlow, Ray]:
    target_type = distribution_dict["distribution_type"].lower()
    if target_type == "pytorch":
        return PyTorch(**distribution_dict)
    if target_type == "mpi":
        return Mpi(**distribution_dict)
    if target_type == "tensorflow":
        return TensorFlow(**distribution_dict)
    if target_type == "ray":
        return Ray(**distribution_dict)
    msg = "Distribution type must be pytorch, mpi, tensorflow or ray: {}".format(target_type)
    raise ValidationException(
        message=msg,
        no_personal_data_message=msg,
        target=ErrorTarget.PIPELINE,
        error_category=ErrorCategory.USER_ERROR,
    )
