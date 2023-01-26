# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from marshmallow.decorators import post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

class ImageSettingsSchema(metaclass=PatchedSchemaMeta):
    reference = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import ImageSettings

        return ImageSettings(**data)

class EndpointSettingsSchema(metaclass=PatchedSchemaMeta):
    target = fields.Int()
    published = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import EndpointSettings

        return EndpointSettings(**data)

class VolumeSettingsSchema(metaclass=PatchedSchemaMeta):
    source = fields.Str()
    target = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import VolumeSettings

        return VolumeSettings(**data)

class CustomApplicationsSchema(metaclass=PatchedSchemaMeta):

    name = fields.Str(required=True)
    image = NestedField(ImageSettingsSchema)
    endpoints = NestedField(EndpointSettingsSchema)
    environment_variables = fields.Dict()
    bind_mounts = NestedField(VolumeSettingsSchema)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._compute._custom_applications import CustomApplications

        return CustomApplications(**data)
