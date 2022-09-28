# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import OutputsField
from azure.ai.ml._schema.job_resource_configuration import JobResourceConfigurationSchema
from azure.ai.ml.constants import JobType


class AutoMLJobSchema(BaseJobSchema):
    type = StringTransformedEnum(required=True, allowed_values=JobType.AUTOML)
    environment_id = fields.Str()
    environment_variables = fields.Dict(keys=fields.Str(), values=fields.Str())
    outputs = OutputsField()
    resources = NestedField(JobResourceConfigurationSchema())
