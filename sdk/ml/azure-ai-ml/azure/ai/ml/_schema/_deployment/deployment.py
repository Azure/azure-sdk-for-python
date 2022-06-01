# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._schema import NestedField, PathAwareSchema
from azure.ai.ml._schema.assets.environment import EnvironmentSchema, AnonymousEnvironmentSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr, UnionField
from azure.ai.ml._schema.assets.model import AnonymousModelSchema
from azure.ai.ml.constants import AzureMLResourceType
from marshmallow import fields

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
            ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, allow_default_version=True),
            NestedField(AnonymousModelSchema),
        ],
        metadata={"description": "Reference to the model asset for the endpoint deployment."},
    )
    code_configuration = NestedField(
        CodeConfigurationSchema, metadata={"description": "Code configuration for the endpoint deployment."}
    )
    environment = UnionField(
        [
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
            NestedField(EnvironmentSchema),
            NestedField(AnonymousEnvironmentSchema),
        ]
    )
    environment_variables = fields.Dict(
        metadata={"description": "Environment variables configuration for the deployment."}
    )
