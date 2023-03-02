# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.job import CreationContextSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AssetTypes, AzureMLResourceType

from azure.ai.ml._schema.core.fields import ArmVersionedStr, StringTransformedEnum, VersionField, NestedField

module_logger = logging.getLogger(__name__)


class ModelPackageInputSchema(PathAwareSchema):
    input_type = StringTransformedEnum(allowed_values=["UriFile", "UriFolder"])
    mode = StringTransformedEnum(
        allowed_values=[
            "readonly_mount",
            "download",
        ]
    )
    path = fields.Str()
    mount_path = fields.Str()
