# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum

module_logger = logging.getLogger(__name__)


class ModelPackageInputSchema(PathAwareSchema):
    type = StringTransformedEnum(allowed_values=["uri_file", "uri_folder"])
    mode = StringTransformedEnum(
        allowed_values=[
            "readonly_mount",
            "download",
        ]
    )
    path = fields.Str()
    mount_path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts.model_package import ModelPackageInput

        return ModelPackageInput(**data)
