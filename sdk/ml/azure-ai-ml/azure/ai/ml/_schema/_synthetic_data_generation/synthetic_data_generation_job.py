# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import OutputsField
from azure.ai.ml._utils._experimental import experimental


@experimental
class SyntheticDataGenerationJobSchema(BaseJobSchema):
    type = fields.Str(load_default="data_generation")
    outputs = OutputsField()
