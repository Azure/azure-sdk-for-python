# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema import NestedField, PathAwareSchema
from azure.ai.ml.constants import AzureMLResourceType
from marshmallow import fields

from azure.ai.ml._schema.resource_configuration import ResourceConfigurationSchema

from ..assets.code_asset import AnonymousCodeAssetSchema
from ..assets.environment import AnonymousEnvironmentSchema
from ..core.fields import ArmVersionedStr, UnionField, RegistryStr, LocalPathField, SerializeValidatedUrl, GitStr
from .distribution import MPIDistributionSchema, PyTorchDistributionSchema, TensorFlowDistributionSchema


class ParameterizedCommandSchema(PathAwareSchema):
    command = fields.Str(
        metadata={
            "description": "The command run and the parameters passed. This string may contain place holders of inputs in {}. "
        },
        required=True,
    )
    code = UnionField(
        [LocalPathField, SerializeValidatedUrl(), GitStr(), ArmVersionedStr(azureml_type=AzureMLResourceType.CODE)],
        metadata={"description": "A local path or http:, https:, azureml: url pointing to a remote location."},
    )
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
        required=True,
    )
    environment_variables = fields.Dict(keys=fields.Str(), values=fields.Str())
    resources = NestedField(ResourceConfigurationSchema)
    distribution = UnionField(
        [
            NestedField(PyTorchDistributionSchema),
            NestedField(TensorFlowDistributionSchema),
            NestedField(MPIDistributionSchema),
        ],
        metadata={"description": "Provides the configuration for a distributed run."},
    )
