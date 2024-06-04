# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import ArmStr
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, AzureMLResourceType

from .artifact import ArtifactSchema
from .asset import AnonymousAssetSchema

module_logger = logging.getLogger(__name__)


class CodeAssetSchema(ArtifactSchema):
    id = ArmStr(azureml_type=AzureMLResourceType.CODE, dump_only=True)
    path = fields.Str(
        metadata={
            "description": "A local path or a Blob URI pointing to a file or directory where code asset is located."
        }
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Code

        return Code(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class AnonymousCodeAssetSchema(CodeAssetSchema, AnonymousAssetSchema):
    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Code

        return Code(is_anonymous=True, base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)

    @pre_dump
    def validate(self, data, **kwargs):
        # AnonymousCodeAssetSchema does not support None or arm string(fall back to ArmVersionedStr)
        if data is None or not hasattr(data, "get"):
            raise ValidationError("Code cannot be None")
        return data
