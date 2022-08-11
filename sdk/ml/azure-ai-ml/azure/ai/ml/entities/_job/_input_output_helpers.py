# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import collections.abc
import re
from typing import Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, JobException, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import CustomModelJobInput as RestCustomModelJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import CustomModelJobOutput as RestCustomModelJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import InputDeliveryMode
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobInputType
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobOutputType, LiteralJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import MLFlowModelJobInput as RestMLFlowModelJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import MLFlowModelJobOutput as RestMLFlowModelJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import MLTableJobInput as RestMLTableJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import MLTableJobOutput as RestMLTableJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import OutputDeliveryMode
from azure.ai.ml._restclient.v2022_02_01_preview.models import TritonModelJobInput as RestTritonModelJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import TritonModelJobOutput as RestTritonModelJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import UriFileJobInput as RestUriFileJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import UriFileJobOutput as RestUriFileJobOutput
from azure.ai.ml._restclient.v2022_02_01_preview.models import UriFolderJobInput as RestUriFolderJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import UriFolderJobOutput as RestUriFolderJobOutput
from azure.ai.ml._restclient.v2022_06_01_preview.models import CustomModelJobInput as RestCustomModelJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import CustomModelJobOutput as RestCustomModelJobOutput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import JobInputType as JobInputType0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import JobOutputType as JobOutputType0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import LiteralJobInput as LiteralJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import MLFlowModelJobInput as RestMLFlowModelJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import MLFlowModelJobOutput as RestMLFlowModelJobOutput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import MLTableJobInput as RestMLTableJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import MLTableJobOutput as RestMLTableJobOutput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import TritonModelJobInput as RestTritonModelJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import TritonModelJobOutput as RestTritonModelJobOutput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import UriFileJobInput as RestUriFileJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import UriFileJobOutput as RestUriFileJobOutput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import UriFolderJobInput as RestUriFolderJobInput0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import UriFolderJobOutput as RestUriFolderJobOutput0601
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.input_output_entry import InputOutputEntry

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
}

OUTPUT_MOUNT_MAPPING_TO_REST = {
    InputOutputModes.MOUNT: OutputDeliveryMode.READ_WRITE_MOUNT,
    InputOutputModes.UPLOAD: OutputDeliveryMode.UPLOAD,
    InputOutputModes.RW_MOUNT: OutputDeliveryMode.READ_WRITE_MOUNT,
}


def get_output_type_mapping_from_rest(new_version=False):
    """Get output type mapping.

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
    """
    if new_version:
        return {
            JobOutputType0601.URI_FILE: AssetTypes.URI_FILE,
            JobOutputType0601.URI_FOLDER: AssetTypes.URI_FOLDER,
            JobOutputType0601.MLTABLE: AssetTypes.MLTABLE,
            JobOutputType0601.MLFLOW_MODEL: AssetTypes.MLFLOW_MODEL,
            JobOutputType0601.CUSTOM_MODEL: AssetTypes.CUSTOM_MODEL,
            JobOutputType0601.TRITON_MODEL: AssetTypes.TRITON_MODEL,
        }
    return {
        JobOutputType.URI_FILE: AssetTypes.URI_FILE,
        JobOutputType.URI_FOLDER: AssetTypes.URI_FOLDER,
        JobOutputType.ML_TABLE: AssetTypes.MLTABLE,
        JobOutputType.ML_FLOW_MODEL: AssetTypes.MLFLOW_MODEL,
        JobOutputType.CUSTOM_MODEL: AssetTypes.CUSTOM_MODEL,
        JobOutputType.TRITON_MODEL: AssetTypes.TRITON_MODEL,
    }


def get_input_rest_init_func_dict(new_version=False):
    """Get input rest init func dict.

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
    """
    if new_version:
        return {
            AssetTypes.URI_FILE: lambda uri, mode: RestUriFileJobInput0601(uri=uri, mode=mode),
            AssetTypes.URI_FOLDER: lambda uri, mode: RestUriFolderJobInput0601(uri=uri, mode=mode),
            AssetTypes.MLTABLE: lambda uri, mode: RestMLTableJobInput0601(uri=uri, mode=mode),
            AssetTypes.MLFLOW_MODEL: lambda uri, mode: RestMLFlowModelJobInput0601(uri=uri, mode=mode),
            AssetTypes.CUSTOM_MODEL: lambda uri, mode: RestCustomModelJobInput0601(uri=uri, mode=mode),
            AssetTypes.TRITON_MODEL: lambda uri, mode: RestTritonModelJobInput0601(uri=uri, mode=mode),
        }
    return {
        AssetTypes.URI_FILE: lambda uri, mode: RestUriFileJobInput(uri=uri, mode=mode),
        AssetTypes.URI_FOLDER: lambda uri, mode: RestUriFolderJobInput(uri=uri, mode=mode),
        AssetTypes.MLTABLE: lambda uri, mode: RestMLTableJobInput(uri=uri, mode=mode),
        AssetTypes.MLFLOW_MODEL: lambda uri, mode: RestMLFlowModelJobInput(uri=uri, mode=mode),
        AssetTypes.CUSTOM_MODEL: lambda uri, mode: RestCustomModelJobInput(uri=uri, mode=mode),
        AssetTypes.TRITON_MODEL: lambda uri, mode: RestTritonModelJobInput(uri=uri, mode=mode),
    }


def get_output_rest_init_func_dict(new_version=False):
    """Get output rest init func dict.

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
    """
    if new_version:
        return {
            AssetTypes.URI_FILE: lambda uri, mode: RestUriFileJobOutput0601(uri=uri, mode=mode),
            AssetTypes.URI_FOLDER: lambda uri, mode: RestUriFolderJobOutput0601(uri=uri, mode=mode),
            AssetTypes.MLTABLE: lambda uri, mode: RestMLTableJobOutput0601(uri=uri, mode=mode),
            AssetTypes.MLFLOW_MODEL: lambda uri, mode: RestMLFlowModelJobOutput0601(uri=uri, mode=mode),
            AssetTypes.CUSTOM_MODEL: lambda uri, mode: RestCustomModelJobOutput0601(uri=uri, mode=mode),
            AssetTypes.TRITON_MODEL: lambda uri, mode: RestTritonModelJobOutput0601(uri=uri, mode=mode),
        }
    return {
        AssetTypes.URI_FILE: lambda uri, mode: RestUriFileJobOutput(uri=uri, mode=mode),
        AssetTypes.URI_FOLDER: lambda uri, mode: RestUriFolderJobOutput(uri=uri, mode=mode),
        AssetTypes.MLTABLE: lambda uri, mode: RestMLTableJobOutput(uri=uri, mode=mode),
        AssetTypes.MLFLOW_MODEL: lambda uri, mode: RestMLFlowModelJobOutput(uri=uri, mode=mode),
        AssetTypes.CUSTOM_MODEL: lambda uri, mode: RestCustomModelJobOutput(uri=uri, mode=mode),
        AssetTypes.TRITON_MODEL: lambda uri, mode: RestTritonModelJobOutput(uri=uri, mode=mode),
    }


class BindingJobInput(LiteralJobInput):
    """Literal input type.

    All required parameters must be populated in order to send to Azure.

    :ivar description: Description for the input.
    :vartype description: str
    :ivar job_input_type: Required. [Required] Specifies the type of job.Constant filled by server.
     Possible values include: "Literal".
    :vartype job_input_type: str or ~azure.mgmt.machinelearningservices.models.JobInputType
    :ivar value: Required. [Required] Literal value for the input.
    :vartype value: str
    :keyword mode: Input Asset Delivery Mode. Possible values include: "ReadOnlyMount",
    "ReadWriteMount", "Download", "Direct", "EvalMount", "EvalDownload".
    :paramtype mode: str or ~azure.mgmt.machinelearningservices.models.InputDeliveryMode
    """

    _validation = {
        "job_input_type": {"required": True},
        "value": {"required": True, "pattern": r"[a-zA-Z0-9_]"},
    }

    _attribute_map = {
        "description": {"key": "description", "type": "str"},
        "job_input_type": {"key": "jobInputType", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "mode": {"key": "mode", "type": "str"},
    }

    def __init__(self, **kwargs):
        """
        :keyword description: Description for the input.
        :paramtype description: str
        :keyword value: Required. [Required] Literal value for the input.
        :paramtype value: str
        """
        super(LiteralJobInput, self).__init__(**kwargs)
        self.job_input_type = "Literal"  # type: str
        self.value = kwargs["value"]
        self.mode = kwargs.get("mode", None)


def build_input_output(
    item: Union[InputOutputEntry, Input, Output, str, bool, int, float],
    inputs: bool = True,
) -> Union[InputOutputEntry, Input, Output, str, bool, int, float]:
    if isinstance(item, InputOutputEntry) or isinstance(item, Input) or isinstance(item, Output):
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


def validate_inputs_for_command(command: str, inputs: Dict[str, Union[InputOutputEntry, Input]]) -> None:
    implicit_inputs = re.findall(r"\${{inputs\.([\w\.-]+)}}", command)
    for key in implicit_inputs:
        if inputs.get(key, None) is None:
            msg = "Inputs to job does not contain '{}' referenced in command"
            raise ValidationException(
                message=msg.format(key),
                no_personal_data_message=msg.format("[key]"),
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )


def validate_key_contains_allowed_characters(key: str) -> None:
    if re.match(r"^[a-zA-Z_]+[a-zA-Z0-9_]*$", key) is None:
        msg = "Key name  {} must be composed letters, numbers, and underscore"
        raise ValidationException(
            message=msg.format(key),
            no_personal_data_message=msg.format("[key]"),
            target=ErrorTarget.JOB,
            error_category=ErrorCategory.USER_ERROR,
        )


def to_rest_dataset_literal_inputs(
    inputs: Dict[str, Union[int, str, float, bool, Input]], new_version=False
) -> Dict[str, RestJobInput]:
    """Turns dataset and literal inputs into dictionary of REST JobInput

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
    :param inputs: Dictionary of dataset and literal inputs to job
    :type inputs: Dict[str, Union[int, str, float, bool, JobInput]]
    :return: A dictionary mapping input name to a ComponentJobInput or PipelineInput
    :rtype: Dict[str, Union[ComponentJobInput, PipelineInput]]
    """
    rest_inputs = {}
    # Pack up the inputs into REST format
    for input_name, input_value in inputs.items():
        validate_key_contains_allowed_characters(input_name)
        if isinstance(input_value, Input):
            if input_value.path and isinstance(input_value.path, str) and is_data_binding_expression(input_value.path):
                if input_value.mode:
                    input_data = BindingJobInput(
                        value=input_value.path, mode=INPUT_MOUNT_MAPPING_TO_REST[input_value.mode]
                    )
                else:
                    input_data = LiteralJobInput(value=input_value.path)
                if new_version:
                    # TODO: remove this
                    input_data.job_input_type = JobInputType0601.LITERAL
            else:
                target_init_func_dict = get_input_rest_init_func_dict(new_version=new_version)

                if input_value.type in target_init_func_dict:
                    input_data = target_init_func_dict[input_value.type](
                        input_value.path,
                        INPUT_MOUNT_MAPPING_TO_REST[input_value.mode.lower()] if input_value.mode else None,
                    )

                else:
                    msg = f"Job input type {input_value.type} is not supported as job input."
                    raise ValidationException(
                        message=msg,
                        no_personal_data_message=msg,
                        target=ErrorTarget.JOB,
                        error_category=ErrorCategory.USER_ERROR,
                    )
        elif input_value is None:
            # If the input is None, we need to pass the origin None to the REST API
            input_data = LiteralJobInput0601(value=None) if new_version else LiteralJobInput(value=None)
        else:
            # otherwise, the input is a literal input
            if isinstance(input_value, dict):
                if "mode" in input_value:
                    input_data = BindingJobInput(value=str(input_value["value"]), mode=input_value["mode"])
                else:
                    input_data = LiteralJobInput(value=str(input_value["value"]))
            else:
                input_data = LiteralJobInput(value=str(input_value))
            if new_version:
                # TODO: remove this
                input_data.job_input_type = JobInputType0601.LITERAL
        # Pack up inputs into PipelineInputs or ComponentJobInputs depending on caller
        rest_inputs[input_name] = input_data
    return rest_inputs


def from_rest_inputs_to_dataset_literal(
    inputs: Dict[str, RestJobInput], new_version=False
) -> Dict[str, Union[int, str, float, bool, Input]]:
    """Turns REST dataset and literal inputs into the SDK format.

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
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

        type_transfer_dict = get_output_type_mapping_from_rest(new_version=new_version)

        if input_value.job_input_type in type_transfer_dict:
            if input_value.uri:
                path = input_value.uri

                input_data = Input(
                    type=type_transfer_dict[input_value.job_input_type],
                    path=path,
                    mode=INPUT_MOUNT_MAPPING_FROM_REST[input_value.mode] if input_value.mode else None,
                )
        elif input_value.job_input_type in (JobInputType.LITERAL, JobInputType0601.LITERAL):
            # otherwise, the input is a literal, so just unpack the InputData value field
            input_data = input_value.value
        else:
            msg = f"Job input type {input_value.job_input_type} is not supported as job input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

        from_rest_inputs[input_name] = input_data
    return from_rest_inputs


def to_rest_data_outputs(outputs: Dict[str, Output], new_version=False) -> Dict[str, RestJobOutput]:
    """Turns job outputs into REST format

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
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
            output_cls = RestUriFolderJobOutput0601 if new_version else RestUriFolderJobOutput
            rest_outputs[output_name] = output_cls(mode=None)
        else:
            target_init_func_dict = get_output_rest_init_func_dict(new_version=new_version)

            output_value_type = output_value.type if output_value.type else AssetTypes.URI_FOLDER
            if output_value_type in target_init_func_dict:
                output = target_init_func_dict[output_value_type](
                    output_value.path,
                    OUTPUT_MOUNT_MAPPING_TO_REST[output_value.mode.lower()] if output_value.mode else None,
                )
            else:
                msg = "unsupported JobOutput type: {}".format(output_value.type)
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.USER_ERROR,
                )
            rest_outputs[output_name] = output
    return rest_outputs


def from_rest_data_outputs(outputs: Dict[str, RestJobOutput], new_version=False) -> Dict[str, Output]:
    """Turns REST outputs into the SDK format

    :param new_version: Use new model for inputs/outputs if new_version is true, as 0501 and later version
        change enum (like JobInputType) from camel to snake.
        Side effect by https://msdata.visualstudio.com/Vienna/_git/vienna/pullrequest/783594.
        TODO: Remove this after all Job and Component migrate to new version afterwards.
    :type new_version: bool
    :param outputs: Dictionary of dataset and literal inputs to job
    :type outputs: Dict[str, RestJobOutput]
    :return: A dictionary mapping input name to a InputOutputEntry
    :rtype: Dict[str, JobOutput]
    """
    output_type_mapping = get_output_type_mapping_from_rest(new_version=new_version)
    from_rest_outputs = {}
    if outputs is None:
        return {}
    for output_name, output_value in outputs.items():
        if output_value is None:
            continue
        if output_value.job_output_type in output_type_mapping:
            from_rest_outputs[output_name] = Output(
                type=output_type_mapping[output_value.job_output_type],
                path=output_value.uri,
                mode=OUTPUT_MOUNT_MAPPING_FROM_REST[output_value.mode] if output_value.mode else None,
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
