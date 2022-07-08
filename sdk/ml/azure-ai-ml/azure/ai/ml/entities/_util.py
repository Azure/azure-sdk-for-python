# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from collections import OrderedDict
from typing import Optional, Any, Dict
from marshmallow.exceptions import ValidationError
import json
import hashlib
from azure.ai.ml.constants import (
    CommonYamlFields,
    REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT,
    YAMLRefDocLinks,
    YAMLRefDocSchemaNames,
    EndpointYamlFields,
)
from azure.ai.ml._schema.assets.data import DataSchema
from azure.ai.ml._schema.assets.dataset import DatasetSchema
from azure.ai.ml._schema.assets.environment import EnvironmentSchema
from azure.ai.ml._schema.assets.model import ModelSchema
from azure.ai.ml._schema.component.command_component import CommandComponentSchema
from azure.ai.ml._schema.component.parallel_component import ParallelComponentSchema
from azure.ai.ml._schema.compute.aml_compute import AmlComputeSchema
from azure.ai.ml._schema.compute.compute_instance import ComputeInstanceSchema
from azure.ai.ml._schema.compute.virtual_machine_compute import VirtualMachineComputeSchema
from azure.ai.ml._schema._datastore import (
    AzureDataLakeGen1Schema,
    AzureBlobSchema,
    AzureFileSchema,
    AzureDataLakeGen2Schema,
)
from azure.ai.ml._schema._endpoint.batch.batch_endpoint import BatchEndpointSchema
from azure.ai.ml._schema._endpoint.online.online_endpoint import (
    KubernetesOnlineEndpointSchema,
    ManagedOnlineEndpointSchema,
    OnlineEndpointSchema,
)
from azure.ai.ml._schema._deployment.batch.batch_deployment import BatchDeploymentSchema
from azure.ai.ml._schema._deployment.online.online_deployment import (
    KubernetesOnlineDeploymentSchema,
    ManagedOnlineDeploymentSchema,
    OnlineDeploymentSchema,
)
from azure.ai.ml._schema.pipeline.pipeline_job import PipelineJobSchema
from azure.ai.ml._schema._sweep import SweepJobSchema
from azure.ai.ml._schema.job import CommandJobSchema
from azure.ai.ml._schema.job import ParallelJobSchema
from azure.ai.ml._schema.workspace import WorkspaceSchema
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


# Maps schema class name to formatted error message pointing to Microsoft docs reference page for a schema's YAML
REF_DOC_ERROR_MESSAGE_MAP = {
    DataSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(YAMLRefDocSchemaNames.DATA, YAMLRefDocLinks.DATA),
    DatasetSchema: REF_DOC_YAML_SCHEMA_ERROR_MSG_FORMAT.format(YAMLRefDocSchemaNames.DATASET, YAMLRefDocLinks.DATASET),
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
    additional_message += """\nThe easiest way to author a specification file is using IntelliSense and auto-completion Azure ML VS code extension provides: https://code.visualstudio.com/docs/datascience/azure-machine-learning
To set up: https://docs.microsoft.com/azure/machine-learning/how-to-setup-vs-code"""
    return f"Validation for {schema.__name__} failed:\n\n {pretty_error} \n\n {additional_message}"


def get_md5_string(text):
    try:
        return hashlib.md5(text.encode("utf8")).hexdigest()
    except Exception as ex:
        raise ex


def validate_attribute_type(attrs_to_check: dict, attr_type_map: dict):
    """Validate if attributes of object are set with valid types, raise error if don't.

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
            )


class SnakeToPascalDescriptor(object):

    """A data descriptor that transforms value from snake_case to CamelCase in setter,
    CamelCase to snake_case in getter. When the optional private_name is provided, the descriptor
    will set the private_name in the object's __dict__.
    """

    def __init__(self, private_name=None, *, transformer=camel_to_snake, reverse_transformer=snake_to_pascal):
        self.private_name = private_name
        self.transformer = transformer
        self.reverse_transformer = reverse_transformer

    def __set_name__(self, owner, name):
        self.public_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        key = self.private_name or self.public_name
        value = obj.__dict__.get(key, None)
        return self.transformer(value) if value else None

    def __set__(self, obj, val):

        key = self.private_name or self.public_name
        value = self.reverse_transformer(val)
        obj.__dict__[key] = value

    def __delete__(self, obj):
        key = self.private_name or self.public_name
        obj.__dict__.pop(key, None)


class LiteralToListDescriptor(object):

    """A data descriptor that transforms singular literal values to lists in the setter. The getter always returns a list
    When the optional private_name is provided, the descriptor will set the private_name in the object's __dict__.
    """

    def __init__(self, private_name=None):
        self.private_name = private_name

    def __set_name__(self, owner, name):
        self.public_name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        key = self.private_name or self.public_name
        return obj.__dict__.get(key, None)

    def __set__(self, obj, val):

        key = self.private_name or self.public_name
        if not isinstance(val, list) and val is not None:
            val = [val]
        obj.__dict__[key] = val

    def __delete__(self, obj):
        key = self.private_name or self.public_name
        obj.__dict__.pop(key, None)


def convert_ordered_dict_to_dict(target_dict):
    """Convert ordered dict to dict. This is a workaround for rest request must be in dict instead of ordered dict."""
    if isinstance(target_dict, dict):
        for key, dict_candidate in target_dict.items():
            target_dict[key] = convert_ordered_dict_to_dict(dict_candidate)
    if isinstance(target_dict, OrderedDict):
        return dict(**target_dict)
    else:
        return target_dict


def get_rest_dict(target_obj, clear_empty_value=False):
    """Convert object to dict and convert OrderedDict to dict."""
    if target_obj is None:
        return None
    result = convert_ordered_dict_to_dict(copy.deepcopy(target_obj.__dict__))
    to_del = ["additional_properties"]
    if clear_empty_value:
        to_del.extend(filter(lambda x: result.get(x) is None, result.keys()))
    for key in to_del:
        if key in result:
            del result[key]
    return result
