# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-member

import logging

from marshmallow import INCLUDE, ValidationError, post_load, pre_dump, pre_load

from azure.ai.ml._schema.core.fields import (
    ArmVersionedStr,
    ComputeField,
    NestedField,
    RegistryStr,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.job import BaseJobSchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.pipeline.component_job import _resolve_inputs_outputs
from azure.ai.ml._schema.pipeline.pipeline_component import (
    PipelineComponentFileRefField,
    PipelineJobsField,
    _post_load_pipeline_jobs,
)
from azure.ai.ml._schema.pipeline.settings import PipelineJobSettingsSchema
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import AzureMLResourceType

module_logger = logging.getLogger(__name__)


class PipelineJobSchema(BaseJobSchema):
    type = StringTransformedEnum(allowed_values=[JobType.PIPELINE])
    compute = ComputeField()
    settings = NestedField(PipelineJobSettingsSchema, unknown=INCLUDE)
    # Support databinding in inputs as we support macro like ${{name}}
    inputs = InputsField(support_databinding=True)
    outputs = OutputsField()
    jobs = PipelineJobsField()
    component = UnionField(
        [
            # for registry type assets
            RegistryStr(azureml_type=AzureMLResourceType.COMPONENT),
            # existing component
            ArmVersionedStr(azureml_type=AzureMLResourceType.COMPONENT, allow_default_version=True),
            # component file reference
            PipelineComponentFileRefField(),
        ],
    )

    @pre_dump()
    def backup_jobs_and_remove_component(self, job, **kwargs):
        # pylint: disable=protected-access
        job_copy = _resolve_inputs_outputs(job)
        if not isinstance(job_copy.component, str):
            # If component is pipeline component object,
            # copy jobs to job and remove component.
            if not job_copy._jobs:
                job_copy._jobs = job_copy.component.jobs
            job_copy.component = None
        return job_copy

    @pre_load()
    def check_exclusive_fields(self, data: dict, **kwargs) -> dict:
        error_msg = "'jobs' and 'component' are mutually exclusive fields in pipeline job."
        # When loading from yaml, data["component"] must be a local path (str)
        # Otherwise, data["component"] can be a PipelineComponent so data["jobs"] must exist
        if isinstance(data.get("component"), str) and data.get("jobs"):
            raise ValidationError(error_msg)
        return data

    @post_load
    def make(self, data: dict, **kwargs) -> dict:
        return _post_load_pipeline_jobs(self.context, data)
