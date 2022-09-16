# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema import PathAwareSchema, StringTransformedEnum


class InternalEnvironmentSchema(PathAwareSchema):
    docker = fields.Dict()
    conda = fields.Dict()
    os = StringTransformedEnum(
        allowed_values=["Linux", "Windows"],
        casing_transform=lambda x: x,
        required=False,
    )
    name = fields.Str()
    version = fields.Str()
    python = fields.Dict()
