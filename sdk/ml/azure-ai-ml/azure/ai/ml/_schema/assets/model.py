# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType, AssetTypes

from azure.ai.ml._schema import NestedField, PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from marshmallow import fields, post_load

from ..core.fields import ArmStr, ArmVersionedStr, StringTransformedEnum, VersionField

module_logger = logging.getLogger(__name__)


class ModelSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=[AssetTypes.CUSTOM_MODEL, AssetTypes.MLFLOW_MODEL, AssetTypes.TRITON_MODEL],
        metadata={"description": "The storage format for this entity. Used for NCD."},
    )
    path = fields.Str()
    version = VersionField()
    description = fields.Str()
    properties = fields.Dict()
    tags = fields.Dict()
    utc_time_created = fields.DateTime()
    flavors = fields.Dict()
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    job_name = fields.Str(dump_only=True)
    latest_version = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Model

        return Model(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class AnonymousModelSchema(ModelSchema):
    name = fields.Str()
    version = VersionField()
