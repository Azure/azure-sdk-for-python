# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, UnionField, NestedField

module_logger = logging.getLogger(__name__)


class PathBaseSchema(PathAwareSchema):
    input_path_type = StringTransformedEnum(
        allowed_values=[
            "path_id",
            "url",
            "path_version",
        ],
        casing_transform=camel_to_snake,
    )


class PackageInputPathIdSchema(PathBaseSchema):
    resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.model_package import PackageInputPathId

        return PackageInputPathId(**data)


class PackageInputPathUrlSchema(PathBaseSchema):
    url = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.model_package import PackageInputPathUrl

        return PackageInputPathUrl(**data)


class PackageInputPathSchema(PathBaseSchema):
    resource_name = fields.Str()
    resource_version = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.model_package import PackageInputPathVersion

        return PackageInputPathVersion(**data)


class ModelPackageInputSchema(PathAwareSchema):
    type = StringTransformedEnum(allowed_values=["uri_file", "uri_folder"], casing_transform=camel_to_snake)
    mode = StringTransformedEnum(
        allowed_values=[
            "readonly_mount",
            "download",
        ],
        casing_transform=camel_to_snake,
    )
    path = UnionField(
        [
            NestedField(PackageInputPathIdSchema),
            NestedField(PackageInputPathUrlSchema),
            NestedField(PackageInputPathSchema),
        ]
    )
    mount_path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.model_package import ModelPackageInput

        return ModelPackageInput(**data)
