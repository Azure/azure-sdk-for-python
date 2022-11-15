# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import json
import os
import shutil
from typing import Any, Dict, List, Optional, Union
from unittest import mock

import msrest
from marshmallow.exceptions import ValidationError

from azure.ai.ml._restclient.v2022_02_01_preview.models import JobInputType as JobInputType02
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobInputType as JobInputType10
from azure.ai.ml._schema._datastore import (
    AzureBlobSchema,
    AzureDataLakeGen1Schema,
    AzureDataLakeGen2Schema,
    AzureFileSchema,
)
from azure.ai.ml._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from azure.ai.ml._schema._deployment.online.online_deployment import (
    KubernetesOnlineDeploymentSchema,
    ManagedOnlineDeploymentSchema,
)
from azure.ai.ml._schema._endpoint.batch.batch_endpoint import BatchEndpointSchema
from azure.ai.ml._schema._endpoint.online.online_endpoint import (
    KubernetesOnlineEndpointSchema,
    ManagedOnlineEndpointSchema,
)
from azure.ai.ml._schema._sweep import SweepJobSchema
from azure.ai.ml._schema.assets.data import DataSchema
from azure.ai.ml._schema.assets.environment import EnvironmentSchema
from azure.ai.ml._schema.assets.model import ModelSchema
from azure.ai.ml._schema.component.command_component import CommandComponentSchema
from azure.ai.ml._schema.component.parallel_component import ParallelComponentSchema
from azure.ai.ml._schema.compute.aml_compute import AmlComputeSchema
from azure.ai.ml._schema.compute.compute_instance import ComputeInstanceSchema
from azure.ai.ml._schema.compute.virtual_machine_compute import VirtualMachineComputeSchema
from azure.ai.ml._schema.job import CommandJobSchema, ParallelJobSchema
from azure.ai.ml._schema.pipeline.pipeline_job import PipelineJobSchema
from azure.ai.ml._schema.schedule.schedule import ScheduleSchema
from azure.ai.ml._schema.workspace import WorkspaceSchema
from azure.ai.ml.constants._common import (
    REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT,
    CommonYamlFields,
    YAMLRefDocLinks,
    YAMLRefDocSchemaNames,
)
from azure.ai.ml.constants._endpoint import EndpointYamlFields
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

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
    ScheduleSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(
        YAMLRefDocSchemaNames.SCHEDULE, YAMLRefDocLinks.SCHEDULE
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


def find_type_in_override(params_override: list = None) -> Optional[str]:
    params_override = params_override or []
    for override in params_override:
        if CommonYamlFields.TYPE in override:
            return override[CommonYamlFields.TYPE]
    return None


def is_compute_in_override(params_override: list = None) -> bool:
    return any([EndpointYamlFields.COMPUTE in param for param in params_override])


def load_from_dict(schema: Any, data: Dict, context: Dict, additional_message: str = "", **kwargs):
    try:
        return schema(context=context).load(data, **kwargs)
    except ValidationError as e:
        pretty_error = json.dumps(e.normalized_messages(), indent=2)
        raise ValidationError(decorate_validation_error(schema, pretty_error, additional_message))


def decorate_validation_error(schema: Any, pretty_error: str, additional_message: str = "") -> str:
    ref_doc_link_error_msg = REF_DOC_ERROR_MESSAGE_MAP.get(schema, "")
    if ref_doc_link_error_msg:
        additional_message += f"\n{ref_doc_link_error_msg}"
    additional_message += (
        "\nThe easiest way to author a specification file is using IntelliSense and auto-completion Azure ML VS "
        "code extension provides: https://code.visualstudio.com/docs/datascience/azure-machine-learning. "
        "To set up: https://docs.microsoft.com/azure/machine-learning/how-to-setup-vs-code"
    )
    return f"Validation for {schema.__name__} failed:\n\n {pretty_error} \n\n {additional_message}"


def get_md5_string(text):
    try:
        return hashlib.md5(text.encode("utf8")).hexdigest()  # nosec
    except Exception as ex:
        raise ex


def validate_attribute_type(attrs_to_check: dict, attr_type_map: dict):
    """Validate if attributes of object are set with valid types, raise error
    if don't.

    :param attrs_to_check: Mapping from attributes name to actual value.
    :param attr_type_map: Mapping from attributes name to tuple of expecting type
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

def is_empty_target(obj):
    """Determines if it's empty target"""
    return (obj is None
            # some objs have overloaded "==" and will cause error. e.g CommandComponent obj
            or (isinstance(obj, dict) and len(obj) == 0)
        )

def convert_ordered_dict_to_dict(target_object: Union[Dict, List], remove_empty=True) -> Union[Dict, List]:
    """Convert ordered dict to dict. Remove keys with None value.

    This is a workaround for rest request must be in dict instead of
    ordered dict.
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


def _general_copy(src, dst):
    """Wrapped `shutil.copy2` function for possible "Function not implemented"
    exception raised by it.

    Background: `shutil.copy2` will throw OSError when dealing with Azure File.
    See https://stackoverflow.com/questions/51616058 for more information.
    """
    if hasattr(os, "listxattr"):
        with mock.patch("shutil._copyxattr", return_value=[]):
            shutil.copy2(src, dst)
    else:
        shutil.copy2(src, dst)


def get_rest_dict_for_node_attrs(target_obj, clear_empty_value=False):
    """Convert object to dict and convert OrderedDict to dict.
    Allow data binding expression as value, disregarding of the type defined in rest object.
    """
    # pylint: disable=too-many-return-statements
    if target_obj is None:
        return None
    if isinstance(target_obj, dict):
        result = {}
        for key, value in target_obj.items():
            if value is None:
                continue
            if key in ["additional_properties"]:
                continue
            result[key] = get_rest_dict_for_node_attrs(value, clear_empty_value)
        return result
    if isinstance(target_obj, list):
        result = []
        for item in target_obj:
            result.append(get_rest_dict_for_node_attrs(item, clear_empty_value))
        return result
    if isinstance(target_obj, RestTranslatableMixin):
        # note that the rest object may be invalid as data binding expression may not fit
        # rest object structure
        # pylint: disable=protected-access
        from azure.ai.ml.entities._credentials import _BaseIdentityConfiguration
        if isinstance(target_obj, _BaseIdentityConfiguration):
            return get_rest_dict_for_node_attrs(target_obj._to_job_rest_object(), clear_empty_value=clear_empty_value)
        return get_rest_dict_for_node_attrs(target_obj._to_rest_object(), clear_empty_value=clear_empty_value)

    if isinstance(target_obj, msrest.serialization.Model):
        # can't use result.as_dict() as data binding expression may not fit rest object structure
        return get_rest_dict_for_node_attrs(target_obj.__dict__, clear_empty_value=clear_empty_value)

    if not isinstance(target_obj, (str, int, float, bool)):
        raise ValueError("Unexpected type {}".format(type(target_obj)))

    return target_obj


class _DummyRestModelFromDict(msrest.serialization.Model):
    """A dummy rest model that can be initialized from dict, return base_dict[attr_name]
    for getattr(self, attr_name) when attr_name is a public attrs; return None when trying to get
    a non-existent public attribute.
    """

    def __init__(self, rest_dict):
        self._rest_dict = rest_dict or {}
        super().__init__()

    def __getattribute__(self, item):
        if not item.startswith("_"):
            return self._rest_dict.get(item, None)
        return super().__getattribute__(item)


def from_rest_dict_to_dummy_rest_object(rest_dict):
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
    """
    if rest_dict is None or isinstance(rest_dict, dict):
        return _DummyRestModelFromDict(rest_dict)
    raise ValueError("Unexpected type {}".format(type(rest_dict)))


def extract_label(input_str: str):
    if "@" in input_str:
        return input_str.rsplit("@", 1)
    return input_str, None


def resolve_pipeline_parameters(pipeline_parameters: dict, remove_empty=False):
    """Resolve pipeline parameters.

    1. Resolve BaseNode and OutputsAttrDict type to NodeOutput.
    2. Remove empty value (optional).
    """

    if pipeline_parameters is None:
        return
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


def resolve_pipeline_parameter(data):
    from azure.ai.ml.entities._builders.base_node import BaseNode
    from azure.ai.ml.entities._builders.pipeline import Pipeline
    from azure.ai.ml.entities._job.pipeline._io import OutputsAttrDict
    from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression

    if isinstance(data, PipelineExpression):
        data = data.resolve()
    if isinstance(data, (BaseNode, Pipeline)):
        # For the case use a node/pipeline node as the input, we use its only one output as the real input.
        # Here we set node = node.outputs, then the following logic will get the output object.
        data = data.outputs
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
        data = list(data.values())[0]
    return data


def normalize_job_input_output_type(input_output_value):
    """
    We have changed the api starting v2022_06_01_preview version and there are some api interface changes, which will
    result in pipeline submitted by v2022_02_01_preview can't be parsed correctly. And this will block
    az ml job list/show. So we convert the input/output type of camel to snake to be compatible with the Jun/Oct api.
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
