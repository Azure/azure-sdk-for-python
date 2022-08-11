# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import ValidationError, fields
from marshmallow.decorators import pre_load

from azure.ai.ml._schema.core.fields import NestedField, VersionField
from azure.ai.ml._schema.job.creation_context import CreationContextSchema

from ..core.resource import ResourceSchema

module_logger = logging.getLogger(__name__)


class AssetSchema(ResourceSchema):
    version = VersionField()
    creation_context = NestedField(CreationContextSchema, dump_only=True)
    latest_version = fields.Str(dump_only=True)


class AnonymousAssetSchema(AssetSchema):
    version = VersionField(dump_only=True)
    name = fields.Str(dump_only=True)

    @pre_load
    def warn_if_named(self, data, **kwargs):
        if isinstance(data, str):
            raise ValidationError("Anonymous assets must be defined inline")
        name = data.pop("name", None)
        data.pop("version", None)
        if name is not None:
            module_logger.warning(
                f"Warning: the provided asset name '{name}' will not be used for anonymous registration."
            )
        return data
