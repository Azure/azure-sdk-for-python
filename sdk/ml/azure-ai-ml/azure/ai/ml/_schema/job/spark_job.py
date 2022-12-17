# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.spark_resource_configuration import SparkResourceConfigurationSchema
from azure.ai.ml.constants import JobType

from ..core.fields import ComputeField, StringTransformedEnum, UnionField
from .base_job import BaseJobSchema
from .parameterized_spark import ParameterizedSparkSchema


class SparkJobSchema(ParameterizedSparkSchema, BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.SPARK)
    compute = ComputeField()
    inputs = InputsField()
    outputs = OutputsField()
    resources = NestedField(SparkResourceConfigurationSchema)
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )
