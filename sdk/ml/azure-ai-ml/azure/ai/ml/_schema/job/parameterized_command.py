# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import CodeField, NestedField
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml.constants._common import AzureMLResourceType

from ..assets.environment import AnonymousEnvironmentSchema
from ..core.fields import ArmVersionedStr, RegistryStr, UnionField
from .distribution import MPIDistributionSchema, PyTorchDistributionSchema, TensorFlowDistributionSchema


class ParameterizedCommandSchema(PathAwareSchema):
    command = fields.Str(
        metadata={
            # pylint: disable=line-too-long
            "description": "The command run and the parameters passed. This string may contain place holders of inputs in {}. "
        },
        required=True,
    )
    code = CodeField()
    environment = UnionField(
        [
            NestedField(AnonymousEnvironmentSchema),
            RegistryStr(azureml_type=AzureMLResourceType.ENVIRONMENT),
            ArmVersionedStr(azureml_type=AzureMLResourceType.ENVIRONMENT, allow_default_version=True),
        ],
        required=True,
    )
    environment_variables = fields.Dict(keys=fields.Str(), values=fields.Str())
    resources = NestedField(JobResourceConfigurationSchema)
    distribution = UnionField(
        [
            NestedField(PyTorchDistributionSchema),
            NestedField(TensorFlowDistributionSchema),
            NestedField(MPIDistributionSchema),
        ],
        metadata={"description": "Provides the configuration for a distributed run."},
    )
