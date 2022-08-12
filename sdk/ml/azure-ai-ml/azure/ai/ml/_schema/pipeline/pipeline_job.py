# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import INCLUDE, post_load, pre_dump

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema._utils.data_binding_expression import _add_data_binding_to_field
from azure.ai.ml._schema.core.fields import ComputeField
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.pipeline.settings import PipelineJobSettingsSchema
from azure.ai.ml._schema.pipeline.component_job import _resolve_inputs_outputs
from azure.ai.ml._schema.pipeline.pipeline_component import PipelineJobsField, _post_load_pipeline_jobs
from azure.ai.ml.constants import JobType

module_logger = logging.getLogger(__name__)


class PipelineJobSchema(BaseJobSchema):
    type = StringTransformedEnum(allowed_values=[JobType.PIPELINE])
    compute = ComputeField()
    settings = NestedField(PipelineJobSettingsSchema, unknown=INCLUDE)
    inputs = InputsField()
    outputs = OutputsField()
    jobs = PipelineJobsField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Support databinding in inputs as we support macro like ${{name}}
        _add_data_binding_to_field(self.load_fields["inputs"], [], [])

    @pre_dump
    def resolve_inputs_outputs(self, job, **kwargs):
        return _resolve_inputs_outputs(job)

    @post_load
    def make(self, data: dict, **kwargs) -> dict:
        return _post_load_pipeline_jobs(self.context, data)
