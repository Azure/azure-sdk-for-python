# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_dump, post_load, INCLUDE
from marshmallow import Schema
from azure.ai.ml.constants import AzureMLResourceType
from azure.ai.ml._schema import (
    AnonymousCodeAssetSchema,
    ArmStr,
    ArmVersionedStr,
    NestedField,
    PatchedSchemaMeta,
    UnionField,
)
from azure.ai.ml._schema.assets.environment import AnonymousEnvironmentSchema


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
