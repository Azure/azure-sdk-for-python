# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import INCLUDE, Schema, fields, post_dump, post_load

from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants import AzureMLResourceType


class PipelineJobSettingsSchema(Schema):
    class Meta:
        unknown = INCLUDE

    default_datastore = ArmStr(azureml_type=AzureMLResourceType.DATASTORE)
    default_compute = ArmStr(azureml_type=AzureMLResourceType.COMPUTE)
    continue_on_step_failure = fields.Bool()
    force_rerun = fields.Bool()

    @post_load
    def make(self, data, **kwargs) -> "PipelineJobSettings":
        from azure.ai.ml.entities import PipelineJobSettings

        return PipelineJobSettings(**data)

    @post_dump
    def remove_none(self, data, **kwargs):
        return {key: value for key, value in data.items() if value is not None}
