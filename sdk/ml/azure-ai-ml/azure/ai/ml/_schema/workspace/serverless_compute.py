# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import ValidationError, fields, validates_schema

from azure.ai.ml._schema._utils.utils import validate_arm_str
from azure.ai.ml._schema.core.schema import PathAwareSchema


class ServerlessComputeSettingsSchema(PathAwareSchema):
    custom_subnet = fields.Str(validate=validate_arm_str)
    no_public_ip = fields.Bool(load_default=False)

    @validates_schema
    def validate_no_public_ip_flag(self, data, **_kwargs):
        if data["no_public_ip"] and len(data["custom_subnet"]) == 0:
            raise ValidationError("custom_subnet must be specified if serverless_compute_no_public_ip is set to true")
