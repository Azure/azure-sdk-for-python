# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import INCLUDE, Schema, fields, post_dump, post_load

from azure.ai.ml._schema.core.fields import ArmStr, StringTransformedEnum, UnionField
from azure.ai.ml._schema.pipeline.pipeline_component import NodeNameStr
from azure.ai.ml._utils.utils import is_private_preview_enabled
from azure.ai.ml.constants._common import AzureMLResourceType, SERVERLESS_COMPUTE


class PipelineJobSettingsSchema(Schema):
    class Meta:
        unknown = INCLUDE

    default_datastore = ArmStr(azureml_type=AzureMLResourceType.DATASTORE)
    default_compute = UnionField(
        [
            StringTransformedEnum(allowed_values=[SERVERLESS_COMPUTE]),
            ArmStr(azureml_type=AzureMLResourceType.COMPUTE),
        ]
    )
    continue_on_step_failure = fields.Bool()
    force_rerun = fields.Bool()

    # move init/finalize under private preview flag to hide them in spec
    if is_private_preview_enabled():
        on_init = NodeNameStr()
        on_finalize = NodeNameStr()

    @post_load
    def make(self, data, **kwargs) -> "PipelineJobSettings":
        from azure.ai.ml.entities import PipelineJobSettings

        return PipelineJobSettings(**data)

    @post_dump
    def remove_none(self, data, **kwargs):
        return {key: value for key, value in data.items() if value is not None}
