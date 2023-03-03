# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ai.ml.constants._job.job import JobPriorityValues, JobTierNames
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from ..core.schema import PathAwareSchema

from .resource_configuration import ResourceConfigurationSchema


class QueueSettingsSchema(PathAwareSchema):
    job_tier = StringTransformedEnum(
        allowed_values=JobTierNames.EntityNames,
        pass_original=True,
    )
    priority = StringTransformedEnum(
        allowed_values=JobPriorityValues.EntityValues,
        pass_original=True,
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import QueueSettings

        return QueueSettings(**data)
