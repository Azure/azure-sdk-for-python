# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from marshmallow import fields

from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema, EnvironmentSchema
from azure.ai.ml._schema.assets.model import AnonymousModelSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, NestedField, PathAwareSchema, RegistryStr, UnionField
from azure.ai.ml.constants._common import AzureMLResourceType

from .code_configuration_schema import CodeConfigurationSchema

module_logger = logging.getLogger(__name__)


class DeploymentSchema(PathAwareSchema):
    name = fields.Str(required=True)
    endpoint_name = fields.Str(required=True)
    description = fields.Str(metadata={"description": "Description of the endpoint deployment."})
    id = fields.Str()
    tags = fields.Dict()
    properties = fields.Dict()
    model = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.MODEL),
            ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, allow_default_version=True),
            NestedField(AnonymousModelSchema),
        ],
        metadata={"description": "Reference to the model asset for the endpoint deployment."},
    )
    code_configuration = NestedField(
        CodeConfigurationSchema,
        metadata={"description": "Code configuration for the endpoint deployment."},
    )
    environment = UnionField(
        [
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
            NestedField(EnvironmentSchema),
            NestedField(AnonymousEnvironmentSchema),
        ]
    )
    environment_variables = fields.Dict(
        metadata={"description": "Environment variables configuration for the deployment."}
    )
