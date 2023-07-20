# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load, pre_dump

from azure.ai.ml._schema.component.input_output import InputPortSchema, OutputPortSchema, ParameterSchema
from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField, UnionField
from azure.ai.ml._schema.core.intellectual_property import IntellectualPropertySchema
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes, AzureMLResourceType

from ..core.fields import ArmVersionedStr, StringTransformedEnum, VersionField

module_logger = logging.getLogger(__name__)


class CustomAssetSchema(PathAwareSchema):
    name = fields.Str(required=True)
    id = ArmVersionedStr(azureml_type=AzureMLResourceType.CUSTOM_ASSET, dump_only=True)
    type = StringTransformedEnum(
        allowed_values=[
            AssetTypes.CUSTOM_ASSET,
            "prompt",
            "custom",
            "command",
            # TODO: add all the types defined in AssetTypes for CustomAsset
        ],
        metadata={"description": ""},
    )
    path = fields.Str()
    version = VersionField()
    description = fields.Str()
    properties = fields.Dict()
    tags = fields.Dict()
    stage = fields.Str()
    template = fields.Dict(keys=fields.Str(), values=fields.Str())
    inputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField(
            [
                NestedField(ParameterSchema),
                NestedField(InputPortSchema),
            ]
        ),
    )
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    job_name = fields.Str(dump_only=True)
    latest_version = fields.Str(dump_only=True)
    datastore = fields.Str(metadata={"description": "Name of the datastore to upload to."}, required=False)
    intellectual_property = ExperimentalField(NestedField(IntellectualPropertySchema, required=False), dump_only=True)

    @pre_dump
    def validate(self, data, **kwargs):
        if data._intellectual_property:  # pylint: disable=protected-access
            ipp_field = data._intellectual_property  # pylint: disable=protected-access
            if ipp_field:
                setattr(data, "intellectual_property", ipp_field)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts.custom_asset import CustomAsset

        return CustomAsset(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class AnonymousCustomAssetSchema(CustomAssetSchema):
    name = fields.Str()
    version = VersionField()
