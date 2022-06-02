# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import post_dump, post_load, INCLUDE

from azure.ai.ml._schema.resource_configuration import ResourceConfigurationSchema


class ComponentResourceSchema(ResourceConfigurationSchema):
    class Meta:
        unknown = INCLUDE

    @post_load
    def make(self, data, **kwargs):
        return data

    @post_dump(pass_original=True)
    def dump_override(self, data, original, **kwargs):
        return original
