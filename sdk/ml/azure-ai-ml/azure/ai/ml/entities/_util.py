# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import hashlib
import json
import os
import shutil
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union, cast, overload
from unittest import mock

import msrest
from marshmallow.exceptions import ValidationError

from .._restclient.v2022_02_01_preview.models import JobInputType as JobInputType02
from .._restclient.v2023_04_01_preview.models import JobInput as RestJobInput
from .._restclient.v2023_04_01_preview.models import JobInputType as JobInputType10
from .._restclient.v2023_04_01_preview.models import JobOutput as RestJobOutput
from .._schema._datastore import AzureBlobSchema, AzureDataLakeGen1Schema, AzureDataLakeGen2Schema, AzureFileSchema
from .._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from .._schema._deployment.online.online_deployment import (
    KubernetesOnlineDeploymentSchema,
    ManagedOnlineDeploymentSchema,
)
from .._schema._endpoint.batch.batch_endpoint import BatchEndpointSchema
from .._schema._endpoint.online.online_endpoint import KubernetesOnlineEndpointSchema, ManagedOnlineEndpointSchema
from .._schema._sweep import SweepJobSchema
from .._schema.assets.data import DataSchema
from .._schema.assets.environment import EnvironmentSchema
from .._schema.assets.model import ModelSchema
from .._schema.component.command_component import CommandComponentSchema
from .._schema.component.parallel_component import ParallelComponentSchema
from .._schema.compute.aml_compute import AmlComputeSchema
from .._schema.compute.compute_instance import ComputeInstanceSchema
from .._schema.compute.virtual_machine_compute import VirtualMachineComputeSchema
from .._schema.job import CommandJobSchema, ParallelJobSchema
from .._schema.pipeline.pipeline_job import PipelineJobSchema
from .._schema.schedule.schedule import JobScheduleSchema
from .._schema.workspace import WorkspaceSchema
from .._utils.utils import is_internal_component_data, try_enable_internal_components
from ..constants._common import (
    REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT,
    CommonYamlFields,
    YAMLRefDocLinks,
    YAMLRefDocSchemaNames,
)
from ..constants._component import NodeType
from ..constants._endpoint import EndpointYamlFields
from ..entities._mixins import RestTranslatableMixin
from ..exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._inputs_outputs import Output
    from azure.ai.ml.entities._job.pipeline._io import NodeOutput

# Maps schema class name to formatted error message pointing to Microsoft docs reference page for a schema's YAML
REF_DOC_ERROR_MESSAGE_MAP = {
    DataSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(YAMLRefDocSchemaNames.DATA, YAMLRefDocLinks.DATA),
    EnvironmentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.ENVIRONMENT, YAMLRefDocLinks.ENVIRONMENT
    ),
    ModelSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(YAMLRefDocSchemaNames.MODEL, YAMLRefDocLinks.MODEL),
    CommandComponentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.COMMAND_COMPONENT, YAMLRefDocLinks.COMMAND_COMPONENT
    ),
    ParallelComponentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.PARALLEL_COMPONENT, YAMLRefDocLinks.PARALLEL_COMPONENT
    ),
    AmlComputeSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.AML_COMPUTE, YAMLRefDocLinks.AML_COMPUTE
    ),
    ComputeInstanceSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.COMPUTE_INSTANCE, YAMLRefDocLinks.COMPUTE_INSTANCE
    ),
    VirtualMachineComputeSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.VIRTUAL_MACHINE_COMPUTE,
        YAMLRefDocLinks.VIRTUAL_MACHINE_COMPUTE,
    ),
    AzureDataLakeGen1Schema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.DATASTORE_DATA_LAKE_GEN_1,
        YAMLRefDocLinks.DATASTORE_DATA_LAKE_GEN_1,
    ),
    AzureBlobSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.DATASTORE_BLOB, YAMLRefDocLinks.DATASTORE_BLOB
    ),
    AzureFileSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.DATASTORE_FILE, YAMLRefDocLinks.DATASTORE_FILE
    ),
    AzureDataLakeGen2Schema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.DATASTORE_DATA_LAKE_GEN_2,
        YAMLRefDocLinks.DATASTORE_DATA_LAKE_GEN_2,
    ),
    BatchEndpointSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.BATCH_ENDPOINT, YAMLRefDocLinks.BATCH_ENDPOINT
    ),
    KubernetesOnlineEndpointSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.ONLINE_ENDPOINT, YAMLRefDocLinks.ONLINE_ENDPOINT
    ),
    ManagedOnlineEndpointSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.ONLINE_ENDPOINT, YAMLRefDocLinks.ONLINE_ENDPOINT
    ),
    BatchDeploymentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.BATCH_DEPLOYMENT, YAMLRefDocLinks.BATCH_DEPLOYMENT
    ),
    ManagedOnlineDeploymentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.MANAGED_ONLINE_DEPLOYMENT,
        YAMLRefDocLinks.MANAGED_ONLINE_DEPLOYMENT,
    ),
    KubernetesOnlineDeploymentSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.KUBERNETES_ONLINE_DEPLOYMENT,
        YAMLRefDocLinks.KUBERNETES_ONLINE_DEPLOYMENT,
    ),
    PipelineJobSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.PIPELINE_JOB, YAMLRefDocLinks.PIPELINE_JOB
    ),
    JobScheduleSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.JOB_SCHEDULE, YAMLRefDocLinks.JOB_SCHEDULE
    ),
    SweepJobSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.SWEEP_JOB, YAMLRefDocLinks.SWEEP_JOB
    ),
    CommandJobSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.COMMAND_JOB, YAMLRefDocLinks.COMMAND_JOB
    ),
    ParallelJobSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.PARALLEL_JOB, YAMLRefDocLinks.PARALLEL_JOB
    ),
    WorkspaceSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.WORKSPACE, YAMLRefDocLinks.WORKSPACE
    ),
}


def find_field_in_override(field: str, params_override: Optional[list] = None) -> Optional[str]:
    """Find specific field in params override.

    :param field: The name of the field to find
    :type field: str
    :param params_override: The params override
    :type params_override: Optional[list]
    :return: The type
    :rtype: Optional[str]
    """
    params_override = params_override or []
    for override in params_override:
        if field in override:
            res: Optional[str] = override[field]
            return res
    return None


def find_type_in_override(params_override: Optional[list] = None) -> Optional[str]:
    """Find type in params override.

    :param params_override: The params override
    :type params_override: Optional[list]
    :return: The type
    :rtype: Optional[str]
    """
    return find_field_in_override(CommonYamlFields.TYPE, params_override)


def is_compute_in_override(params_override: Optional[list] = None) -> bool:
    """Check if compute is in params override.

    :param params_override: The params override
    :type params_override: Optional[list]
    :return: True if compute is in params override
    :rtype: bool
    """
    if params_override is not None:
        return any(EndpointYamlFields.COMPUTE in param for param in params_override)
    return False


def load_from_dict(schema: Any, data: Dict, context: Dict, additional_message: str = "", **kwargs: Any) -> Any:
    """Load data from dict.

    :param schema: The schema to load data with.
    :type schema: Any
    :param data: The data to load.
    :type data: Dict
    :param context: The context of the data.
    :type context: Dict
    :param additional_message: The additional message to add to the error message.
    :type additional_message: str
    :return: The loaded data.
    :rtype: Any
    """
    try:
        return schema(context=context).load(data, **kwargs)
    except ValidationError as e:
        pretty_error = json.dumps(e.normalized_messages(), indent=2)
        raise ValidationError(decorate_validation_error(schema, pretty_error, additional_message)) from e


def decorate_validation_error(schema: Any, pretty_error: str, additional_message: str = "") -> str:
    """Decorate validation error with additional message.

    :param schema: The schema that failed validation.
    :type schema: Any
    :param pretty_error: The pretty error message.
    :type pretty_error: str
    :param additional_message: The additional message to add.
    :type additional_message: str
    :return: The decorated error message.
    :rtype: str
    """
    ref_doc_link_error_msg = REF_DOC_ERROR_MESSAGE_MAP.get(schema, "")
    if ref_doc_link_error_msg:
        additional_message += f"\n{ref_doc_link_error_msg}"
    additional_message += (
        "\nThe easiest way to author a specification file is using IntelliSense and auto-completion Azure ML VS "
        "code extension provides: https://code.visualstudio.com/docs/datascience/azure-machine-learning. "
        "To set up: https://docs.microsoft.com/azure/machine-learning/how-to-setup-vs-code"
    )
    return f"Validation for {schema.__name__} failed:\n\n {pretty_error} \n\n {additional_message}"


def get_md5_string(text: Optional[str]) -> str:
    """Get md5 string for a given text.

    :param text: The text to get md5 string for.
    :type text: str
    :return: The md5 string.
    :rtype: str
    """
    try:
        if text is not None:
            return hashlib.md5(text.encode("utf8")).hexdigest()  # nosec
        return ""
    except Exception as ex:
        raise ex


def validate_attribute_type(attrs_to_check: Dict[str, Any], attr_type_map: Dict[str, Type]) -> None:
    """Validate if attributes of object are set with valid types, raise error
    if don't.

    :param attrs_to_check: Mapping from attributes name to actual value.
    :type attrs_to_check: Dict[str, Any]
    :param attr_type_map: Mapping from attributes name to tuple of expecting type
    :type attr_type_map: Dict[str, Type]
    """
    #
    kwargs = attrs_to_check.get("kwargs", {})
    attrs_to_check.update(kwargs)
    for attr, expecting_type in attr_type_map.items():
        attr_val = attrs_to_check.get(attr, None)
        if attr_val is not None and not isinstance(attr_val, expecting_type):
            msg = "Expecting {} for {}, got {} instead."
            raise ValidationException(
                message=msg.format(expecting_type, attr, type(attr_val)),
                no_personal_data_message=msg.format(expecting_type, "[attr]", type(attr_val)),
                target=ErrorTarget.GENERAL,
                error_type=ValidationErrorType.INVALID_VALUE,
            )


def is_empty_target(obj: Optional[Dict]) -> bool:
    """Determines if it's empty target

    :param obj: The object to check
    :type obj: Optional[Dict]
    :return: True if obj is None or an empty Dict
    :rtype: bool
    """
    return (
        obj is None
        # some objs have overloaded "==" and will cause error. e.g CommandComponent obj
        or (isinstance(obj, dict) and len(obj) == 0)
    )


def convert_ordered_dict_to_dict(target_object: Union[Dict, List], remove_empty: bool = True) -> Union[Dict, List]:
    """Convert ordered dict to dict. Remove keys with None value.
    This is a workaround for rest request must be in dict instead of
    ordered dict.

    :param target_object: The object to convert
    :type target_object: Union[Dict, List]
    :param remove_empty: Whether to omit values that are None or empty dictionaries. Defaults to True.
    :type remove_empty: bool
    :return: Converted ordered dict with removed None values
    :rtype: Union[Dict, List]
    """
    # OrderedDict can appear nested in a list
    if isinstance(target_object, list):
        new_list = []
        for item in target_object:
            item = convert_ordered_dict_to_dict(item)
            if not is_empty_target(item) or not remove_empty:
                new_list.append(item)
        return new_list
    if isinstance(target_object, dict):
        new_dict = {}
        for key, value in target_object.items():
            value = convert_ordered_dict_to_dict(value)
            if not is_empty_target(value) or not remove_empty:
                new_dict[key] = value
        return new_dict
    return target_object


def _general_copy(src: Union[str, os.PathLike], dst: Union[str, os.PathLike], make_dirs: bool = True) -> None:
    """Wrapped `shutil.copy2` function for possible "Function not implemented" exception raised by it.

    Background: `shutil.copy2` will throw OSError when dealing with Azure File.
    See https://stackoverflow.com/questions/51616058 for more information.

    :param src: The source path to copy from
    :type src: Union[str, os.PathLike]
    :param dst: The destination path to copy to
    :type dst: Union[str, os.PathLike]
    :param make_dirs: Whether to ensure the destination path exists. Defaults to True.
    :type make_dirs: bool
    """
    if make_dirs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    if hasattr(os, "listxattr"):
        with mock.patch("shutil._copyxattr", return_value=[]):
            shutil.copy2(src, dst)
    else:
        shutil.copy2(src, dst)


def _dump_data_binding_expression_in_fields(obj: Any) -> Any:
    for key, value in obj.__dict__.items():
        # PipelineInput is subclass of NodeInput
        from ._job.pipeline._io import NodeInput

        if isinstance(value, NodeInput):
            obj.__dict__[key] = str(value)
        elif isinstance(value, RestTranslatableMixin):
            _dump_data_binding_expression_in_fields(value)
    return obj


T = TypeVar("T")


def get_rest_dict_for_node_attrs(
    target_obj: Union[T, str], clear_empty_value: bool = False
) -> Union[T, Dict, List, str, int, float, bool]:
    """Convert object to dict and convert OrderedDict to dict.
    Allow data binding expression as value, disregarding of the type defined in rest object.

    :param target_obj: The object to convert
    :type target_obj: T
    :param clear_empty_value: Whether to clear empty values. Defaults to False.
    :type clear_empty_value: bool
    :return: The translated dict, or the the original object
    :rtype: Union[T, Dict]
    """
    # pylint: disable=too-many-return-statements
    from azure.ai.ml.entities._job.pipeline._io import PipelineInput

    if target_obj is None:
        return None
    if isinstance(target_obj, dict):
        result_dict: dict = {}
        for key, value in target_obj.items():
            if value is None:
                continue
            if key in ["additional_properties"]:
                continue
            result_dict[key] = get_rest_dict_for_node_attrs(value, clear_empty_value)
        return result_dict
    if isinstance(target_obj, list):
        result_list: list = []
        for item in target_obj:
            result_list.append(get_rest_dict_for_node_attrs(item, clear_empty_value))
        return result_list
    if isinstance(target_obj, RestTranslatableMixin):
        # note that the rest object may be invalid as data binding expression may not fit
        # rest object structure
        # pylint: disable=protected-access
        _target_obj = _dump_data_binding_expression_in_fields(copy.deepcopy(target_obj))

        from azure.ai.ml.entities._credentials import _BaseIdentityConfiguration

        if isinstance(_target_obj, _BaseIdentityConfiguration):
            # TODO: Bug Item number: 2883348
            return get_rest_dict_for_node_attrs(
                _target_obj._to_job_rest_object(), clear_empty_value=clear_empty_value  # type: ignore
            )
        return get_rest_dict_for_node_attrs(_target_obj._to_rest_object(), clear_empty_value=clear_empty_value)

    if isinstance(target_obj, msrest.serialization.Model):
        # can't use result.as_dict() as data binding expression may not fit rest object structure
        return get_rest_dict_for_node_attrs(target_obj.__dict__, clear_empty_value=clear_empty_value)

    if isinstance(target_obj, PipelineInput):
        return get_rest_dict_for_node_attrs(str(target_obj), clear_empty_value=clear_empty_value)

    if not isinstance(target_obj, (str, int, float, bool)):
        raise ValueError("Unexpected type {}".format(type(target_obj)))

    return target_obj


class _DummyRestModelFromDict(msrest.serialization.Model):
    """A dummy rest model that can be initialized from dict, return base_dict[attr_name]
    for getattr(self, attr_name) when attr_name is a public attrs; return None when trying to get
    a non-existent public attribute.
    """

    def __init__(self, rest_dict: Optional[dict]):
        self._rest_dict = rest_dict or {}
        super().__init__()

    def __getattribute__(self, item: str) -> Any:
        if not item.startswith("_"):
            return self._rest_dict.get(item, None)
        return super().__getattribute__(item)


def from_rest_dict_to_dummy_rest_object(rest_dict: Optional[Dict]) -> _DummyRestModelFromDict:
    """Create a dummy rest object based on a rest dict, which is a primitive dict containing
    attributes in a rest object.
    For example, for a rest object class like:
        class A(msrest.serialization.Model):
            def __init__(self, a, b):
                self.a = a
                self.b = b
        rest_object = A(1, None)
        rest_dict = {"a": 1}
        regenerated_rest_object = from_rest_dict_to_fake_rest_object(rest_dict)
        assert regenerated_rest_object.a == 1
        assert regenerated_rest_object.b is None

    :param rest_dict: The rest dict
    :type rest_dict: Optional[Dict]
    :return: A dummy rest object
    :rtype: _DummyRestModelFromDict
    """
    if rest_dict is None or isinstance(rest_dict, dict):
        return _DummyRestModelFromDict(rest_dict)
    raise ValueError("Unexpected type {}".format(type(rest_dict)))


def extract_label(input_str: str) -> Union[Tuple, List]:
    """Extract label from input string.

    :param input_str: The input string
    :type input_str: str
    :return: The rest of the string and the label
    :rtype: Tuple[str, Optional[str]]
    """
    if not isinstance(input_str, str):
        return None, None
    if "@" in input_str:
        return input_str.rsplit("@", 1)
    return input_str, None


@overload
def resolve_pipeline_parameters(pipeline_parameters: None, remove_empty: bool = False) -> None: ...


@overload
def resolve_pipeline_parameters(
    pipeline_parameters: Dict[str, T], remove_empty: bool = False
) -> Dict[str, Union[T, str, "NodeOutput"]]: ...


def resolve_pipeline_parameters(pipeline_parameters: Optional[Dict], remove_empty: bool = False) -> Optional[Dict]:
    """Resolve pipeline parameters.

    1. Resolve BaseNode and OutputsAttrDict type to NodeOutput.
    2. Remove empty value (optional).

    :param pipeline_parameters: The pipeline parameters
    :type pipeline_parameters: Optional[Dict[str, T]]
    :param remove_empty: Whether to remove None values. Defaults to False.
    :type remove_empty: bool
    :return:
        * None if pipeline_parameters is None
        * The resolved dict of pipeline parameters
    :rtype: Optional[Dict[str, Union[T, str, "NodeOutput"]]]
    """

    if pipeline_parameters is None:
        return None
    if not isinstance(pipeline_parameters, dict):
        raise ValidationException(
            message="pipeline_parameters must in dict {parameter: value} format.",
            no_personal_data_message="pipeline_parameters must in dict {parameter: value} format.",
            target=ErrorTarget.PIPELINE,
        )

    updated_parameters = {}
    for k, v in pipeline_parameters.items():
        v = resolve_pipeline_parameter(v)
        if v is None and remove_empty:
            continue
        updated_parameters[k] = v
    pipeline_parameters = updated_parameters
    return pipeline_parameters


def resolve_pipeline_parameter(data: Any) -> Union[T, str, "NodeOutput"]:
    """Resolve pipeline parameter.
    1. Resolve BaseNode and OutputsAttrDict type to NodeOutput.
    2. Remove empty value (optional).
    :param data: The pipeline parameter
    :type data: T
    :return:
        * None if data is None
        * The resolved pipeline parameter
    :rtype: Union[T, str, "NodeOutput"]
    """
    from azure.ai.ml.entities._builders.base_node import BaseNode
    from azure.ai.ml.entities._builders.pipeline import Pipeline
    from azure.ai.ml.entities._job.pipeline._io import NodeOutput, OutputsAttrDict
    from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression

    if isinstance(data, PipelineExpression):
        data = cast(Union[str, BaseNode], data.resolve())
    if isinstance(data, (BaseNode, Pipeline)):
        # For the case use a node/pipeline node as the input, we use its only one output as the real input.
        # Here we set node = node.outputs, then the following logic will get the output object.
        data = cast(OutputsAttrDict, data.outputs)
    if isinstance(data, OutputsAttrDict):
        # For the case that use the outputs of another component as the input,
        # we use the only one output as the real input,
        # if multiple outputs are provided, an exception is raised.
        output_len = len(data)
        if output_len != 1:
            raise ValidationException(
                message="Setting input failed: Exactly 1 output is required, got %d. (%s)" % (output_len, data),
                no_personal_data_message="multiple output(s) found of specified outputs, exactly 1 output required.",
                target=ErrorTarget.PIPELINE,
            )
        data = cast(NodeOutput, list(data.values())[0])
    return cast(Union[T, str, "NodeOutput"], data)


def normalize_job_input_output_type(input_output_value: Union[RestJobOutput, RestJobInput, Dict]) -> None:
    """Normalizes the `job_input_type`, `job_output_type`, and `type` keys for REST job output and input objects.

    :param input_output_value: Either a REST input or REST output of a job
    :type input_output_value: Union[RestJobOutput, RestJobInput, Dict]

    .. note::

        We have changed the api starting v2022_06_01_preview version and there are some api interface changes,
        which will result in pipeline submitted by v2022_02_01_preview can't be parsed correctly. And this will block
        az ml job list/show. So we convert the input/output type of camel to snake to be compatible with the Jun/Oct
        api.

    """

    FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING = {
        JobInputType02.CUSTOM_MODEL: JobInputType10.CUSTOM_MODEL,
        JobInputType02.LITERAL: JobInputType10.LITERAL,
        JobInputType02.ML_FLOW_MODEL: JobInputType10.MLFLOW_MODEL,
        JobInputType02.ML_TABLE: JobInputType10.MLTABLE,
        JobInputType02.TRITON_MODEL: JobInputType10.TRITON_MODEL,
        JobInputType02.URI_FILE: JobInputType10.URI_FILE,
        JobInputType02.URI_FOLDER: JobInputType10.URI_FOLDER,
    }
    if (
        hasattr(input_output_value, "job_input_type")
        and input_output_value.job_input_type in FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING
    ):
        input_output_value.job_input_type = FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING[input_output_value.job_input_type]
    elif (
        hasattr(input_output_value, "job_output_type")
        and input_output_value.job_output_type in FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING
    ):
        input_output_value.job_output_type = FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING[input_output_value.job_output_type]
    elif isinstance(input_output_value, dict):
        job_output_type = input_output_value.get("job_output_type", None)
        job_input_type = input_output_value.get("job_input_type", None)
        job_type = input_output_value.get("type", None)

        if job_output_type and job_output_type in FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING:
            input_output_value["job_output_type"] = FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING[job_output_type]
        if job_input_type and job_input_type in FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING:
            input_output_value["job_input_type"] = FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING[job_input_type]
        if job_type and job_type in FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING:
            input_output_value["type"] = FEB_JUN_JOB_INPUT_OUTPUT_TYPE_MAPPING[job_type]


def get_type_from_spec(data: dict, *, valid_keys: Iterable[str]) -> str:
    """Get the type of the node or component from the yaml spec.

    Yaml spec must have a key named "type" and exception will be raised if it's not once of valid_keys.

    If internal components are enabled, related factory and schema will be updated.

    :param data: The data
    :type data: dict
    :keyword valid_keys: An iterable of valid types
    :paramtype valid_keys: Iterable[str]
    :return: The type of the node or component
    :rtype: str
    """
    _type, _ = extract_label(data.get(CommonYamlFields.TYPE, None))

    # we should keep at least 1 place outside _internal to enable internal components
    # and this is the only place
    try_enable_internal_components()
    # todo: refine Hard code for now to support different task type for DataTransfer component
    if _type == NodeType.DATA_TRANSFER:
        _type = "_".join([NodeType.DATA_TRANSFER, data.get("task", " ")])
    if _type not in valid_keys:
        is_internal_component_data(data, raise_if_not_enabled=True)

        raise ValidationException(
            message="Unsupported component type: %s." % _type,
            target=ErrorTarget.COMPONENT,
            no_personal_data_message="Unsupported component type",
            error_category=ErrorCategory.USER_ERROR,
        )
    res: str = _type
    return res


def copy_output_setting(source: Union["Output", "NodeOutput"], target: "NodeOutput") -> None:
    """Copy node output setting from source to target.

    Currently only path, name, version will be copied.

    :param source: The Output to copy from
    :type source: Union[Output, NodeOutput]
    :param target: The Output to copy to
    :type target: NodeOutput
    """
    # pylint: disable=protected-access
    from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineOutput

    if not isinstance(source, NodeOutput):
        # Only copy when source is an output builder
        return
    source_data = source._data
    if isinstance(source_data, PipelineOutput):
        source_data = source_data._data
    if source_data:
        target._data = copy.deepcopy(source_data)
    # copy pipeline component output's node output to subgraph builder
    if source._binding_output is not None:
        target._binding_output = source._binding_output
