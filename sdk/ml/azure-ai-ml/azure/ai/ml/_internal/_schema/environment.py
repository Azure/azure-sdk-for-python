# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import DumpableEnumField


class InternalEnvironmentSchema(PathAwareSchema):
    docker = fields.Dict()
    conda = fields.Dict()
    os = DumpableEnumField(
        allowed_values=["Linux", "Windows"],
        required=False,
    )
    name = fields.Str()
    version = fields.Str()
    python = fields.Dict()
