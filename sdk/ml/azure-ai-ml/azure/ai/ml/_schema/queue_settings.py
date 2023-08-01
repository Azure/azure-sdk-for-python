# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import post_load
from azure.ai.ml.constants._job.job import JobPriorityValues, JobTierNames
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class QueueSettingsSchema(metaclass=PatchedSchemaMeta):
    job_tier = StringTransformedEnum(
        allowed_values=JobTierNames.ALLOWED_NAMES,
    )
    priority = StringTransformedEnum(
        allowed_values=JobPriorityValues.ALLOWED_VALUES,
    )

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        from azure.ai.ml.entities import QueueSettings

        return QueueSettings(**data)
