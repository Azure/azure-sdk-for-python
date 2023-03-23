# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum


module_logger = logging.getLogger(__name__)


class ModelConfigurationSchema(PathAwareSchema):
    mode = StringTransformedEnum(
        allowed_values=[
            "readonly_mount",
            "download",
        ]
    )
    mount_path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ModelConfiguration

        return ModelConfiguration(**data)
