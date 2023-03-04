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
from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelConfiguration

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
        return ModelConfiguration(**data)
