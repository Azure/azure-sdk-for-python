# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from ..._schema import PathAwareSchema
from ..._schema.core.fields import DumpableEnumField, VersionField


class InternalEnvironmentSchema(PathAwareSchema):
    docker = fields.Dict()
    conda = fields.Dict()
    os = DumpableEnumField(
        # add enum instead of use string transformer here to avoid changing the value
        allowed_values=["Linux", "Windows", "linux", "windows"],
        required=False,
    )
    name = fields.Str()
    version = VersionField()
    python = fields.Dict()
