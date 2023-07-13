# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument
from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.constants._compute import CustomApplicationDefaults


class ImageSettingsSchema(metaclass=PatchedSchemaMeta):
    reference = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import ImageSettings

        return ImageSettings(**data)


class EndpointsSettingsSchema(metaclass=PatchedSchemaMeta):
    target = fields.Int()
    published = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import EndpointsSettings

        return EndpointsSettings(**data)


class VolumeSettingsSchema(metaclass=PatchedSchemaMeta):
    source = fields.Str()
    target = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import VolumeSettings

        return VolumeSettings(**data)


class CustomApplicationsSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True)
    type = StringTransformedEnum(allowed_values=[CustomApplicationDefaults.DOCKER])
    image = NestedField(ImageSettingsSchema)
    endpoints = fields.List(NestedField(EndpointsSettingsSchema))
    environment_variables = fields.Dict()
    bind_mounts = fields.List(NestedField(VolumeSettingsSchema))

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import (
            CustomApplications,
        )

        return CustomApplications(**data)
