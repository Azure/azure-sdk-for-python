# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy

import yaml
from marshmallow import INCLUDE, ValidationError, fields, post_load, pre_load

from azure.ai.ml._schema.core.fields import (
    ComputeField,
    FileRefField,
    StringTransformedEnum,
    ArmStr,
    NestedField,
    UnionField,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField, OutputsField
from azure.ai.ml._schema.pipeline import PipelineJobSettingsSchema
from azure.ai.ml._utils.utils import load_file
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType, JobType

_SCHEDULED_JOB_UPDATES_KEY = "scheduled_job_updates"


class CreateJobFileRefField(FileRefField):
    def _serialize(self, value, attr, obj, **kwargs):
        """FileRefField does not support serialize.

        This function is overwrite because we need job can be dumped inside schedule.
        """
        return value._to_dict()

    def _deserialize(self, value, attr, data, **kwargs) -> "Job":
        # Get component info from component yaml file.
        data = super()._deserialize(value, attr, data, **kwargs)
        job_dict = yaml.safe_load(data)

        from azure.ai.ml.entities import Job

        return Job._load(
            data=job_dict,
            yaml_path=self.context[BASE_PATH_CONTEXT_KEY] / value,
            **kwargs,
        )


class BaseCreateJobSchema(metaclass=PatchedSchemaMeta):
    compute = ComputeField()
    inputs = InputsField()
    outputs = OutputsField()
    identity = UnionField(
        [
            NestedField(ManagedIdentitySchema),
            NestedField(AMLTokenIdentitySchema),
            NestedField(UserIdentitySchema),
        ]
    )
    description = fields.Str(attribute="description")
    tags = fields.Dict(keys=fields.Str, attribute="tags")
    experiment_name = fields.Str()
    properties = fields.Dict(keys=fields.Str(), values=fields.Str(allow_none=True))
    job = UnionField(
        [
            ArmStr(azureml_type=AzureMLResourceType.JOB),
            CreateJobFileRefField,
        ],
        required=True,
    )

    def _get_job_instance_for_remote_job(self, id, data, **kwargs):
        """Get a job instance to store updates for remote job."""
        from azure.ai.ml.entities import Job

        data = {} if data is None else data
        if "type" not in data:
            raise ValidationError("'type' must be specified when scheduling a remote job with updates.")
        # Create a job instance if job is arm id
        job_instance = Job._load(
            data=data,
            **kwargs,
        )
        # Set back the id and base path to created job
        job_instance._id = id
        job_instance._base_path = self.context[BASE_PATH_CONTEXT_KEY]
        return job_instance

    @pre_load
    def pre_load(self, data, **kwargs):
        if isinstance(data, dict):
            # Put the raw replicas into context.
            # dict type indicates there are updates to the scheduled job.
            copied_data = copy.deepcopy(data)
            copied_data.pop("job", None)
            self.context[_SCHEDULED_JOB_UPDATES_KEY] = copied_data
        return data

    @post_load
    def make(self, data: dict, **kwargs) -> "Job":
        from azure.ai.ml.entities import Job

        # Get the loaded job
        job = data.pop("job")
        # Get the raw dict data before load
        raw_data = self.context.get(_SCHEDULED_JOB_UPDATES_KEY, {})
        if isinstance(job, Job):
            from azure.ai.ml.entities import Job

            if job._source_path is None:
                raise ValidationError("Could not load job for schedule without '_source_path' set.")
            # Load local job again with updated values
            job_dict = yaml.safe_load(load_file(job._source_path))
            return Job._load(
                data={**job_dict, **raw_data},
                yaml_path=job._source_path,
                **kwargs,
            )
        # Create a job instance for remote job
        return self._get_job_instance_for_remote_job(job, raw_data, **kwargs)


class PipelineCreateJobSchema(BaseCreateJobSchema):
    type = StringTransformedEnum(allowed_values=[JobType.PIPELINE])
    settings = NestedField(PipelineJobSettingsSchema, unknown=INCLUDE)
