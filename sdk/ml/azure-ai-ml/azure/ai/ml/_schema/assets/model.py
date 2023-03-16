# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField
from azure.ai.ml._schema.core.intellectual_property_schema import IntellectualPropertySchema
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes, AzureMLResourceType

from ..core.fields import ArmVersionedStr, StringTransformedEnum, VersionField

module_logger = logging.getLogger(__name__)


class ModelSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = ArmVersionedStr(azureml_type=AzureMLResourceType.MODEL, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.CUSTOM_MODEL,
            AssetTypes.MLFLOW_MODEL,
            AssetTypes.TRITON_MODEL,
        ],
        metadata={"description": "The storage format for this entity. Used for NCD."},
    )
    path = fields.Str()
    version = VersionField()
    description = fields.Str()
    properties = fields.Dict()
    tags = fields.Dict()
    utc_time_created = fields.DateTime(format="iso", dump_only=True)
    flavors = fields.Dict()
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    job_name = fields.Str(dump_only=True)
    latest_version = fields.Str(dump_only=True)
    datastore = fields.Str(metadata={"description": "Name of the datastore to upload to."}, required=False)
    intellectual_property = ExperimentalField(NestedField(IntellectualPropertySchema, required=False), dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Model

        return Model(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class AnonymousModelSchema(ModelSchema):
    name = fields.Str()
    version = VersionField()
