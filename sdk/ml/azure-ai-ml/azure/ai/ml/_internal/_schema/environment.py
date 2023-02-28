# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, pre_load

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import DumpableEnumField


class InternalEnvironmentSchema(PathAwareSchema):
    docker = fields.Dict()
    conda = fields.Dict()
    os = DumpableEnumField(
        # add enum instead of use string transformer here to avoid changing the value
        allowed_values=["Linux", "Windows", "linux", "windows"],
        required=False,
    )
    name = fields.Str()
    version = fields.Str()
    python = fields.Dict()

    @pre_load
    def convert_version_to_str(self, data, **kwargs):
        if "version" in data and data["version"] is not None:
            data["version"] = str(data["version"])
        return data
