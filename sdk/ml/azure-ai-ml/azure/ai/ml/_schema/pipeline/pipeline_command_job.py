# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import ComputeField, EnvironmentField, NestedField, UnionField
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml._schema.job.input_output_entry import OutputSchema

module_logger = logging.getLogger(__name__)


class PipelineCommandJobSchema(CommandJobSchema):
    compute = ComputeField()
    environment = EnvironmentField()
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), fields.Str()], allow_none=True),
    )

    @post_load
    def make(self, data: Any, **kwargs: Any):
        from azure.ai.ml.entities import CommandJob

        return CommandJob(**data)
