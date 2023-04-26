# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import collections.abc
import re
from typing import Any, Dict, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import CustomModelJobInput as RestCustomModelJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import CustomModelJobOutput as RestCustomModelJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import InputDeliveryMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobInputType
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobOutputType, LiteralJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import MLFlowModelJobInput as RestMLFlowModelJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import MLFlowModelJobOutput as RestMLFlowModelJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import MLTableJobInput as RestMLTableJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import MLTableJobOutput as RestMLTableJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import OutputDeliveryMode
from azure.ai.ml._restclient.v2023_04_01_preview.models import TritonModelJobInput as RestTritonModelJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import TritonModelJobOutput as RestTritonModelJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFileJobInput as RestUriFileJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFileJobOutput as RestUriFileJobOutput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFolderJobInput as RestUriFolderJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import UriFolderJobOutput as RestUriFolderJobOutput
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes, InputOutputModes, JobType
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.input_output_entry import InputOutputEntry
from azure.ai.ml.entities._util import normalize_job_input_output_type
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException, ValidationErrorType, ValidationException

INPUT_MOUNT_MAPPING_FROM_REST = {
    InputDeliveryMode.READ_WRITE_MOUNT: InputOutputModes.RW_MOUNT,
    InputDeliveryMode.READ_ONLY_MOUNT: InputOutputModes.RO_MOUNT,
    InputDeliveryMode.DOWNLOAD: InputOutputModes.DOWNLOAD,
    InputDeliveryMode.DIRECT: InputOutputModes.DIRECT,
    InputDeliveryMode.EVAL_MOUNT: InputOutputModes.EVAL_MOUNT,
    InputDeliveryMode.EVAL_DOWNLOAD: InputOutputModes.EVAL_DOWNLOAD,
}

INPUT_MOUNT_MAPPING_TO_REST = {
    InputOutputModes.MOUNT: InputDeliveryMode.READ_ONLY_MOUNT,
    InputOutputModes.RO_MOUNT: InputDeliveryMode.READ_ONLY_MOUNT,
    InputOutputModes.DOWNLOAD: InputDeliveryMode.DOWNLOAD,
    InputOutputModes.EVAL_MOUNT: InputDeliveryMode.EVAL_MOUNT,
    InputOutputModes.EVAL_DOWNLOAD: InputDeliveryMode.EVAL_DOWNLOAD,
    InputOutputModes.DIRECT: InputDeliveryMode.DIRECT,
}


OUTPUT_MOUNT_MAPPING_FROM_REST = {
    OutputDeliveryMode.READ_WRITE_MOUNT: InputOutputModes.RW_MOUNT,
    OutputDeliveryMode.UPLOAD: InputOutputModes.UPLOAD,
    OutputDeliveryMode.DIRECT: InputOutputModes.DIRECT,
}

OUTPUT_MOUNT_MAPPING_TO_REST = {
    InputOutputModes.MOUNT: OutputDeliveryMode.READ_WRITE_MOUNT,
    InputOutputModes.UPLOAD: OutputDeliveryMode.UPLOAD,
    InputOutputModes.RW_MOUNT: OutputDeliveryMode.READ_WRITE_MOUNT,
    InputOutputModes.DIRECT: OutputDeliveryMode.DIRECT,
}


# TODO: Remove this as both rest type and sdk type are snake case now.
def get_output_type_mapping_from_rest():
    """Get output type mapping."""
    return {
        JobOutputType.URI_FILE: AssetTypes.URI_FILE,
        JobOutputType.URI_FOLDER: AssetTypes.URI_FOLDER,
        JobOutputType.MLTABLE: AssetTypes.MLTABLE,
        JobOutputType.MLFLOW_MODEL: AssetTypes.MLFLOW_MODEL,
        JobOutputType.CUSTOM_MODEL: AssetTypes.CUSTOM_MODEL,
        JobOutputType.TRITON_MODEL: AssetTypes.TRITON_MODEL,
    }


def get_input_rest_cls_dict():
    """Get input rest init func dict."""
    return {
        AssetTypes.URI_FILE: RestUriFileJobInput,
        AssetTypes.URI_FOLDER: RestUriFolderJobInput,
        AssetTypes.MLTABLE: RestMLTableJobInput,
        AssetTypes.MLFLOW_MODEL: RestMLFlowModelJobInput,
        AssetTypes.CUSTOM_MODEL: RestCustomModelJobInput,
        AssetTypes.TRITON_MODEL: RestTritonModelJobInput,
    }


def get_output_rest_cls_dict():
    """Get output rest init cls dict."""

    return {
        AssetTypes.URI_FILE: RestUriFileJobOutput,
        AssetTypes.URI_FOLDER: RestUriFolderJobOutput,
        AssetTypes.MLTABLE: RestMLTableJobOutput,
        AssetTypes.MLFLOW_MODEL: RestMLFlowModelJobOutput,
        AssetTypes.CUSTOM_MODEL: RestCustomModelJobOutput,
        AssetTypes.TRITON_MODEL: RestTritonModelJobOutput,
    }


def build_input_output(
    item: Union[InputOutputEntry, Input, Output, str, bool, int, float],
    inputs: bool = True,
) -> Union[InputOutputEntry, Input, Output, str, bool, int, float]:
    if isinstance(item, (Input, InputOutputEntry, Output)):
        # return objects constructed at yaml load or specified in sdk
        return item
    # parse dictionary into supported class
    if isinstance(item, collections.abc.Mapping):
        if item.get("data"):
            return InputOutputEntry(**item)
        # else default to JobInput
        return Input(**item) if inputs else Output(**item)
    # return literal inputs as-is
    return item


def _validate_inputs_for(input_consumer_name: str, input_consumer: str, inputs: Dict[str, Any]) -> None:
    implicit_inputs = re.findall(r"\${{inputs\.([\w\.-]+)}}", input_consumer)
    # optional inputs no need to validate whether they're in inputs
    optional_inputs = re.findall(r"\[[\w\.\s-]*\${{inputs\.([\w\.-]+)}}]", input_consumer)
    for key in implicit_inputs:
        if inputs.get(key, None) is None and key not in optional_inputs:
            msg = "Inputs to job does not contain '{}' referenced in " + input_consumer_name
            raise ValidationException(
                message=msg.format(key),
                no_personal_data_message=msg.format("[key]"),
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )


def validate_inputs_for_command(command: str, inputs: Dict[str, Any]) -> None:
    _validate_inputs_for("command", command, inputs)


def validate_inputs_for_args(args: str, inputs: Dict[str, Any]) -> None:
    _validate_inputs_for("args", args, inputs)


def validate_key_contains_allowed_characters(key: str) -> None:
    if re.match(r"^[a-zA-Z_]+[a-zA-Z0-9_]*$", key) is None:
        msg = "Key name  {} must be composed letters, numbers, and underscore"
        raise ValidationException(
            message=msg.format(key),
            no_personal_data_message=msg.format("[key]"),
            target=ErrorTarget.JOB,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


def validate_pipeline_input_key_contains_allowed_characters(key: str) -> None:
    # Pipeline input allow '.' to support parameter group in key.
    # Note: ([a-zA-Z_]+[a-zA-Z0-9_]*) is a valid single key,
    # so a valid pipeline key is: ^{single_key}([.]{single_key})*$
    if re.match(IOConstants.VALID_KEY_PATTERN, key) is None:
        msg = (
            "Pipeline input key name {} must be composed letters, numbers, and underscores with optional split by dots."
        )
        raise ValidationException(
            message=msg.format(key),
            no_personal_data_message=msg.format("[key]"),
            target=ErrorTarget.JOB,
            error_category=ErrorCategory.USER_ERROR,
        )


def to_rest_dataset_literal_inputs(
    inputs: Dict[str, Union[int, str, float, bool, Input]],
    *,
    job_type,
) -> Dict[str, RestJobInput]:
    """Turns dataset and literal inputs into dictionary of REST JobInput.

    :param inputs: Dictionary of dataset and literal inputs to job
    :type inputs: Dict[str, Union[int, str, float, bool, JobInput]]
    :return: A dictionary mapping input name to a ComponentJobInput or PipelineInput
    :rtype: Dict[str, Union[ComponentJobInput, PipelineInput]]
    :param job_type: When job_type is pipeline, enable dot('.') in parameter keys to support parameter group.
        TODO: Remove this after move name validation to Job's customized validate.
    :type job_type: str
    """
    rest_inputs = {}
    # Pack up the inputs into REST format
    for input_name, input_value in inputs.items():
        if job_type == JobType.PIPELINE:
            validate_pipeline_input_key_contains_allowed_characters(input_name)
        elif job_type:
            # We pass job_type=None for pipeline node, and want skip this check for nodes.
            validate_key_contains_allowed_characters(input_name)
        if isinstance(input_value, Input):
            if input_value.path and isinstance(input_value.path, str) and is_data_binding_expression(input_value.path):
                input_data = LiteralJobInput(value=input_value.path)
                # set mode attribute manually for binding job input
                if input_value.mode:
                    input_data.mode = INPUT_MOUNT_MAPPING_TO_REST[input_value.mode]
                input_data.job_input_type = JobInputType.LITERAL
            else:
                target_cls_dict = get_input_rest_cls_dict()

                if input_value.type in target_cls_dict:
                    input_data = target_cls_dict[input_value.type](
                        uri=input_value.path,
                        mode=INPUT_MOUNT_MAPPING_TO_REST[input_value.mode.lower()] if input_value.mode else None,
                    )

                else:
                    msg = f"Job input type {input_value.type} is not supported as job input."
                    raise ValidationException(
                        message=msg,
                        no_personal_data_message=msg,
                        target=ErrorTarget.JOB,
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
        elif input_value is None:
            # If the input is None, we need to pass the origin None to the REST API
            input_data = LiteralJobInput(value=None)
        else:
            # otherwise, the input is a literal input
            if isinstance(input_value, dict):
                input_data = LiteralJobInput(value=str(input_value["value"]))
                # set mode attribute manually for binding job input
                if "mode" in input_value:
                    input_data.mode = input_value["mode"]
            else:
                input_data = LiteralJobInput(value=str(input_value))
            input_data.job_input_type = JobInputType.LITERAL
        # Pack up inputs into PipelineInputs or ComponentJobInputs depending on caller
        rest_inputs[input_name] = input_data
    return rest_inputs


def from_rest_inputs_to_dataset_literal(
    inputs: Dict[str, RestJobInput]
) -> Dict[str, Union[int, str, float, bool, Input]]:
    """Turns REST dataset and literal inputs into the SDK format.

    :param inputs: Dictionary mapping input name to ComponentJobInput or PipelineInput
    :type inputs: Dict[str, Union[ComponentJobInput, PipelineInput]]
    :return: A dictionary mapping input name to a literal value or JobInput
    :rtype: Dict[str, Union[int, str, float, bool, JobInput]]
    """
    if inputs is None:
        return {}
    from_rest_inputs = {}
    # Unpack the inputs
    for input_name, input_value in inputs.items():
        # TODO:Brandon Clarify with PMs if user should be able to define null input objects
        if input_value is None:
            continue

        # TODO: Remove this as both rest type and sdk type are snake case now.
        type_transfer_dict = get_output_type_mapping_from_rest()
        # deal with invalid input type submitted by feb api
        # todo: backend help convert node level input/output type
        normalize_job_input_output_type(input_value)

        if input_value.job_input_type in type_transfer_dict:
            if input_value.uri:
                path = input_value.uri

                input_data = Input(
                    type=type_transfer_dict[input_value.job_input_type],
                    path=path,
                    mode=INPUT_MOUNT_MAPPING_FROM_REST[input_value.mode] if input_value.mode else None,
                )
        elif input_value.job_input_type in (JobInputType.LITERAL, JobInputType.LITERAL):
            # otherwise, the input is a literal, so just unpack the InputData value field
            input_data = input_value.value
        else:
            msg = f"Job input type {input_value.job_input_type} is not supported as job input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        from_rest_inputs[input_name] = input_data
    return from_rest_inputs


def to_rest_data_outputs(outputs: Dict[str, Output]) -> Dict[str, RestJobOutput]:
    """Turns job outputs into REST format.

    :param outputs: Dictionary of dataset outputs from job
    :type outputs: Dict[str, JobOutput]
    :return: A dictionary mapping output name to a RestJobOutput
    :rtype: Dict[str, RestJobOutput]
    """
    rest_outputs = {}
    for output_name, output_value in outputs.items():
        validate_key_contains_allowed_characters(output_name)
        if output_value is None:
            # pipeline output could be none, default to URI folder with None mode
            output_cls = RestUriFolderJobOutput
            rest_outputs[output_name] = output_cls(mode=None)
        else:
            target_cls_dict = get_output_rest_cls_dict()

            output_value_type = output_value.type if output_value.type else AssetTypes.URI_FOLDER
            if output_value_type in target_cls_dict:
                output = target_cls_dict[output_value_type](
                    asset_name=output_value.name,
                    asset_version=output_value.version,
                    uri=output_value.path,
                    mode=OUTPUT_MOUNT_MAPPING_TO_REST[output_value.mode.lower()] if output_value.mode else None,
                    description=output_value.description,
                )
            else:
                msg = "unsupported JobOutput type: {}".format(output_value.type)
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            rest_outputs[output_name] = output
    return rest_outputs


def from_rest_data_outputs(outputs: Dict[str, RestJobOutput]) -> Dict[str, Output]:
    """Turns REST outputs into the SDK format.

    :param outputs: Dictionary of dataset and literal inputs to job
    :type outputs: Dict[str, RestJobOutput]
    :return: A dictionary mapping input name to a InputOutputEntry
    :rtype: Dict[str, JobOutput]
    """
    output_type_mapping = get_output_type_mapping_from_rest()
    from_rest_outputs = {}
    if outputs is None:
        return {}
    for output_name, output_value in outputs.items():
        if output_value is None:
            continue
        # deal with invalid output type submitted by feb api
        # todo: backend help convert node level input/output type
        normalize_job_input_output_type(output_value)

        if output_value.job_output_type in output_type_mapping:
            from_rest_outputs[output_name] = Output(
                type=output_type_mapping[output_value.job_output_type],
                path=output_value.uri,
                mode=OUTPUT_MOUNT_MAPPING_FROM_REST[output_value.mode] if output_value.mode else None,
                description=output_value.description,
                name=output_value.asset_name,
                version=output_value.asset_version,
            )
        else:
            msg = "unsupported JobOutput type: {}".format(output_value.job_output_type)
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    return from_rest_outputs
